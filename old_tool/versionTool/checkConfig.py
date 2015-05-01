# -*- coding: utf-8 -*

import sys, os, stat
import string
import platform
reload(sys)
sys.setdefaultencoding('utf-8') 

path=sys.argv[0][0:sys.argv[0].rfind(os.sep)+1]
sys.path.insert(0,path + "../utils")
from tool import *

chDirToExecPath()
config = None
envConfig = None

svrConfigPath = r"\\10.12.196.75\qday\client\config\qday"

def checkChange(fullpath):
	filename = os.path.split(fullpath)[-1]
	filepath = os.path.split(fullpath)[0]
	svrName = svrConfigPath
	if filepath.endswith("Config"):
		svrName = svrName + "\\pb\\" + filename
	elif filepath.endswith("Data"):
		svrName = svrName + "\\lua\\" + filename
	cmd = "@echo off&copy %s .  >null"%(svrName)
	os.system(cmd)
	if not os.path.exists(filename):
		# print filename + " not exist"
		return 
	if get_md5_value(fullpath) != get_md5_value(filename):
		print filename + " changed"
	os.system("del " + filename)

def run():
	walk(currentConfig["rootDir"] + "/Config", checkChange)
	walk(currentConfig["rootDir"] + "/Script/Data", checkChange)

config = loadConfig()

if not isMac():
	# print "in android"
	currentConfig = config["android"]
else:
	# print "in ios"
	currentConfig = config["ios"]
run()



# sys.exit(0)
os.system("pause")
