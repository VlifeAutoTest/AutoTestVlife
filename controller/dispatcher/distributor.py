#! /usr/bin/python
# -*- coding: utf-8 -*-

#import paramiko
#import connMysql
import logging
import logging.config

import commands
import sys
# sys.path.append("..")
from library import *
from library import myglobal
from library import configuration
#FILE_FOLDER = commands.getoutput("echo $BEMAILPATH") + "config/"
#QUEUE_FILE_FOLDER = commands.getoutput("echo $BEMAILPATH") + "dispatcher/"

class distributor:
    __queue_file= "framework/dispatcher/job_queue.txt"
    __base_configuration_ini = myglobal.CONFIGURATONBASEINI
    __tmp_configuration_ini = myglobal.CONFIGURATONINI

    #just for debugging
    #__run_command="nohup python bemail-automation/tsserver.py 0</dev/null 1>/dev/null 2>/dev/null &"
    __run_command="nohup python bemail-automation/tsserver.py > bemail-automation/nohup.log 0</dev/null &"

    def __init__(self):
        self.__config = configuration.configuration()
        self.__config.fileConfig(myglobal.DISPATCHERINI)
        logging.config.fileConfig(myglobal.LOGGINGINI)
        self.__logger=logging.getLogger('distributor')

        host = self.__config.getValue("Database","host")
        user = self.__config.getValue("Database","username")
        pwd = self.__config.getValue("Database","password")
        schema = self.__config.getValue("Database","db")
        port = self.__config.getValue("Database","port")
        self.__db=database.database()
        self.__db.initDB(host, user, pwd, schema, port)

    # def __connectTestServer(self,server):
    #     try:
    #         ssh=paramiko.SSHClient()
    #         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #         ssh.connect(server,username='root',password='svc')
    #     except Exception,e:
    #         print e
    #         ssh=None
    #     return ssh

    def __retrieveTestServer(self,component):
        #server_list={'bmci':'192.168.0.1','bmca':'192.168.0.2','bmm':'192.168.0.3','bmx':'192.168.0.4','bmn':'192.168.0.5'}
        test_server=self.__config.getValue('Test_Server',component).split(",")
        self.__logger.info("The test server is %s"%test_server[0])
        return test_server

    def __retrieveTargetServer(self,component):
        #server_list={'bmci':'192.168.0.1','bmca':'192.168.0.2','bmm':'192.168.0.3','bmx':'192.168.0.4','bmn':'192.168.0.5'}
        target_server=self.__config.getValue('Target_Server',component).split(",")
        self.__logger.info("The target server is %s"%target_server[0])
        return target_server
    '''
    def __retrieveCandicateTargetServers(self,component):
        clientside=['bmci','bmca']
        serverside=['bmn','bmx','bmm']
        if (component in clientside):
            return self.__config.getValue('Target_Server_List','clientside')
        else:
            return self.__config.getValue('Target_Server_List','serverside')

    def __retrieveAvailableTargetServer(self,servers):
        available_target_server=None
        server_list=servers.split(",")
        for server in server_list:
            if self.__isTargetServerFree(server):
                available_target_server=server
                self.__logger.info("The target server is %s"%server)
                break
        return available_target_server
    '''

    # def __isTestServerFree(self,component):
    #     status=False
    #     cmd="select status from AutoResults.TestServers where component=\'"+component.lower()+"\';"
    #     try:
    #         a=connMysql.connMysql().selectCMD(cmd)
    #         if len(a)==1:
    #             if a[0]==0:
    #                 status=True
    #                 self.__logger.debug("Component %s test server is FREE."%component)
    #             else:
    #                 self.__logger.info("Component %s test server is BUSY."%component)
    #     except Exception.e:
    #         print "Cannot retrieve status of test server for %s"%component
    #         self.__logger.error("Cannot retrieve status of test server for %s"%component)
    #     return status

    def __isTestServerFree(self,component):
        if self.__db.testServerStatusQuery(component):
            self.__logger.info("Component %s test server is BUSY."%component)
            return False
        else:
            self.__logger.info("Component %s test server is FREE."%component)
            return True

    # def __isTargetServerFree(self,server):
    #     status=False
    #     cmd="select status from AutoResults.TargetServers where server=\'"+server+"\';"
    #     try:
    #         a=connMysql.connMysql().selectCMD(cmd)
    #         if len(a)==1:
    #             if a[0]==0:
    #                 status=True
    #                 self.__logger.debug("Target server %s is FREE."%server)
    #             else:
    #                 self.__logger.info("Target server %s is BUSY."%server)
    #     except Exception,e:
    #         print "Cannot retrieve status of target server %s"%server
    #         self.__logger.error("Cannot retrieve status of target server %s."%server)
    #     return status

    def __isTargetServerFree(self,component):
        if self.__db.targetServerStatusQuery(component):
            self.__logger.info("Component %s target server is BUSY."%component)
            return False
        else:
            self.__logger.info("Component %s target server is FREE."%component)
            return True

    # def __setTestServerBusy(self,component):
    #     '''
    #     status=1 means server is busy
    #     '''
    #     try:
    #         cmd="update AutoResults.TestServers set status=1 where component=\'"+component+"\'"
    #         connMysql.connMysql().updateCMD(cmd)
    #         self.__logger.debug("Component %s test server status has been changed to BUSY."%component)
    #     except Exception,e:
    #         print "Fail to set the test server of %s to BUSY."%component
    #         self.__logger.error("Fail to set the test server of %s to BUSY."%component)

    def __setTestServerBusy(self,component):
        self.__db.testServerStatusUpdate(component,"1")
        self.__logger.info("Component %s test server status has been changed to BUSY."%component)

    def __setTestServerFree(self,component):
        self.__db.testServerStatusUpdate(component,"0")
        self.__logger.info("Component %s test server status has been changed to Free."%component)

    # def __setTargetServerBusy(self,server):
    #     '''
    #     status=1 means server is busy
    #     '''
    #     try:
    #         cmd="update AutoResults.TargetServers set status=1 where server=\'"+server.lower()+"\';"
    #         connMysql.connMysql().updateCMD(cmd)
    #         self.__logger.debug("Target server %s status has been changed to BUSY."%server)
    #     except Exception,e:
    #         print "Fail to set the target server %s to BUSY."%server
    #         self.__logger.error("Fail to set the target server %s to BUSY."%server)

    def __setTargetServerBusy(self,component):
        self.__db.targetServerStatusUpdate(component,"1")
        self.__logger.info("Component %s target server status has been changed to BUSY."%component)

    def __setTargetServerFree(self,component):
        self.__db.targetServerStatusUpdate(component,"0")
        self.__logger.info("Component %s target server status has been changed to Free."%component)


    def __genRemoteConfig(self,jobid,jobnumer,component,category,upstream_buildurl):
        result=False
        #Generate personalized config
        category_low = category.lower()
        if category_low=="buildly":
            session_include=self.__config.getValue('Buildly_Include',component)
            session_exclude=self.__config.getValue('Buildly_Exclude',component)
            #category = "Smoke"
            #self.__config.setValue('Build_Version',component, build)
            if component == "bmn":
                buildurl_list = self.__config.getValue('Build_Url',component).split(",")
                buildurl_list[0] = upstream_buildurl
                self.__config.setValue('Build_Url',component,buildurl_list[0] + "," + buildurl_list[1])
            else:
                self.__config.setValue('Build_Url',component,upstream_buildurl)
            tmp_urls = upstream_buildurl
            urls = tmp_urls.split('/')
            build = urls[len(urls)-2]
            self.__config.setValue('Build_Version',component,build)
            self.__config.setValue('Job_Num',component,jobnumer)

        else:
            session_include=self.__config.getValue('Nightly_Include',component)
            session_exclude=self.__config.getValue('Nightly_Exclude',component)
            build = self.__config.getValue('Build_Version',component)
            #upstream_buildurl = self.__config.getValue('Build_Url',component)
            #category = "nightly"
        #build_url=self.__config.getValue('Build_Url',component)+build+".exe"
        suite_path=self.__config.getValue('Suite_Path',component)
        log_ip=self.__config.getValue('RobotLogRepository',"ipaddress")
        log_usr=self.__config.getValue('RobotLogRepository',"username")
        log_pwd=self.__config.getValue('RobotLogRepository',"password")
        log_path=self.__config.getValue('RobotLogRepository',"rootpath")

        report_to=self.__config.getValue('Report_To',component)

        target_server = self.__config.getValue('Target_Server',component).split(",")
        test_server = self.__config.getValue('Test_Server',component).split(",")
        #suite_path=self.__config.getValue('Suite_Path','path')+component

        try:
            #Read config from base configuration ini
            fi=open(self.__base_configuration_ini,'r')
            configs=fi.readlines()
            fi.close()
            #After modification, generate a new tmp configuration ini
            fo=open(self.__tmp_configuration_ini,'w')
            for config in configs:
                config = config.replace('${target_ipaddress}$',target_server[0])
                config = config.replace('${target_user}$',target_server[1])
                config = config.replace('${target_pwd}$',target_server[2])
                config = config.replace('${session_include}$',session_include)
                config = config.replace('${session_exclude}$',session_exclude)
                config = config.replace('${session_component}$',component)
                config = config.replace('${build_version}$',self.__config.getValue('Build_Version',component))
                config = config.replace('${build_url}$',self.__config.getValue('Build_Url',component))
                config = config.replace('${job_number}$',jobnumer)
                config = config.replace('${jobid}$',jobid)
                config = config.replace('${suite_path}$',suite_path)
                config = config.replace('${category}$',category)
                config = config.replace('${log_ip}$',log_ip)
                config = config.replace('${log_user}$',log_usr)
                config = config.replace('${log_pwd}$',log_pwd)
                config = config.replace('${root_path}$',log_path)
                config = config.replace('${log_component}$',component)
                config = config.replace('${test_server}$',test_server[0])
                config = config.replace('${report_to}$',report_to)
                fo.write(config)
            fo.close()
            result=True
            self.__logger.info("Temp configuration.ini had been generated.")
        except IOError,e:
            print e.strerror
            self.__logger.error("IO exception: %s"%e.strerror)
        return result

    def __pushConfigToRemote(self,test_server):
        #return scpconnect.scp_cmd(test_server,password,self.__tmp_configuration_ini)
        nRet=False
        if (0 == sshconnect.scp_cmd(test_server[0],test_server[1],test_server[2],self.__tmp_configuration_ini,self.__config.getValue('Test_Server_Settings','autofolder')+'/config/')):
            nRet = True
        return nRet


    def __sendCommand(self,test_server,command):
        #return sshconnect.ssh_cmd(test_server,password,self.__genCommand())
        nRet=False
        if (0 == sshconnect.ssh_cmd(test_server[0],test_server[1],test_server[2],command)):
            nRet = True
        return nRet

    def __removeJobFromQueue(self,job):
        return "#"+job

    def __updatejobstatus(self, jobid, status):
        roundmap=self.__db.RoundMapping()
        roundmap.roundId=jobid
        roundmap.errorMessage=status
        if self.__db.roundMappingQuery(roundmap.roundId):
            self.__db.roundMappingUpdate(roundmap)
        else:
            self.__db.roundMappingInsert(roundmap)

    def __pushJob(self,job):
        '''
        Based on the job, do the following things:
        1. fetch the corresponding test server (fixed mapping currently, will dynamically choose in future)
        2. fetch an available target server
        3. if previous 2 steps succeeds, generate a one-time configuration_base.ini for test server
        4. scp the config to test server
        5. start the script on test server thru ssh
        6. if all above succeed, return 1
        '''
        result = False
        para = job.strip('\n').split(" ")
        #bmca 51 buildly http://192.168.0.33:8080/job/BeMail_Android/ 21
        #jobinfo="$jobid $COM $Build_VersionBER $jobType $UP_STREAM_PROJECT $buildly_number"
        #jobinfo="$jobid $jobType $COMPONENT $Build_VersionBER $UPSTREAM_BUILD_URL"

        jobid = para[0]
        jobtype = para[1]
        component = para[2].lower()
        jobnumber = para[3]
