# -*- coding: utf-8 -*
import sys, os, stat
import shutil
import platform
from zipfile import * 
import zipfile 
import urllib2
path=sys.argv[0][0:sys.argv[0].rfind(os.sep)+1]
sys.path.insert(0,path + "../../utils")
from tool import *

config = None
envConfig = None

zipFile = None
#新的pb
newArray = fileversions_pb2.file_item_array()
#上一个版本的pb
prevArray = fileversions_pb2.file_item_array()

chDirToExecPath()
pkeys = None

plist ={ 'filenames':{},
'metadata':{'version':1} 
}

fileHash = plist["filenames"]

fileList = []
striptFileList = []

#将增量文件拷贝到指定的目录(目录名为版本号)并加密
def copyIncrementFileToResDirAndEncrypt(item):
		fileSavePath = config["output"] + currentConfig["platform"]
		tmpSavePath = currentConfig["rootDir"]  + "/" + item.file_path

		jitFile(tmpSavePath)
		encryptFile(tmpSavePath)
		prevItem = getItemByFilename(prevArray, item.file_path )
		if isImageFile(tmpSavePath) and not tmpSavePath.endswith("gl"):
			decryptFile(tmpSavePath)
			print "decrypt file prevItem..." + tmpSavePath + "  "+get_md5_value(tmpSavePath)
		item.md5 = get_md5_value(tmpSavePath)
		if prevItem == None or prevItem.md5 != item.md5:
			if tmpSavePath.endswith(".lua"):
				decryptFile(tmpSavePath)
				stripFile(tmpSavePath)
				encryptFile(tmpSavePath)
				item.md5 = get_md5_value(tmpSavePath)
				if prevItem != None and item.md5 == prevItem.md5:
					item.url = prevItem.url
					item.size = prevItem.size
					return
				
			print "%s  need update, size is %d"%(item.file_path , os.path.getsize(tmpSavePath))
			path = os.path.split(fileSavePath + "/" + item.file_path)[0]
			if not os.path.exists(path):
				os.makedirs(path)
			destFilename = fileSavePath +   "/" + item.url
			shutil.move(tmpSavePath,  destFilename)
			zipFile.write(destFilename, currentConfig["platform"] + "/" + item.url) 
			item.size = os.path.getsize(destFilename)
			fileList.append(item)

		else:
			item.url = prevItem.url
			item.size = prevItem.size
           
#生成一个版本item
def genVersion(filename):
	item = newArray.items.add()
	item.file_path = formatFileName(filename, currentConfig["rootDir"])
	# print item.file_path + " " + filename
	item.url = item.file_path + currentConfig["version"]
	#查找上个版本该文件
	prevItem = getItemByFilename(prevArray, item.file_path )
	#如果上个版本的md5码跟当前不一致 则增加当前的版本号
	copyIncrementFileToResDirAndEncrypt(item)
	
def getPrevVersionFile():
	url = envConfig["url"]  + "versions_" + currentConfig["platform"] +  currentConfig["prevVersion"]
	try:
		f = urllib2.urlopen(url)
		prevArray.ParseFromString(f.read())
		f.close()
	except:
		url = "clientVersions.pb"
		print "download file from " + url + "  failed!"
		if os.path.exists(url):
			f = open(url, "rb")
			prevArray.ParseFromString(f.read())
			f.close()
		
def preProcessFiles(filename):
	if not isImageFile(filename):
		return	
	fmtname = getShortFileName(filename, currentConfig["rootDir"])
	if fmtname in pkeys:
		processImage(fileHash, filename,currentConfig["rootDir"])


def copyResToTmpDir():
	tmpDir = config["output"] + "/temp"
	if  os.path.exists(tmpDir):
		shutil.rmtree(config["output"] + "/temp")
	shutil.copytree(currentConfig["rootDir"],tmpDir)
	currentConfig["rootDir"] = tmpDir
	
def genBulletinFile():
	dict = {"title" :"",
	"content":"",
	"version": currentConfig["version"]}
	filepath = config["output"] + "/" + "bulletin_" + currentConfig["platform"] + ".txt"
	f = open(filepath,"wb") 
	f.write(json.dumps(dict).encode("utf-8"))
	f.close()
	zipFile.write(filepath, os.path.basename(filepath))
	print "zip file " + filepath 

def resetFilename():
	for item in fileList:
		if item.file_path.endswith("gl"):
			item.file_path = item.file_path[:-2]
	
def itemSort(x, y):
	extx = os.path.splitext(x.file_path)[-1]
	exty = os.path.splitext(y.file_path)[-1]
	sx = x.size
	sy = y.size
	if extx == exty:
		if sx > sy:
			return 1
		elif sx < sy:
			return -1
		else:
			return 0
	elif extx > exty:
		return 1
	else:
		return -1
		
