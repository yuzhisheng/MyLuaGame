# -*- coding: utf-8 -*
#读取配置文件
import json
import sys, os, stat
import hashlib
import fileversions_pb2
import client_gamesetting_conf_pb2
from biplist import*
from datetime import *
import time
import platform
import re
import codecs

texopt = {
# "texture-format" : "pvr2ccz",
"padding" : "0",
"trim-mode" : "None",
"algorithm" : "Basic",
"size-constraints" : "AnySize",
"max-size" : "4096",
"premultiply-alpha":" "
}

	#设置gamesetting.pb里面资源服务器url
def setValueKey(array, key, value, replace = True):
	for item in array.items: 
		if item.key == key:
			if not replace:
				return
			item.value = value
			return
	item = array.items.add()
	item.key = key
	item.value = value

def setGamesetting(currentConfig, envConfig):
	settingArray = client_gamesetting_conf_pb2.client_gamesetting_conf_array()
	filename = currentConfig["rootDir"] + "/" + "GameSetting.pb" 
	readFromPB(settingArray, filename)
	#设置资源服务器路径
	setValueKey(settingArray, "res_server_url", envConfig["url"])
	print "res server url: " +  envConfig["url"]
	#设置公告文件路径
	bulletinurl = envConfig["url"] + "bulletin_" + currentConfig["platform"] + ".txt"
	setValueKey(settingArray, "bulletin_file_url", bulletinurl)
	print "bulletin url: " +  bulletinurl
	#版本信息文件
	setValueKey(settingArray, "server_version_file", "versions_" + currentConfig["platform"])
	print "server_version_file : " +  "versions_" + currentConfig["platform"]
	#版本号
	setValueKey(settingArray, "client_res_version", currentConfig["version"], False)
	print "client_res_version : " + currentConfig["version"]
	#设置服务器ip
	setValueKey(settingArray, "ip", envConfig["serverIP"])
	print "server ip: " +  envConfig["serverIP"]
	#设置支付环境
	setValueKey(settingArray, "android_pay", envConfig["android_pay"])
	print "android_pay : " +  envConfig["android_pay"]
	writeToPB(settingArray, filename)

def setLuaVersion(currentConfig):
	print "setLuaVersion to version " + currentConfig["version"]
	filename = currentConfig["rootDir"] + "/Script/script_config.lua" 
	replaceFile(filename, r'(.*current_res_version\s*=\s*")(.*)(".*)', currentConfig["version"])
	
def replaceFile(filename, reStr, destStr):
	# p = re.compile(reStr)
	f= open(filename, 'rb')
	content = f.read()
	# print "content before replace: "+ content 
	f.close()
	result =re.sub(reStr,  r'\g<1>%s\g<3>'%(destStr), content)
	if content == result:
		print filename + " need not modify!"
		return
	f= open(filename, 'wb')  
	f.write(result)
	# print "content after replace: "+ result
	f.close()
	
#去除空行 注释和log
def stripFile(filename):
	# return
	if not filename.endswith(".lua") or isMac():
		return
	print "stripFile " + filename
	removeCommentAndLog(filename)
	removeEmptyLines(filename)
	
def removeEmptyLines(filename):
	f= open(filename, 'rb')
	lines = f.readlines()
	f.close()
	lines = [line for line in lines if line.strip()]
	f = open(filename, "wb")
	f.writelines(lines)
	f.close()
	
def removeCommentAndLog(filename):
	f= open(filename, 'rb')
	content = f.read()
	f.close()
	content = re.sub(re.compile("--\[\[.*?\]\]",re.DOTALL ) ,"" ,content)
	content = re.sub(re.compile("--.*" ) ,"" ,content)
	content = re.sub(re.compile("cclog\s*?\(.*?\n" ) ,"" ,content)
	content = re.sub(re.compile("print\s*?\(.*?\n" ) ,"" ,content)

	f = open(filename, "wb")
	f.write(content)
	f.close()

	
	
def getTxtOptByDict(opts):
	ret = ""
	for (k,v) in  opts.items():
		ret = ret + "--" + k + " " + v + " "
	return ret

def getSizeStr(size):
	ret = ""
	kb = size / 1024.0
	mb = kb / 1024.0
	if mb > 1:
		ret = "%.2f MB"%(mb)
	elif kb > 1:
		ret = "%d KB"%(kb)
	else:
		ret = "%d Byte"%(size)
	return ret
	
def getVersion3From4(verName):
	ret = verName
	verList = verName.split('.')
	if len(verList) > 3:
		verCode = verList[-1]
		ret = verName[:-len(verList[-1]) - 1]
	return ret

def chDirToExecPath():
	path=sys.argv[0][0:sys.argv[0].rfind(os.sep)+1]
	# print "exe path is " + path
	if len(path) != 0:
		os.chdir(path)
		
def loadConfig():
	configPath =  './config.txt'
	while not os.path.exists(configPath):
		os.chdir('../')
	# print "load config, dir is:" + os.path.abspath(configPath)
	f = file(configPath)
	config = json.load(f, strict=False)
	f.close()
	return config
	
#获取一个文件的md5
def get_md5_value(filename):
    f= open(filename, 'rb')  
    return get_md5_valuefromData(f.read())

def get_md5_valuefromData(data):
	myMd5 = hashlib.md5()
	myMd5.update(data)
	myMd5_Digest = myMd5.hexdigest()
	return myMd5_Digest
	
