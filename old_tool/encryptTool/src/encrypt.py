# -*- coding: gbk -*
import os.path
import json
import sys, os, stat
import struct
import string       
import base64                        

path=sys.argv[0][0:sys.argv[0].rfind(os.sep)+1]
sys.path.insert(0,path + "../../utils")
from tool import *
chDirToExecPath()
import xxtea


config = None
choice = 1
key = "518060fm"

def isEncryptFile(bytes):
    codeLen = len(config["code"])
    if len(bytes) < codeLen :
      return False
    ret = bytes[:codeLen]== config["code"].encode('utf-8')
    return ret

def swapList(list, left, right, ilen):
	if len(list) < right + ilen :
		return list
	leftpart = list[:left]
	rightpart = list[right + ilen:]
	list = leftpart + list[right: right + ilen] + list[left + ilen : right] + list[left:left + ilen] + rightpart
	return list

def decryptBytes(bytes):
	totalLen = len(bytes)
	leftIdx = 0
	while True:
		rightIdx = 10 ** (leftIdx + 2) - 10
		if rightIdx + 10 > totalLen:
			break
		bytes = swapList(bytes, leftIdx*10, rightIdx, 10)
		leftIdx += 1	
	return bytes

def encryptFile(file):
        f=open(file,'rb')  
        bytes = f.read()
        f.close()

        if isEncryptFile(bytes):
        	return
		print "encrypt  " + file
        f=open(file,'wb')  
        #WRITE 8 BIT AT FRONT
        f.write(config["code"])
        bytes = decryptBytes(bytes)
        f.write(bytes)
        f.close()
        return

def decryptFile(file):
	f=open(file,'rb')  
	bytes = f.read()
	f.close()
	
	if not isEncryptFile(bytes):
		return
		
	print "decrypt  " + file
	f=open(file,'wb')  
	bytes = bytes[6:]
	
	bytes = decryptBytes(bytes)
	f.write(bytes)
	f.close()
	return

def XXTEAencrypt(filename):
	filename = os.path.abspath(filename)
	# print os.getcwd()
	os.system("set  CYGWIN=nodosfilewarning  && cd xxtea && " + getExecPrefix() + "xxtea 1 " + filename + " " + key)

def XXTEAdecrypt(filename):
	filename = os.path.abspath(filename)
	os.system("set  CYGWIN=nodosfilewarning  && cd xxtea && " + getExecPrefix() + "xxtea 2 " + filename + " " + key)

def walkFunc(path):
	# return
	# print "walk  " + path
	if choice == 1:
		if isFileNeedEncrypt(path):
			if isLuaFile(path):
				XXTEAencrypt(path)
			else:
				encryptFile(path)

	else:
		if isFileNeedEncrypt(path):
			if isLuaFile(path):
				print "descrypt " + path
				XXTEAdecrypt(path)
			else:
				decryptFile(path)
			

config = loadConfig()
if len(sys.argv) > 1:
	choice = string.atoi(sys.argv[1])
else:
    choice = input("please choose 1: encrypt  else:decrypt ")  

dirs = sys.argv[2:]
if len(dirs) > 0:
    config["dirs"] = dirs

for path in config["dirs"]:
    if os.path.isdir(path):
        walk(path, walkFunc)
    else:
        walkFunc(path)

# print "success!"
sys.exit(0)
