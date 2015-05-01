# -*- coding: utf-8 -*

import sys, os, getopt
import urllib2
import string

os.chdir(sys.path[0])
sys.path.insert(0, "../")

from utils import *
tool.chDirToExecPath()


url = ""
outputDir = "../../resources"



def run():
    try:
        f = urllib2.urlopen(url)
        filename = url.split("/")[-1]
        print "filename is " + filename
        strCode = f.read()
        newCode  = int(strCode) + 1
        print "prev Code is " + strCode
        f.close()

        f = open(outputDir + "/" + filename ,"wb")
        try:
            f.write(str(newCode))
        except:
            print "write " + filename + "  failed!"
        finally:
            f.close()
    except:
        print "download file from " + url + "  failed!"


def usage():
    print "-u:  prev code url"
    print "-o:  output directory"


opts, args = getopt.getopt(sys.argv[1:], "hu:o:")
for op, value in opts:
    if op == "-u":
        inputDir = value
    elif op == "-o":
        outputDir = value
    elif op == "-h":
        usage()
        sys.exit()

run()


sys.exit(0)
#os.system("pause")
