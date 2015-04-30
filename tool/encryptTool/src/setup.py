#mysetup.py 
from distutils.core import setup 
import py2exe 
setup(console=[{"script":"encrypt.py", "icon_resources": [(1, "myicon.ico")]}],
    options = {"py2exe":{"bundle_files": 1 ,"compressed": 1, }},
    zipfile=None,   
    )