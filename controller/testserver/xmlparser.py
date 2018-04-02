__author__ = 'carl'

import xml.etree.ElementTree as ET
import datetime
import time
import os

class xmlparser:
    #xmlFile="/tmp/RIDEhabI1X.d/output.xml"
    __xmlFile='framework/testserver/robotlog/output.xml'
    #__xmlFile='robotlog/output.xml'

    __base="/tmp/"
    __root=None
    __nd_stat=None
    __nd_suite=None
    __nd_nd_total=None
    data=''
    layout=0
    __splitter = '^'

    def __init__(self):
        '''
        Initial the root of the XML tree.
        '''
        self._nRet = True
        try:
            # for test only purpose, comment following one line
            #self.__xmlFile=self.__getLogFile()
            #self.__xmlFile= FILE_FOLDER + "output.xml"
            if os.path.exists(self.__xmlFile):
                tree = ET.parse(self.__xmlFile)
                self.__root=tree.getroot()

        except Exception,e:
            self._nRet = False
            print str(e)

    def isTrue(self):
        return self._nRet

    def __getLogFolderList(self):
        '''
        Find the log folder
        '''
        logFolderList=[]
        fList=os.listdir(self.__base)
        for f in fList:
            if f.startswith("RIDE"):
                #print f
                if os.path.isdir(self.__base+f):
                    #print f+" is a directory"
                    logFolderList.append(self.__base+f)
        return logFolderList

    def __getLogFile(self):
        '''
        Find the log file
        '''
        logFile = ""
        logFolderList=self.__getLogFolderList()
        if len(logFolderList)==1:
            logFile= logFolderList[0]
        else:
            tmpCtime=0
            for l in logFolderList:
                Ctime=os.stat(l+"/output.xml").st_ctime
                if Ctime>tmpCtime:
                    logFile=l
                    tmpCtime=Ctime
        print logFile+"/output.xml"
        return logFile+"/output.xml"

    def __getStatNode(self):
        '''
        Locate the Stat node
        '''
        for node in self.__root:
            if node.tag=="statistics":
                self.__nd_stat=node
        #return self.nd_stat

    def __getSuiteNode(self):
        '''
        Locate the Suite node
        '''
        for node in self.__root:
            if node.tag=="suite":
                self.__nd_suite=node
        #return self.nd_suite

    def __getTotalNode(self):
        self.__getStatNode()
        for node in self.__nd_stat:
            if node.tag=="total":
                self.__nd_nd_total=node
        #return nd_nd_total

    def __getTotalResult(self):
        self.__getTotalNode()
        for node in self.__nd_nd_total:
            #print node.tag
            #print node.text
            if node.text=="All Tests":
                return node.attrib

    def __getStatusResults(self):
        self.__getSuiteNode()
        for node in self.__nd_suite:
            #print node.tag
            if node.tag=="status":
                return node.attrib

    def __timeStrip(self,time):
        return time[0:time.index('.')]

    def __timeToBigSecond(self,time):
        return time.replace(" ","").replace(":","").replace(".","")

    def __secondToTime(self,second):
        pass

    def __getGenTime(self):
        return self.__root.attrib["generated"]

    def getStartTime(self):
        return self.__getStatusResults()["starttime"]

    def getEndTime(self):
        return self.__getStatusResults()["endtime"]

    def getRunTime(self):
        #return self.__timeToBigSecond(self.__timeStrip(self.__getGenTime()))
        return self.__timeToBigSecond(self.__getGenTime())


    def getDuration(self):
        start=self.__timeStrip(self.getStartTime())
        end=self.__timeStrip(self.getEndTime())
        start=time.strptime(start,"%Y%m%d %H:%M:%S")
        end=time.strptime(end,"%Y%m%d %H:%M:%S")
        start=datetime.datetime(start[0],start[1],start[2],start[3],start[4],start[5])
        end=datetime.datetime(end[0],end[1],end[2],end[3],end[4],end[5])
        return str(end-start)

    def getPassNum(self):
        return int(self.__getTotalResult()["pass"])

    def getFailNum(self):
        return int(self.__getTotalResult()["fail"])

    def getTotalNum(self):
        return int(self.getPassNum())+int(self.getFailNum())

    def getFinalStatus(self):
        f=self.getFailNum()
        if f==0:
            return "All tests passed"
        else:
            return "%s critical test failed"%f


    def __ergodic(self, xpath, tree, index):
        '''
        Recursively fetch each case and result, and save to a list
        '''
        suites = tree.findall(xpath)
        if self.layout <index:
            self.layout = index

        for suite in suites:
            self.data = self.data + str(index) + self.__splitter + suite.attrib.get('name') + '\n'
            tcs = suite.findall('./test')
            tag = suite.findall('arguments')
            #print tcs
            #print tag
            for tc in tcs:
                #print tc
                status = tc.find('status').attrib
                tags = tc.find("tags")
                #print status
                #print tags
                priority = ""
                for tag in tags:
                    if tag.text[0] == 'p' or tag.text[0] == 'P':
                        #print tag.text
                        priority = tag.text
                self.data = self.data + str(index + 1) + self.__splitter + \
                       tc.attrib.get('name') + self.__splitter + \
                       priority + self.__splitter + \
                       status.get('status') + self.__splitter + \
                       self.__formatDateTimeStr(status.get('starttime')) + self.__splitter + \
                       self.__formatDateTimeStr(status.get('endtime')) + self.__splitter + \
                       self.__getDuration(self.__formatDateTimeStr(status.get('starttime')),
                                          self.__formatDateTimeStr(status.get('endtime'))) + "\n"
            self.__ergodic('./suite', suite, (index+1))

    def __formatDateTimeStr(self, dt):
        dt = dt[0:dt.index('.')]
        return dt[4:6] + '/' + dt[6:8] + '/' + dt[0:4] + dt[8:]

    def __getDuration(self, start, end, flag=''):
        rt = ''
        if start.find('-') > -1:
            st = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
            dt = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        else:
            st = datetime.datetime.strptime(start, '%m/%d/%Y %H:%M:%S')
            dt = datetime.datetime.strptime(end, '%m/%d/%Y %H:%M:%S')
        total = (dt-st).seconds
        if total >= 3600:
            rt = str(total / 3600) + 'h' + flag
            total = total % 3600
        if total >= 60:
            rt = rt + str(total / 60) + "'" + flag
            total = total % 60
        rt = rt + str(total) + '"'
        return rt

    def loadXMLDetails(self):
        if os.path.exists(self.__xmlFile):
            try:
                tree = ET.parse(self.__xmlFile)
               # self.__ergodic('suite/suite', tree, 0)
                self.__ergodic('suite', tree, 0)
            except Exception,e:
                print str(e)
        return self.data

#d= xmlparser()
'''
#print d.getPassNum()
#print d.getFailNum()
#print d.getTotalNum()
#print d.getFinalStatus()
#print d.getRunTime()
#print d.getStartTime()
#print d.getEndTime()
#print d.getDuration()
'''
#print(d.loadXMLDetails())