def dumpUpdateInfo():
	global striptFileList
	if os.path.exists("striplist.txt"):
		f = open("striplist.txt")
		striptFileList = f.readlines()
		f.close()
	
	resetFilename()
	fileList.sort(cmp=itemSort)
	filepath = config["output"] + "/log.txt"
	totalSize = 0
	hdSize = 0
	ldSize = 0
	
	totalFiles = len(fileList)
	f = open(filepath,"wb") 
	prevVer = currentConfig["prevVersion"]
	verTxt = "%s from version %s update to version %s \n"%(currentConfig["platform"] , prevVer,currentConfig["version"] )
	f.write("-" * 100 + "\n")
	f.write(verTxt)
	f.write("-" * 100 + "|\n")
	f.write("%-70s|\t\t%-24s|\n"%("filename", "size"))
	# f.write("-" * 100 + "|\n")
	#上一个扩展名
	prevExt = ""
	extFiles = 0
	extSize = 0
	for item in fileList:
		if item.file_path.endswith(".lua") and item.file_path + "\n" not in  striptFileList:
			striptFileList.append(item.file_path + "\n")
		ext = os.path.splitext(item.file_path)[-1]
		if ext != prevExt  :
			if extFiles > 1:
				f.write("%d files, size is %s\n"%(extFiles, getSizeStr(extSize)))
			extSize = 0
			extFiles = 0
			prevExt = ext
			f.write("-" * 100 + "|\n")
			f.write(ext + " files\n")
		typeStr = "Added"
		prevItem = getItemByFilename(prevArray, item.file_path )
		if prevItem == None:
			prevItem = getItemByFilename(prevArray, item.file_path + "gl" )
		if prevItem != None:
			typeStr = "Modified"
		info = "%-70s|\t%-10s\t%-16s|\n"%(item.file_path, typeStr, getSizeStr(item.size))
		f.write(info)
		extSize = item.size + extSize
		extFiles = extFiles + 1
		totalSize = totalSize + item.size
		if "HD"  in item.file_path:
			hdSize = hdSize + item.size
		elif "LD"  in item.file_path:
			ldSize = ldSize + item.size
		else:
			ldSize = ldSize + item.size
			hdSize = hdSize + item.size
	if extFiles > 1:
		f.write("%d files, size is %s\n"%(extFiles, getSizeStr(extSize)))
	f.write("-" * 100 + "|\n")
	sizeTxt = "%d files need to update, totalSize is %s, hd size %s, ld size %s\n"%(totalFiles, getSizeStr(totalSize), getSizeStr(hdSize), getSizeStr(ldSize))
	f.write(sizeTxt)
	f.write("-" * 100 + "\n")
	f.close()
	shutil.copyfile(filepath, "./log.txt")
	f = open("striplist.txt", "w")
	f.writelines(striptFileList)
	f.close()
	
	
def run():
	newArray.Clear()
	getPrevVersionFile()
	print("getPrevVersionFile %d files" % (len(prevArray.items)))
	setGamesetting(currentConfig, envConfig)
	setLuaVersion(currentConfig)
	#将所有资源复制到临时目录
	copyResToTmpDir()
	#预处理文件
	# walk(currentConfig["rootDir"], preProcessFiles, config["exclude"])
	#生成文件hash列表
	writePlistFile(plist, currentConfig["rootDir"] + "/" + "hash.plist")
	#生成文件版本信息
	walk(currentConfig["rootDir"], genVersion, config["exclude"])
	
	#保存pb文件
	newArray.url = envConfig["url"] + "/" + currentConfig["platform"] + "/"
	newArray.version = currentConfig["version"]
	pbName = "versions_" + currentConfig["platform"] + currentConfig["version"]
	pbSavePath = config["output"] + pbName
	writeToPB(newArray, pbSavePath);
	zipFile.write(pbSavePath, pbName)
	#公告文件
	# genBulletinFile()
	shutil.rmtree(config["output"] + "/temp/")
	zipFile.close()
	
	dumpUpdateInfo()

config = loadConfig()


if isWindows():
	currentConfig = config["android"]
else:
	currentConfig = config["ios"]
envConfig = currentConfig[config["env"]]
	
config["output"] = config["output"]  +currentConfig["version"] + "/"	
if os.path.isdir(config["output"]):
	shutil.rmtree(config["output"])
	
os.makedirs(config["output"])
zipFile = zipfile.ZipFile(config["output"] + currentConfig["platform"] + '.zip','w',zipfile.ZIP_DEFLATED)
pkeys = readPlistFile(os.path.abspath("Hash.plist")).filenames

run()

print("success, total processed %d files" % (len(newArray.items)))

os.system("pause")