class GMT8(tzinfo):
	delta=timedelta(hours=8)
	def utcoffset(self,dt):
		return self.delta
	def tzname(self,dt):
		return "GMT+8"
	def dst(self,dt):
		return self.delta
	
#格式化文件路径
def formatFileName(filename, rootDir):
    rootLen = len(rootDir) + 1
    return filename[rootLen :].replace('\\', '/')
	
#去除掉分辨率路径
def stripResolutionDir(filename):
	if filename.startswith("HD/") or filename.startswith("LD/"):
		return filename[3:]
	return filename
	
def getItemByFilename(array, filename):
	for item in array.items:
		if item.file_path == filename:
			return item
			
#将pb写入制定文件
def writeToPB(array, file):
	f = open(file,"wb") 
	print "save File " + file
	try:
		f.write(array.SerializeToString())  
	except:
		print "write " + file + "  failed!"
	finally:
		f.close()  

#读取一个文件到pb
def readFromPB(array, file):
	if not os.path.exists(file):
		print  file + "  not exist!"
		return
	f = open(file,"rb") 
	try:
		content = f.read()
		array.ParseFromString(content)
	except:
		print "read " + file + "  failed!"
	finally:
		f.close()
		
def isImageFile(path):
	ret = path.endswith(".png") or path.endswith(".jpg") or\
	path.endswith(".pnggl") or path.endswith(".jpggl") 
	return ret
	
def encryptFile(path):
	absPath = os.path.abspath(path)
	if isFileNeedEncrypt(absPath):
		print "encrypt file " + absPath
		os.system("cd ./../encryptTool/src/ && "  + "python ./encrypt.py 1 " +   absPath)
		
def decryptFile(path):
	absPath = os.path.abspath(path)
	if isFileNeedEncrypt(absPath):
		print "encrypt file " + absPath
		os.system("cd ./../encryptTool/src/ && "  + "python ./encrypt.py 2 " +   absPath)

def isLuaFile(path):
    return path.endswith(".lua")

#mac 下有luajit 不加密了
def isFileNeedEncrypt(path):
	#return (isLuaFile(path) and not isMac()) or isImageFile(path)
	return (isLuaFile(path) and not isMac()) 

def getExecPrefix():
	sysstr = platform.system()
	if(sysstr !="Windows"):
		sysstr = "./"
	else:
		sysstr = ""
	return sysstr
	
def jitFile(path):
	if not isMac():
		return
	absPath = os.path.abspath(path)
	#lua jit
	jitDir=os.path.abspath("../../cocos2dx_src/scripting/lua/luajit/LuaJIT-2.0.1/src")
	if isLuaFile(absPath):
		os.system("cd " + jitDir  + " && " + getExecPrefix() + "luajit -b " + absPath + " " + absPath)

def fileNameOfExt(filename, ext):
	pos=filename.rfind(".")
	return filename[:pos] + ext

def isFileNeedToConvert(filename):
	plistName = fileNameOfExt(filename, ".plist")
	atlasName = filename.split("-")[0] + ".atlas"
	return os.path.exists(plistName) or os.path.exists(atlasName)
	
def convertToPvr(filename):
	if not isFileNeedToConvert(filename):
		return filename
	pos=filename.rfind(".")
	newName = fileNameOfExt(filename, ".pvr")
	print "---------" + filename
	#--opt PVRTC4
	cmd = "..\TexturePacker\TexturePacker.exe "
	cmd = cmd + getTxtOptByDict(texopt)
	#cmd = cmd + " --data " + (fileNameOfExt(filename, ".plist"))
	cmd = cmd + " --sheet " + (fileNameOfExt(filename, ".pvr")) 
	cmd = cmd + " " + filename
	
	print cmd
	os.system(cmd)
	os.remove(filename)
	return newName

def renameFileWithExt(filename, ext):
	if filename.endswith(ext):
		return filename
	newName = filename + ext
	os.rename(filename, newName)
	return newName
	
def getShortFileName(filename, rootDir):
	shortName = formatFileName(filename,rootDir)
	shortName = stripResolutionDir(shortName)
	return shortName
	
#文件处理		
def processImage(fileHash, filename, rootDir):
	if not isImageFile(filename):
		return	
	newName = renameFileWithExt(filename, "gl")
	if newName == filename:
		filename = filename[:-2]
	filename = getShortFileName(filename,rootDir)
	newName = getShortFileName(newName, rootDir)
	if filename != newName:
		fileHash[filename] = newName

def writePlistFile(plist, filename):
	try:
		writePlist(plist,filename, False)
	except (InvalidPlistException,NotBinaryPlistException), e:
		print "Something bad happened:",e

def readPlistFile(filename):
	try:
		plist = readPlist(filename)
		return plist
	except (InvalidPlistException,NotBinaryPlistException), e:
		print "Something bad happened:",e

	
def walk(path, function, excludes = []):
    for item in os.listdir(path):
        subpath = os.path.join(path, item)
        if subpath.split(os.sep)[-1] in excludes:
            print "skip " + subpath
            continue
        mode = os.stat(subpath)[stat.ST_MODE]
        if stat.S_ISDIR(mode):
            walk(subpath, function, excludes)
        else:
            function(subpath)
			
def isWindows():
	sysstr = platform.system()
	return sysstr =="Windows"
def isMac():
	sysstr = platform.system()
	return sysstr =="Darwin"
def isLinux():
	sysstr = platform.system()
	return sysstr =="Linux"