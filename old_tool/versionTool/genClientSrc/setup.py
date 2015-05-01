#mysetup.py 
from distutils.core import setup 
import py2exe 
setup(console=[{"script":"genClientVersions.py", "icon_resources": [(1, "myicon.ico")]}],
		app=["genClientVersions.py"],
    options = {"py2exe":{"bundle_files": 1 ,"compressed": 1, }},
    zipfile=None,   
    )