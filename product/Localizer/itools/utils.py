# -*- coding: utf-8 -*-
# Copyright (C) 2006-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2008 Gautier Hayoun <gautier.hayoun@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the Standard Library
from distutils import core
from distutils.errors import DistutilsOptionError
from distutils.command.build_py import build_py
from distutils.command.register import register
from distutils.command.upload import upload
from getpass import getpass
from mimetypes import MimeTypes
from os import getcwd, open as os_open, devnull, dup2, O_RDWR
from os.path import exists, join as join_path, sep, splitdrive
from re import search
from sys import _getframe, platform, exit, stdin, stdout, stderr
from urllib2 import HTTPPasswordMgr
import sys

def get_abspath(local_path, mname=None):
    """Returns the absolute path to the required file.
    """
    if mname is None:
        mname = _getframe(1).f_globals.get('__name__')

    if mname == '__main__' or mname == '__init__':
        mpath = getcwd()
    else:
        module = sys.modules[mname]
        if hasattr(module, '__path__'):
            mpath = module.__path__[0]
        elif '.' in mname:
            mpath = sys.modules[mname[:mname.rfind('.')]].__path__[0]
        else:
            mpath = mname

    drive, mpath = splitdrive(mpath)
    mpath = drive + join_path(mpath, local_path)

    # Make it working with Windows. Internally we use always the "/".
    if sep == '\\':
        mpath = mpath.replace(sep, '/')

    return mpath
