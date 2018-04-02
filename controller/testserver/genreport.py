#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
#import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")

#os.chdir("/Users/rwang/Documents/Work/Automation/code/bemail-automation")
#print ("workspace is %s" % os.getcwd())

from library import myglobal
from library import configuration
from library import db
import sendemail
import logging
import logging.config


class genreport:
    #Report is generated based on a template.
    __template_file = 'framework/testserver/template/report_template.html'
    __tmp_report_file = 'framework/testserver/template/tmp_Report.html'
    __report_file= ''

    __total = ''
    __component =''
    __data=''
    __db=None
    _config = None
    _logger = None

    def __init__(self):
        self._config = configuration.configuration()
        self._config.fileConfig(myglobal.CONFIGURATONINI)
        host = self._config.getValue("Database","host")
        user = self._config.getValue("Database","username")
        pwd = self._config.getValue("Database","password")
        schema = self._config.getValue("Database","db")
        port = self._config.getValue("Database","port")
        self.__db= db.database()
        self.__db.initDB(host, user, pwd, schema, port)

        logging.config.fileConfig(myglobal.LOGGINGINI)
        self._logger=logging.getLogger('genreport')
        '''
        In initialization,
         total result of current test round is retrieved
         detailed results info are retrieved
         temp report for current round is generated
        '''
        #self.data = ''
        #self.layout = 0

    def _makedata(self):
        try:
            if self.__db is None:
                self._logger.error("The DB is not initialed")
                return False
            self.__total=self.__db.totalResultQueryLatest()
            self.__component=self.__total.component
            self.__roundId=self.__genRoundId()
            self.__job_number=self.__getJobNumber()
            self.__data=self.__retrieveData(self.__roundId,self.__component)
            self.__report_file= "framework/testserver/report/Report_"+self.__roundId+".html"
            self.__genReport()
            return True
        except Exception,e:
            self._logger.error("the exception is %s" % e.message)
            return False

    def __genRoundId(self):

        return self._config.getValue("TestSession", "jobid")
        #self.__time=self.__total.time
        #return self.__component+self.__time

    def __getJobNumber(self):

        return self._config.getValue("TestSession", "jobnumber")
        #self.__time=self.__total.time
        #return self.__component+self.__time

    def __retrieveData(self,roundId,component):
        query_mapping={'bmci':self.__db.bmciResultQuery,'bmca':self.__db.bmcaResultQuery,'bmn':self.__db.bmnResultQuery,'bmx':self.__db.bmxResultQuery,'bmm':self.__db.bmmResultQuery}
        return query_mapping[component](roundId)

    def __transTime(self,a):
        time=''
        x=a.split(' ')
        if len(x)==2:
            if len(x[0])==8:
                time=time+x[0][0:4]+'-'+x[0][4:6]+'-'+x[0][6:]
                time=time+' '+x[1][0:x[1].index('.')]
        else:
            print "Wrong time format."
        return time


    def __genReportGeneralInfo(self):
        '''
        Replace basic result info in temp report
        '''
        rBuild=self.__total.build
        rJobnumber=self.__job_number
        rCategory=self.__total.category
        if not rCategory:
            rCategory="Null"
        rStart=self.__transTime(self.__total.startTime)
        rEnd=self.__transTime(self.__total.endTime)
        rDuration=self.__total.duration
        #rStatus=self.__total.status
        rTotal=self.__total.total_num
        rPass=self.__total.pass_num
        rFail=self.__total.fail_num
        in_f = ''
        out_f = ''
        try:
            comonent_mapping={'bmci':"BMCI",'bmca':"BMCA",'bmn':"BMN",'bmx':"BMX",'bmm':"BMM"}
            in_f=open(self.__template_file,'r')
            out_f=open(self.__tmp_report_file,'w')
            line=in_f.readline()
            while line:
                line = line.replace('${bemail_component}$', comonent_mapping[self.__component])
                line = line.replace('${build_version}$', rBuild)
                line = line.replace('${jobnumber}$', rJobnumber)
                line = line.replace('${category}$', rCategory)
                line = line.replace('${start_time}$', rStart)
                line = line.replace('${end_time}$', rEnd)
                line = line.replace('${duration}$', str(rDuration))
                line = line.replace('${total_num}$', str(rTotal))
                line = line.replace('${pass_num}$', str(rPass))
                line = line.replace('${fail_num}$', str(rFail))
                out_f.write(line)
                line=in_f.readline()
        finally:
            if in_f:
                in_f.close()
            if out_f:
                out_f.close()

    def __genDetailedInfoTable(self):
        '''
        Draw table with detailed test results
        '''
        n=len((self.__data))
        tr='<tr style="border-left:solid #A8A8A8 1.0pt">\n'
        trr='\n</tr>'
        #tdc='<td nowrap="" colspan="4" style="border-left:solid #A8A8A8 1;border:solid #A8A8A8 1.0pt;border-top:none;padding:.75pt .75pt .75pt .75pt">\n<p class="MsoNormal">'
        td='<td nowrap="" style=" text-align:center;border-top:none;border-left:solid #A8A8A8 1.0pt;border-bottom:solid #A8A8A8 1.0pt;border-right:solid #A8A8A8 1.0pt;padding:.75pt .75pt .75pt .75pt">\n<p class="MsoNormal">'
        tdr='</p></td>\n'

        table=''
        i=0
        while (i<n):

            entry=self.__data[i]
            cspan=int(entry.layer)
            tdc='<td nowrap="" colspan="'+str(str(4-cspan))+'" style="border:solid #A8A8A8 1.0pt;border-top:none;padding:.75pt .75pt .75pt .75pt">\n<p class="MsoNormal">'
            tCase=entry.caseTitle
            tPriority=entry.casePriority.upper()
            tResult=entry.result
            tStart=entry.startTime
            tEnd=entry.endTime
            tElapsed=entry.elapsed


            tCase='<font color="blue">'+tCase+'</font>'
            if tResult=="PASS":
                tResult='<font color="green">'+tResult+'</font>'
            if tResult=="FAIL":
                tResult='<font color="red">'+tResult+'</font>'
            if tResult=='':
                tCase='<i>'+tCase+'</i>'

            #table=table+tr +td*cspan+tdr*cspan +tdc+"${case"+str(i)+"}"+tdr +td+"${result"+str(i)+"}"+tdr +td+"${duration"+str(i)+"}"+tdr +td+"${start"+str(i)+"}"+tdr +td+"${end"+str(i)+"}"+tdr +trr+"\n"
            table=table+tr +(td+tdr)*cspan +tdc+tCase+tdr +td+tPriority+tdr +td+tResult+tdr +td+tElapsed+tdr +td+tStart+tdr +td+tEnd+tdr +trr+"\n"
            i=i+1
        #print table
        return table


    def __genReport(self):
        '''
        Generate the report
        '''
        self.__genReportGeneralInfo()
        table=self.__genDetailedInfoTable()
        target="${detailed_data}$"
        in_f = ''
        out_f = ''
        try:
            in_f=open(self.__tmp_report_file,'r')
            out_f=open(self.__report_file,'w')
            line=in_f.readline()
            while line:
                if line.find(target)>-1:
                    #print line
                    line=line.replace(target,table)
                    #print line
                out_f.write(line)
                line=in_f.readline()
        finally:
            if in_f:
                in_f.close()
            if out_f:
                out_f.close()

    def _genAttachment(self):
        attachments=[]
        rootdir = "framework/testserver/tmp/"
        os.system("mkdir %s"%rootdir)
        robotdir = self._config.getValue("TestSession", "outputdir")
        file_xml = "*.xml"
        file_html = "*.html"
        file_png = "*.png"
        file_tgz = "*.tar.gz"
        if os.path.exists('testserver.log'):
            os.system("cp %s %s " % ("testserver.log",rootdir))
        if os.path.exists("pybot.log"):
            os.system("cp %s %s " % ("pybot.log",rootdir))

        target_log_folder = self._config.getValue("TestSession", "target_log")
        os.system("cp %s %s " % (target_log_folder+"*",rootdir))

        #os.system("cp %s %s " % (robotdir+file_xml,rootdir))
        #os.system("cp %s %s " % (robotdir+file_html,rootdir))
        os.system("cp %s %s " % (robotdir+file_tgz,rootdir))

        #os.system("tar -czvf %s %s %s >/dev/null 2>&1" % (rootdir+"robotlog.tar.gz",robotdir + file_xml, robotdir + file_html))

        os.system("tar -czvf %s --exclude=%s --exclude=%s -C %s . >/dev/null 2>&1" % (rootdir+"robotlog.tar.gz",file_png, file_tgz, robotdir))
        '''
        isPng = False
        for filename in os.listdir(robotdir):
            if filename.endswith('png'):
                isPng = True
                break
        if isPng:
            try:
                os.system("tar -czvf %s --exclude=%s --exclude=%s -C %s . >/dev/null 2>&1" % (rootdir+"robotscreenshot.tgz",file_xml, file_html,robotdir))
            except Exception,e:
                print e.message
        '''
        total_size= 0
        filesize = 0
        for parent,dirnames,filenames in os.walk(rootdir):

            for filename in filenames:
                if filename[0] == ".":
                    continue
                fullname = os.path.join(parent,filename)
                filesize = os.path.getsize(fullname)
                if filesize < 25000000:
                    if (total_size+filesize) < 25000000:
                        attachments.append(fullname)
                        total_size = total_size + filesize
                    else:
                        self._logger.error("the size of all attachments is %i, which will exceed 50M, skip the attachment %s" % (total_size+filesize, filename))
                else:
                    self._logger.error("the size of attachment %s is %i, which exceeds 50M" % (filename, filesize))
                #print attachments
        return attachments

    def sendreport(self):
        nRet = True
        self._logger.info("Retrieve data from database")
        if not self._makedata():
            nRet = False
            return nRet

        self._logger.info("Generate Attachment")
        attachments = self._genAttachment()
        f = ''

        f=open(self.__report_file,'r')
        report=f.readlines()
        mailbody=''
        for line in report:
            line=line.strip()
            mailbody=mailbody+line

        subject = self._config.getValue("Report", "subject") + "-" + self._config.getValue("TestSession", "component").upper() + \
                            " " + self._config.getValue("TestSession", "category") + " " + "T" + str(self.__total.total_num) + "|P" + str(self.__total.pass_num) + "|F" + str(self.__total.fail_num)
        fromname= self._config.getValue("Report", "from")

        category = self.__total.category
        # Manually report will only send to QA
        if category.lower() == "manually":
            to = self._config.getValue("Report", "to_qa")
        else:
            to = self._config.getValue("Report", "to")
        # Nightly report will cc MaWeining
        if category.lower() == "nightly":
            cc = self._config.getValue("Report", "cc")
        else:
            cc = ''
        smtpserver = self._config.getValue("Report", "smtpserver")
        port = self._config.getValue("Report", "port")
        sender = self._config.getValue("Report", "sender")
        passwd = self._config.getValue("Report", "password")
        self._logger.info("Send email")
        for i in range(0,4):
            nRet = sendemail.sendmail(smtpserver, port, sender, subject,fromname, passwd, to, cc, mailbody, attachments)
            if nRet:
                break
        if f:
            f.close()
        return nRet

#r=genreport()
#r.sendreport()
