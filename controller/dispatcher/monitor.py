__author__ = 'carl'

# import configuration
import logging
import logging.config
import os

from publiclib import myglobal
from publiclib import configuration
from publiclib import database


class monitor():
    '''
    Monitor is designed to be used per component
    '''
    __queue_file = "framework/dispatcher/job_queue.txt"
    __j_file = "../jenkinsjob.txt"

    def __init__(self):
        '''
        Latest build of certain component is retrieved on initialization
        '''
        self.__config = configuration.configuration()
        logging.config.fileConfig(myglobal.LOGGINGINI)
        self.__logger = logging.getLogger('monitor')
        if os.path.exists(self.__queue_file) == False:
            os.system(r'touch %s' % self.__queue_file)
        self.__config.fileConfig(myglobal.CONFIGURATONINI)
        self._db = None
        self._initData()

    def __addJobToQueue(self, job):
        '''
        Add the job to the queue
        '''
        try:
            f = open(self.__queue_file, 'a+')
            f.write("\n" + job)
            self.__logger.info("Add new buildly job to the queue: \'" + job + "\'")
        finally:
            if f:
                f.close()

    def scanJob(self):
        '''
        If there is a new build for current component, add a new job to the queue, and update the latest build number
        '''

        f_jenkins = ""
        f_job = ""
        try:
            if os.path.exists(self.__j_file) == False:
                return
            f_jenkins = open(self.__j_file, 'r')
            for line in f_jenkins.readlines():
                line = line.strip('\n')
                exist_job = False
                f_job = open(self.__queue_file, 'r')
                for line_job in f_job.readlines():
                    line_job = line_job.strip('\n')
                    if line == line_job:
                        exist_job = True
                        break
                    if "#" + line == line_job:
                        exist_job = True
                        break
                f_job.close()
                if exist_job == False:
                    self.__addJobToQueue(line)
                else:
                    self.__logger.debug("There is NO new Jenkins job.")
        finally:
            if f_jenkins:
                f_jenkins.close()
            if f_job:
                f_job.close()

    def _initData(self):
        host = self.__config.getValue("Database", "host")
        user = self.__config.getValue("Database", "username")
        pwd = self.__config.getValue("Database", "password")
        schema = self.__config.getValue("Database", "db")
        port = self.__config.getValue("Database", "port")
        self._db = database.database()
        if self._db.initDB(host, user, pwd, schema, port):
            self.__logger.info("Connect DB successfully")
        else:
            self.__logger.error("Connect DB failed")
            self._db = None

    def _get_integrated_latest(self):
        result = False
        iBuild = 0
        aBuild = 0
        mBuild = 0
        xBuild = 0
        nBuild = 0
        if self._db is not None:
            item = self._db.endToEndResultsQueryLatest()
            # print type(item)
            iBuild = int(item.bmci_build)
            aBuild = int(item.bmca_build)
            mBuild = int(item.bmm_build)
            xBuild = int(item.bmx_build)
            nBuild = int(item.bmn_build)
            self.__logger.info(
                "Query integrated latest tested builds are %i-%i-%i-%i-%i" % (iBuild, aBuild, mBuild, xBuild, nBuild))
        if (iBuild != 0 and aBuild != 0 and mBuild != 0 and xBuild != 0 and nBuild != 0):
            result = True
        return result, iBuild, aBuild, mBuild, xBuild, nBuild

    def _get_integrated_lpb(self):
        result = False
        iBuild = 0
        aBuild = 0
        mBuild = 0
        xBuild = 0
        nBuild = 0
        if self._db is not None:
            iBuild, aBuild, mBuild, xBuild, nBuild = self._db.lpbIntegratedQueryAll()
        if (iBuild != 0 and aBuild != 0 and mBuild != 0 and xBuild != 0 and nBuild != 0):
            result = True
        return result, iBuild, aBuild, mBuild, xBuild, nBuild

    def _get_individual_lpb(self):
        result = False
        iBuild = 0
        aBuild = 0
        mBuild = 0
        xBuild = 0
        nBuild = 0
        if self._db is not None:
            iBuild, aBuild, mBuild, xBuild, nBuild = self._db.lpbIndividualQueryAll()
        if (iBuild != 0 and aBuild != 0 and mBuild != 0 and xBuild != 0 and nBuild != 0):
            result = True
        return result, iBuild, aBuild, mBuild, xBuild, nBuild

    def _need_to_run(self, individual_lpb, integrated_latest, integrated_lpb):
        result = False
        # build=0
        individual_lpb = int(individual_lpb)
        integrated_latest = int(integrated_latest)
        integrated_lpb = int(integrated_lpb)
        # print str(individual_lpb)+","+str(integrated_latest)+","+str(integrated_lpb)
        if individual_lpb > integrated_latest >= integrated_lpb:    #in real, integrated_latest will always be greater then integrated lpb
            result = True
        return result

    def scan_end2end(self):
        # ind_rt, ind_ib, ind_ab, ind_mb, ind_xb, ind_mb = self._get_individual_lpb()
        # end_lt_rt, end_lt_ib, end_lt_ab, end_lt_mb, end_lt_xb, end_lt_mb = self._get_integrated_latest()
        # end_ps_rt, end_ps_ib, end_ps_ab, end_ps_mb, end_ps_xb, end_ps_mb = self._get_integrated_lpb()
        individual_lpb_list = self._get_individual_lpb()
        integrated_latest_list = self._get_integrated_latest()
        integrated_lpb_list = self._get_integrated_lpb()

        if individual_lpb_list[0] == integrated_latest_list[0] == integrated_lpb_list[0] == True:
            self.__logger.info("Query individual and integrated LPB successfully.")
            for i in range(1, 6):
                integrated_lpb_dict = {"BMCI": integrated_lpb_list[1], "BMCA": integrated_lpb_list[2], "BMM": integrated_lpb_list[3], "BMX": integrated_lpb_list[4], "BMN": integrated_lpb_list[5]}
                mapper = {1: "BMCI", 2: "BMCA", 3: "BMM", 4: "BMX", 5: "BMN"}
                if self._need_to_run(individual_lpb_list[i], integrated_latest_list[i], integrated_lpb_list[i]):
                    print "%s LPB has changed, need to add an e2e job with #%i" % (mapper[i], int(individual_lpb_list[i]))
                    integrated_lpb_dict[mapper[i]] = individual_lpb_list[i]
                    print "Job builds are BMCI-%i BMCA-%i BMM-%i BMX-%i BMN-%i" % (integrated_lpb_dict['BMCI'], integrated_lpb_dict['BMCA'], integrated_lpb_dict['BMM'], integrated_lpb_dict['BMX'], integrated_lpb_dict['BMN'])
                    # Do something, like add job to a queue
                    '''
                    Need to discuss if break is needed here
                    supporting the scenario that, BMCA and BMN are both having a new build
                    If no break, 2 jobs will be added, and will be ran in sequence, first for new BMCA, second for new BMN
                       after first job finished with All Passed, we can consider that this build is good, so in second job,
                       we should use new BMCA, but not the one we added previously
                    If using break, only one job will be added in every scan, this may lead to an extreme cases
                       unless current job being done and database being updated, no job for other components lpb change
                       can be added. but during the job is running, some component may make more than 1 build and being
                       tested pass(BMM and BMX individual automation takes very short time). in this case, the intermediate
                       build(s) of some component cannot be tested in end-to-end
                    '''
                    # break
                else:
                    print "%s has nothing to do" % mapper[i]

        else:
            print "Query individual or integrated LPB failed."
            self.__logger.error("Query individual or integrated LPB failed.")


# m = monitor()
# m.scanJob()
# m.addNightlyJob()
# print "end-to-end latest " + str(m._get_integrated_latest())
# print "end-to-end LPB " + str(m._get_integrated_lpb())
# print "component LPB " + str(m._get_individual_lpb())
# m.scan_end2end()
