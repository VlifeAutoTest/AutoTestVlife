#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import time


desfolder = os.path.dirname(sys.argv[0])
if desfolder != '':
    os.chdir(desfolder)
os.chdir("../..")
print ("workspace is %s" % os.getcwd())

sys.path.append(os.getcwd())
#print sys.path
from library import configuration
from library import myglobal
from library import db

config = configuration.configuration()
config.fileConfig(myglobal.DISPATCHERINI)
host = config.getValue("Database","host")
user = config.getValue("Database","username")
pwd = config.getValue("Database","password")
schema = config.getValue("Database","db")
port = config.getValue("Database","port")
db=database.database()
db.initDB(host, user, pwd, schema, port)
roundmap = db.RoundMapping()
roundmap.roundId=sys.argv[1]
entry = None
time.sleep(60)
while True:
    entry = db.roundMappingQuery(roundmap.roundId)
    if entry != None:
        #print "Get the jobid %s" % roundmap.roundId
        if (entry.errorMessage == "SUCCEED"):
            os.system("echo SUCCEED > result.txt")
            break
        elif (entry.errorMessage == "FAILED"):
            os.system("echo FAILED > result.txt")
            break
        elif  (entry.errorMessage == "WARNING"):
            os.system("echo WARNING > result.txt")
            break
    time.sleep(60)



