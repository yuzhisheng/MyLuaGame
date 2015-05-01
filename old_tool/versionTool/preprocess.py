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
verCode = None
verName = None

def setGameSetting():
	print "set setGameSetting version: " + verName
	filename = "../../GL_Project/Classes/GLGameSetting.cpp"
	replaceFile(filename, r'(.*CURRENT_CLIENT_VERSION\s*=\s*")(.*)(".*)', verName)
	replaceFile(filename, r'(.*CURRENT_RES_VERSION\s*=\s*")(.*)(".*)', verName)
	
# def setLuaVersion():
	# print "setLuaVersion to version " + currentConfig["version"]
	# filename = currentConfig["rootDir"] + "/Script/script_config.lua" 
	# replaceFile(filename, r'(.*current_res_version\s*=\s*")(.*)(".*)', currentConfig["version"])
	
def setManifestVersion():
	if isMac():
		return
	filename = "../../GL_Project/proj.android/AndroidManifest.xml"

	print "set mainfest version: " + config["versionName"]
	replaceFile(filename, r'(.*versionName\s*=\s*")(.*)(".*)', verName)
	replaceFile(filename, r'(.*versionCode\s*=\s*")(.*)(".*)', verCode)
	

def run():
	setLuaVersion(currentConfig)
	setGameSetting()
	setManifestVersion()
	
	# filename = "../../GL_Project/Resources/Script/script_plugin_lib.lua"
	# stripFile(filename)

	

config = loadConfig()

if not isMac():
	print "in android"
	currentConfig = config["android"]
else:
	print "in ios"
	currentConfig = config["ios"]
envConfig = currentConfig[config["env"]]

if len(sys.argv) > 1:
	config["versionName"] = sys.argv[1]
if len(sys.argv) > 2:
	currentConfig["version"] = getVersion3From4(sys.argv[2])
verName = config["versionName"]
verList = verName.split('.')
verCode = verList[-1]
verName = getVersion3From4(verName)


run()



sys.exit(0)
#os.system("pause")