#        projectID = para[2]

        #build = ''
        upstream_buildurl = ''
        if jobtype == 'Buildly':
            upstream_buildurl = para[4]
            #print upstream_buildurl
            if not upstream_buildurl.endswith("/"):
                upstream_buildurl=upstream_buildurl+'/'

        self.__updatejobstatus(jobid, "pending")

        #build=para[2].strip()
        test_server=self.__retrieveTestServer(component)
        target_server=self.__retrieveTargetServer(component)
        if self.__isTestServerFree(component) and self.__isTargetServerFree(component):

            self.__setTestServerBusy(component)
            self.__setTargetServerBusy(component)

        #--    if True:
            if (self.__genRemoteConfig(jobid,jobnumber,component,jobtype,upstream_buildurl) and self.__pushConfigToRemote(test_server)):
                self.__logger.info("Succeed pushing config to %s."%test_server[0])
                if self.__sendCommand(test_server,self.__run_command):
                    result=True
                    self.__logger.info("Succeed start job on %s."%test_server[0])
                    self.__updatejobstatus(jobid, "going")
                else:
                    self.__setTestServerFree(component)
                    self.__setTargetServerFree(component)
                    self.__logger.error("Fail to start job on %s !!!"%test_server[0])
            else:
                self.__logger.error("Fail to push config to %s !!!"%test_server[0])
        #else:
        #    self.__logger.error("No available target server to be tested. Skip this job in current round.")
        else:
            self.__logger.info("The test server %s and/or target server %s is BUSY. Skip this job in current round." % (test_server, target_server))
        return result


    def checkQueue(self):
        '''
        open queue file
        check if any new jobs to be issued
        if finding new job, push the job
        if pushing job successfully, annotate the job in the queue file
        '''
        try:
            #print self.__queue_file
            fr=open(self.__queue_file,'r')
            jobs=fr.readlines()
            #print jobs
            fr.close()
            count=0
            for i in range(len(jobs)):
                if jobs[i].startswith("#"):
                    continue
                elif len(jobs[i])>2:
                    self.__logger.info("New job is found in queue: %s"%jobs[i])
                    count=count+1
                    if self.__pushJob(jobs[i]) == 1:
                        self.__logger.info("Job \"%s\" had been annotated in the queue."%jobs[i])
                        jobs[i]=self.__removeJobFromQueue(jobs[i])
            if count==0:
                self.__logger.info("There is no new job in the queue.")
            fr.close()
            fw=open(self.__queue_file,'w')
            fw.writelines(jobs)
            fw.close()

        except IOError,e:
            print e.strerror
            self.__logger.error("IO exception: %s"%e.strerror)





#d=distributor()
#d.checkQueue()
#command="ps -ax | grep ping | wc -l"
#d.sendCommand()
#server='192.168.0.196'
#print (d.isTestServerFree(server))

#component='bmci'
#d.isServerFree(component)
#d.setServerBusy(component)
