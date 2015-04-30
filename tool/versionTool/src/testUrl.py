# -*- coding: utf-8 -*
import sys, os, stat
import hashlib
import string
import shutil
import platform
from zipfile import * 
import zipfile 
import urllib
import urllib2

path=sys.argv[0][0:sys.argv[0].rfind(os.sep)+1]
sys.path.insert(0,path + "../../utils")
from tool import *
chDirToExecPath()

config = None
envConfig = None
#新的pb
newArray = fileversions_pb2.file_item_array()

successnum = 0
failednum = 0

path=sys.argv[0][0:sys.argv[0].rfind(os.sep)+1]
if len(path) != 0:
	os.chdir(path)
#读取配置文件
def loadConfig():
    global config	
    configPath =  './config.txt'
    while not os.path.exists(configPath):
        os.chdir('../')
    f = file(configPath)
    config = json.load(f)
    f.close()
			
def get_md5_valuefromData(data):
	myMd5 = hashlib.md5()
	myMd5.update(data)
	myMd5_Digest = myMd5.hexdigest()
	return myMd5_Digest
	
def getCurrentVersionFile(array):
	pbName = "versions_" + currentConfig["platform"] + currentConfig["version"]
	url = envConfig["url"] + urllib.quote(pbName)
	try:
		f = urllib2.urlopen(url)
		content = f.read()
		array.ParseFromString(content)
		f.close()
		print "download version file from " + url + "  success!, md5 is " + get_md5_valuefromData(content)
	except:
		print "download file from " + url + "  failed!"
		
def testDownLoadFiles(array):
	global failednum
	global successnum
	for item in array.items: 
		url = envConfig["url"] + currentConfig["platform"] + "/" + urllib.quote(item.url)
		try:
			f = urllib2.urlopen(url)
			str = f.read()
			fileMd5 = get_md5_valuefromData(str)
			if fileMd5 == item.md5:
				print ("download file from #%s# size is %d %s success! " %(url, item.size, fileMd5))
				successnum = successnum + 1
			else:
				print ("file from #%s# md5 is %s, configMd5 is %s!" %(url,fileMd5 , item.md5))
				failednum = failednum + 1
			f.close()
		except urllib2.URLError,e:
			print "download file from #" + url + "#  failed!, reason: " + e.reason
			failednum = failednum + 1

def run():
	newArray.Clear()
	getCurrentVersionFile(newArray)
	testDownLoadFiles(newArray)

loadConfig()

sysstr = platform.system()
print sysstr
if(sysstr =="Windows"):
	currentConfig = config["android"]
else:
	currentConfig = config["ios"]
envConfig = currentConfig[config["env"]]
run()

print("success, total processed %d files, success %d, failed %d" % (len(newArray.items), successnum, failednum))

os.system("pause")