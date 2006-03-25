# Copyright (c) 2001 New Information Paradigms Ltd
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.
#

from Products.CMFCore.FSZSQLMethod import FSZSQLMethod
from Products.CMFCore.utils import expandpath
from Products.ZSQLMethods.SQL import SQL

def FSZSQLMethod_readFile(self, reparse):
    fp = expandpath(self._filepath)
    file = open(fp, 'r')    # not 'rb', as this is a text file!
    try:
        data = file.read()
    finally: file.close()

    RESPONSE = {}
    RESPONSE['BODY'] = data

    self.PUT(RESPONSE,None)


def FSZSQLMethod_createZODBClone(self):
    """Create a ZODB (editable) equivalent of this object."""
    # I guess it's bad to 'reach inside' ourselves like this,
    # but Z SQL Methods don't have accessor methdods ;-)
    s = SQL(self.id,
            self.title,
            self.connection_id,
            self.arguments_src,
            self.src)
    s.manage_advanced(self.max_rows_,
                      self.max_cache_,
                      self.cache_time_,
                      self.class_name_,
                      self.class_file_)
    return s

FSZSQLMethod._readFile = FSZSQLMethod_readFile
FSZSQLMethod._createZODBClone = FSZSQLMethod_createZODBClone
