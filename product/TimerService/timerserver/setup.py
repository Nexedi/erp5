#!/usr/bin/env python
import sys
from distutils import util
from distutils.core import setup, Extension

from __pkginfo__ import modname, version, license, short_desc, long_desc,\
     web, author, author_email

if __name__ == '__main__' :
    dist = setup(name = modname,
                 version = version,
                 license =license,
                 description = short_desc,
                 long_description = long_desc,
                 author = author,
                 author_email = author_email,
                 url = web,
                 package_dir = {modname: '.'},
                 packages = [modname,],
		 data_files = [
		   ('./lib/python%s.%s/site-packages/%s'%(sys.version_info[0], sys.version_info[1], modname), 
		   ['component.xml'])]
                 )
