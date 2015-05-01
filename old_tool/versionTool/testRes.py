# -*- coding: utf-8 -*
import sys, os, stat
import hashlib
import string
import shutil
import platform
from zipfile import * 
import zipfile 

path=sys.argv[0][0:sys.argv[0].rfind(os.sep)+1]
sys.path.insert(0,path + "../utils")
from tool import *


newArray = fileversions_pb2.file_item_array()

resDir = ""

	
def getCurrentVersionFile(array):
	global resDir
	pbName = resDir + "clientVersions.pb"
	if not os.path.exists(pbName):
		for file in os.listdir(resDir):
			if file.startswith("versions_"):
				pbName = resDir + file
				if isMac():
					resDir = resDir + "ios" + os.sep
				else:
					resDir = resDir + "android" + os.sep

	f = open(pbName, "rb")
	content = f.read()
	array.ParseFromString(content)
	f.close()
	
def testFile(newArray):
	failedNum = 0
	succedNum = 0
	for item in newArray.items:
		realPath = ""
		if os.path.exists(resDir + item.file_path):
			realPath = resDir + item.file_path
		elif os.path.exists(resDir + item.url):
			realPath = resDir + item.url
		else:
			continue
		if item.md5 == get_md5_value(realPath):
			print item.file_path + " success"
			succedNum = succedNum + 1
		else:
			print item.file_path + " Failed!"
			failedNum = failedNum + 1
	print "complete, success %d, failed %d"%(succedNum, failedNum)
		
def run():
	newArray.Clear()
	getCurrentVersionFile(newArray)
	testFile(newArray)


if len(sys.argv) <= 1:
	print "please input directory!"
	exit(0)

resDir = sys.argv[1] + os.sep
run()


os.system("pause")