#! /usr/bin/python
# -*- coding: utf-8 -*-

import xmlparser
from library import myglobal, configuration, db
import logging
import logging.config


class savelog:
    def __init__(self):
        self.__config = configuration.configuration()
        self.__config.fileConfig(myglobal.CONFIGURATONINI)

        logging.config.fileConfig(myglobal.LOGGINGINI)
        self._logger = logging.getLogger('savelog')

        self.__total_data = ''
        self.__mapping_data = ''
        self.__result_data = ''
        self.__component = ''
        self.__category = ''
        self.__splitter = "^"

        self.__db = None
        self._xml = None
        self._nRet = True
        self._initData()

    def _initData(self):
        self._xml = xmlparser.xmlparser()
        self._nRet = self._xml.isTrue()
        self.__component = self.__config.getValue('TestSession', 'component')
        self.__category = self.__config.getValue('TestSession', 'category')

        host = self.__config.getValue("Database", "host")
        user = self.__config.getValue("Database", "username")
        pwd = self.__config.getValue("Database", "password")
        schema = self.__config.getValue("Database", "db")
        port = self.__config.getValue("Database", "port")
        self.__db = database.database()
        if self.__db.initDB(host, user, pwd, schema, port):
            self._logger.debug("DB Connection successfully")
        else:
            self._logger.error("DB Connection error: %s %s %s %s %s" % (host, user, pwd, schema, port))
            self.__db = None

    def isTrue(self):
        return self._nRet

    def __genTotalResult(self):
        '''
        To generate the record object for TotalResult table.
        '''

        d = self.__db.TotalResults()
        d.component = self.__component
        d.category = self.__category
        d.build = self.__config.getValue('Build', 'version')
        d.time = self._xml.getRunTime()
        d.total_num = self._xml.getTotalNum()
        d.pass_num = self._xml.getPassNum()
        d.fail_num = self._xml.getFailNum()
        d.startTime = self._xml.getStartTime()
        d.endTime = self._xml.getEndTime()
        d.duration = self._xml.getDuration()
        d.status = self._xml.getFinalStatus()
        return d

    def __genRoundId(self):
        # time=self.x.getRunTime()
        # return self.__component+time
        return self.__config.getValue('TestSession', 'jobid')

    def __genMappingResult(self):
        '''
        To generate the record object for MappingResult table.
        '''
        r = self.__db.RoundMapping()
        r.roundId = self.__genRoundId()
        r.component = self.__component
        r.build = self.__config.getValue('Build', 'version')
        r.time = self._xml.getRunTime()
        return r

    def __genDetailedRawResults(self):
        '''
        To generate the detailed records.
        '''
        record = []
        x = xmlparser.xmlparser()
        rawData = x.loadXMLDetails().encode('utf8')
        rawData = rawData.strip().split("\n")
        for entry in rawData:
            entryList = entry.split(self.__splitter)
            if len(entryList) < 3:
                entryList += ['', '', '', '', '']
            record.append(entryList)
        return record

    def __genDetailedResults(self):
        '''
        Parse the raw detailed records to objects
        '''
        record = self.__genDetailedRawResults()
        item_list = []
        for entry in record:
            result_list_class = {'bmci': database.database.BMCIResults(), 'bmca': database.database.BMCAResults(),
                                 'bmx': database.database.BMXResults(), 'bmm': database.database.BMMResults(),
                                 'bmn': database.database.BMNResults()}
            d = result_list_class[self.__component.lower()]
            d.roundId = self.__genRoundId()
            # print entry
            d.layer = entry[0]
            # print len(entry)
            d.caseTitle = entry[1]
            d.casePriority = entry[2]
            d.result = entry[3]
            d.startTime = entry[4]
            d.endTime = entry[5]
            d.elapsed = entry[6]
            # print d.caseTitle
            item_list.append(d)
        # for i in range(len(item_list)):
        #     print item_list[i].caseTitle
        return item_list

    def insertTotalRecord(self):
        result = False
        if self.__db is None:
            return result
        try:
            self.__db.totalResultsInsert(self.__genTotalResult())
            result = True
        except:
            self._logger.error("Fail to insertTotalRecord")
        return result

    def insertMappingRecord(self):
        if self.__db is None:
            return False
        roundmap = self.__genMappingResult()
        if self.__db.roundMappingQuery(roundmap.roundId):
            self.__db.roundMappingUpdate(roundmap)

        else:
            self.__db.roundMappingInsert(roundmap)
        return True

    def insertDetailedRecords(self):
        result = False
        if self.__db is None:
            return result
        items = self.__genDetailedResults()
        insert_mapping = {'bmci': self.__db.bmciResultInsert, 'bmca': self.__db.bmcaResultsInsert,
                          'bmn': self.__db.bmnResultsInsert, 'bmx': self.__db.bmxResultsInsert,
                          'bmm': self.__db.bmmResultsInsert}
        try:
            insert_mapping[self.__component](items)
            result = True
        except:
            self._logger.error("insertResult error")
        return result

    def updateIndividualLPB(self):
        if self.__db is None:
            return False
        build = self.__db.totalResultQueryLPB(self.__component)
        # print "build is %s"%str(build)
        if build == None:
            self._logger.warning("LPB for %s is None!" % self.__component)
            self._logger.warning("Do not update individual LPB for %s." % self.__component)
        else:
            self.__db.lpbIndividualUpdate(self.__component, build)
            self._logger.info("Update individual LPB for %s with %i" % (self.__component, int(build)))
        return True

# save = savelog()
# save.insertDetailedRecords()
# save.insertMappingRecord()
# save.insertTotalRecord()
# save.updateIndividualLPB()
