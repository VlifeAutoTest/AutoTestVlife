#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import os.path
import logging
import logging.config

from library import configuration
from library import myglobal

import savelog
import genreport
import testserver
import sendemail

_XML_FILE='framework/testserver/robotlog/output.xml'

_config = None
_logger = None
_config = configuration.configuration()
_config.fileConfig(myglobal.LOGGINGINI)
_config.setValue("handler_fileHandler", "args", ('testserver.log', 'a'))
_config.setValue("handler_fileHandler", "level", "INFO")
_config.setValue("handler_consoleHandler", "level", "INFO")
logging.config.fileConfig(myglobal.LOGGINGINI)
_logger=logging.getLogger('main')

def _sendAlert():

        attachments = []
        filename = 'testserver.log'
        rootdir = os.getcwd()
        if os.path.exists(filename):
            fullname = os.path.join(rootdir,filename)
            attachments.append(fullname)

        mailbody = 'Please check it manually!!!'
        _config.fileConfig(myglobal.CONFIGURATONINI)
        subject = _config.getValue("Report", "subject") + "-" + _config.getValue("TestSession", "component").upper() + \
                            " " + _config.getValue("TestSession", "category") + " " + "Test is blocked"
        # category = _config.getValue("TestSession", "category")
        # if category.lower() == "nightly":
        #     cc = _config.getValue("Report", "cc")
        # else:
        #     cc = ''
        cc = ''
        fromname= _config.getValue("Report", "from")
        # to = _config.getValue("Report", "to")
        to = "qa_tj@nationsky.com"
        smtpserver = _config.getValue("Report", "smtpserver")
        port = _config.getValue("Report", "port")
        sender = _config.getValue("Report", "sender")
        passwd = _config.getValue("Report", "password")

        try:
            #_logger.info("Test is terminated, send out alert")
            sendemail.sendmail(smtpserver, port, sender, subject,fromname, passwd, to, cc, mailbody, attachments)
        except Exception,e:
            _logger.error(e.message)


def runit(log_level = "INFO"):
    nResult = True
    _config = configuration.configuration()
    _config.fileConfig(myglobal.LOGGINGINI)
    _config.setValue("handler_fileHandler", "args", ('testserver.log', 'a'))
    _config.setValue("handler_fileHandler", "level", log_level)
    _config.setValue("handler_consoleHandler", "level", log_level)

    logging.config.fileConfig(myglobal.LOGGINGINI)

    _logger=logging.getLogger('main')
    ts = testserver.testserver()

    _logger.info("Lock the test server and target server in database")
    ts.setStatus("1")

    _logger.info("Download and push the build to target server")
    nResult = ts.getBuildReady()
    if not nResult:
        _logger.error("Failed to get build, break this test session")
        _sendAlert()
        _logger.info("Unlock the test server and target server in database")
        ts.setStatus("0")
        _logger.info("Update job status as FAILED in database")
        ts.updateJobStatus("FAILED")
        #to Send alert message
        _logger.info("=======Quit the job========")
        return

    _logger.info("Execute Robot Framework Test...")
    ts.startTest()
    _logger.info("Robot Framework Test Done")

    if not os.path.exists(_XML_FILE):
        _logger.error("The robot framework test is broken unexpected")
        _logger.info("Update job status as FAILED in database")
        ts.updateJobStatus("FAILED")
        _logger.error("Failed to get output.xml, the test is abnormal")
        _sendAlert()
        _logger.info("Unlock the test server and target server in database")
        ts.setStatus("0")
        _logger.info("=======Quit the job========")
        return

    _logger.info("Save the test result in database")
    save = savelog.savelog()
    if not save.isTrue():
        _logger.error("Fail to save log")
        _logger.info("Update job status as FAILED in database")
        ts.updateJobStatus("FAILED")
        _logger.info("Fail to save log to database, send alert")
        _sendAlert()
        _logger.info("Unlock the test server and target server in database")
        ts.setStatus("0")
        _logger.info("=======Quit the job========")
        return

    nResult = save.insertDetailedRecords()
    nResult = nResult and save.insertMappingRecord()
    nResult = nResult and save.insertTotalRecord()
    # nResult = nResult and save.updateIndividualLPB()
    if not nResult:
        _logger.error("Fail to save log")
        _logger.info("Update job status as FAILED in database")
        ts.updateJobStatus("FAILED")
        _logger.info("Fail to save log to database, send alert")
        _sendAlert()
        _logger.info("Unlock the test server and target server in database")
        ts.setStatus("0")
        _logger.info("=======Quit the job========")
        return

    _logger.info("Generate the test result data")
    report = genreport.genreport()

    _logger.info("Upload the robot framework logs")
    ts.uploadLog()

    _logger.info("Update job status as SUCCEED in database")
    ts.updateJobStatus("SUCCEED")

    _logger.info("Send out test report by email")
    if not report.sendreport():
        _logger.info("Update job status as FAILED in database")
        ts.updateJobStatus("FAILED")
        _logger.info("Fail to send out test report by email, send alert")
        _sendAlert()

    _logger.info("Unlock the test server and target server in database")
    ts.setStatus("0")

    _logger.info("========Test server completes the job==========")


