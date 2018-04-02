__author__ = 'CarlGao'

import sys
import time
import logging
import logging.config
import os

# desfolder = os.path.dirname(sys.argv[0])
# if desfolder != '':
#     os.chdir(desfolder)
# print ("workspace is %s" % os.getcwd())
#
# sys.path.append("../..")
from library import myglobal
from library import configuration
import dispatcher
#import configuration
#import commands
#FILE_FOLDER = commands.getoutput("echo $BEMAILPATH") + "config/"


timeout=60
scheduled_nightly_time="20:00"
log_level="INFO"


# if __name__ == '__main__':
#     if len(sys.argv)==2:
#         #Help
#         if sys.argv[1].lower() in ("help","-help","--help","-h"):
#             print "Usage:\n" \
#                   "Run the script directly: (Default log level is 'INFO')\n" \
#                   "Sample:\tpython runme.py\n" \
#                   "Run script with customized log level: ('DEBUG','INFO','WARNING','ERROR','CRITICAL')\n" \
#                     "Sample:\tpython runme.py INFO\n"
#             sys.exit(0)
#         #Customize log level
#         elif sys.argv[1].upper() in ("DEBUG","INFO","WARNING","ERROR","CRITICAL"):
#             log_level=sys.argv[1].upper()

def run(log_level = "INFO"):
    config = configuration.configuration()
    config.fileConfig(myglobal.LOGGINGINI)
    config.setValue("handler_fileHandler", "args", ('dispatcher.log', 'a'))
    config.setValue("handler_fileHandler", "level", log_level)
    config.setValue("handler_consoleHandler", "level", log_level)
#    logging.config.fileConfig(FILE_FOLDER + configuration.configuration("dispatcher.ini").getValue('Log','file'))
    logging.config.fileConfig(myglobal.LOGGINGINI)
    logger=logging.getLogger('main')

    d=dispatcher.dispatcher()

    while True:
        logger.info("Run periodically build and queue check.")

        config.fileConfig(myglobal.CONFIGURATONINI)
        type=config.getValue("Platform", "type")
        if type=="integration":
            #run scheduled integration necessity check
            d.checkIntegrationNecessity()
        else:
            #run scheduled build check
            d.scheduledCheck()
        #check the queue to see if any new job to do
        d.scanQueue()
        '''
        #add nightly jobs only on designated time
        currentTime=time.strftime('%H%M',time.localtime())
        scheduledTime=scheduled_nightly_time.replace(":","")
        if int(currentTime)>=int(scheduledTime) and int(currentTime)<(int(scheduledTime)+timeout/60):
            #print "It comes to the scheduled time, add nightly jobs."
            logger.info("It comes to the scheduled time, add nightly jobs.")
            d.addNightlyJobs()
        '''
        #wait for a whole
        logger.info("Sleep for %i minutes"%(timeout/60))
        time.sleep(timeout)

        continue