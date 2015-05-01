# -*- coding: utf-8 -*

import sys, os, getopt

os.chdir(sys.path[0])
sys.path.insert(0, "../")

import fileversions_pb2
from utils import *
tool.chDirToExecPath()

pbList = fileversions_pb2.file_item_array()
config = tool.loadConfig()
inputDir = "../../resources"
outputDir = "../../resources"


	
#生成一个版本item
def genVersion(filename):
    item = pbList.items.add()
    item.file_path = tool.formatFileName(filename,inputDir)
    print item.file_path
    item.md5 = tool.get_md5_value(filename)
    item.size = os.path.getsize(filename)


def run():
    pbList.Clear()
    print "running" + inputDir
    tool.walk(inputDir, genVersion, config["exclude"])
    tool.writeToPB(pbList, outputDir + "/" + "clientVersions.pb");

def usage():
    print "-i:  input directory"
    print "-o:  output directory"


opts, args = getopt.getopt(sys.argv[1:], "hi:o:")
for op, value in opts:
    if op == "-i":
        inputDir = value
    elif op == "-o":
        outputDir = value
    elif op == "-h":
        usage()
        sys.exit()

run()

print("success, total processed %d files" % (len(pbList.items)))

sys.exit(0)
#os.system("pause")
