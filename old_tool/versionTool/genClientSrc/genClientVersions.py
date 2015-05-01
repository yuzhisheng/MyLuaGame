# -*- coding: utf-8 -*

import sys, os, stat
import string
import platform


path=sys.argv[0][0:sys.argv[0].rfind(os.sep)+1]
sys.path.insert(0,path + "../../utils")

from tool import *
chDirToExecPath()
config = None
envConfig = None
newArray = fileversions_pb2.file_item_array()
#上一个版本的pb
prevArray = fileversions_pb2.file_item_array()

pkeys = None

plist ={ 'filenames':{},
'metadata':{'version':1} 
}
fileHash = plist["filenames"]

striptFileList = []

def preProcessFiles(filename):
	if not isImageFile(filename):
		return	
	fmtname = getShortFileName(filename, currentConfig["rootDir"])
	if fmtname in pkeys:
		processImage(fileHash, filename,currentConfig["rootDir"])
	else:
		print fmtname + " not in pkeys"
		decryptFile(filename)
	
#生成一个版本item
def genVersion(filename):
	item = newArray.items.add()
	item.file_path = formatFileName(filename,currentConfig["rootDir"])
	print  "genVersion " + " " + filename  + "   " + envConfig["android_pay"]
	print str(envConfig["android_pay"] == "1")
	if envConfig["android_pay"] == "1":
		decryptFile(filename)
		stripFile(filename)
		print("strip file  " + filename)
		encryptFile(filename)
	item.md5 = get_md5_value(filename)
	item.url = item.file_path + currentConfig["version"]
	item.size = os.path.getsize(filename)

def createPackageVersion():
	local_tzinfo=GMT8()#本地时区，+8区
	tm = datetime.fromtimestamp(time.time(), local_tzinfo)
	timeStr = tm.strftime('%m%d_%H%M')
	print "time is " + str(timeStr)
	f = open(currentConfig["rootDir"] + "/" + "packageConf.txt","wb") 
	f.write(timeStr)
	f.close()
	
def getPrevVersionFile():
	url = envConfig["url"]  + "versions_" + currentConfig["platform"] +  currentConfig["prevVersion"]
	try:
		f = urllib2.urlopen(url)
		prevArray.ParseFromString(f.read())
		f.close()
	except:
		print "download file from " + url + "  failed!"
		url = "clientVersions.pb"
		if os.path.exists(url):
			f = open(url, "rb")
			prevArray.ParseFromString(f.read())
			f.close()

def loadStripFileList():
	global striptFileList
	if os.path.exists("striplist.txt"):
		f = open("striplist.txt")
		striptFileList = f.readlines()
		f.close()
		print "striptFileList load success %d files"%(len(striptFileList))


def run():
	newArray.Clear()
	global envConfig
	if len(sys.argv) > 1:
		currentConfig["rootDir"] = sys.argv[1]
	if len(sys.argv) > 2:
		envConfig = currentConfig[sys.argv[2]]
	else:
		envConfig = currentConfig[config["env"]]
	if len(sys.argv) > 3:
		currentConfig["version"] = getVersion3From4(sys.argv[3])

	# getPrevVersionFile()
	loadStripFileList()
	setGamesetting(currentConfig, envConfig)
	# setLuaVersion(currentConfig, envConfig)
	#walk(currentConfig["rootDir"], preProcessFiles, config["exclude"])
	writePlistFile(plist, currentConfig["rootDir"] + "/" + "hash.plist")
	walk(currentConfig["rootDir"], genVersion, config["exclude"])
	newArray.url = envConfig["url"] + "/" + currentConfig["platform"] + "/"
	newArray.version = currentConfig["version"]
	writeToPB(newArray, currentConfig["rootDir"] + "/" + "clientVersions.pb");
	createPackageVersion()

	
config = loadConfig()

if not isMac():
	print "in android"
	currentConfig = config["android"]
else:
	print "in ios"
	currentConfig = config["ios"]

print os.path.abspath("Hash.plist")
pkeys = readPlistFile(os.path.abspath("Hash.plist")).filenames
run()

print("success, total processed %d files" % (len(newArray.items)))

sys.exit(0)
#os.system("pause")
