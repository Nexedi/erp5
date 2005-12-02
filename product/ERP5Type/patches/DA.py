##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# XML content of zsql methods
import re
try: from IOBTree import Bucket
except: Bucket=lambda:{}
from Shared.DC.ZRDB.Aqueduct import decodestring, parse
from Shared.DC.ZRDB.DA import DA

def DA_fromFile(self, filename):
  """
    Read the file and update self
  """
  f = file(filename)
  s = f.read()
  f.close()
  self.fromText(s)

def DA_fromText(self, text):
  """
    Read the string 'text' and updates self
  """
  start = text.find('<dtml-comment>')
  end = text.find('</dtml-comment>')
  block = text[start+14:end]
  parameters = {}
  for line in block.split('\n'):
    pair = line.split(':',1)
    if len(pair)!=2:
      continue
    parameters[pair[0].strip().lower()]=pair[1].strip()
  # check for required and optional parameters
  max_rows = parameters.get('max_rows',1000)
  max_cache = parameters.get('max_cache',100)
  cache_time = parameters.get('cache_time',0)
  class_name = parameters.get('class_name','')
  class_file = parameters.get('class_file','')
  title = parameters.get('title','')
  connection_id = parameters.get('connection_id','')
  arguments = parameters.get('arguments','')
  start = text.rfind('<params>')
  end = text.rfind('</params>')
  arguments = text[start+8:end]
  template = text[end+9:]
  while template.find('\n')==0:
    template=template.replace('\n','',1)
  self.manage_edit(title=title, connection_id=connection_id,
                  arguments=arguments, template=template)
  self.manage_advanced(max_rows, max_cache, cache_time, class_name, class_file)

def DA_manage_FTPget(self):
    """Get source for FTP download"""
    self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')
    return """<dtml-comment>
title:%s
connection_id:%s
max_rows:%s
max_cache:%s
cache_time:%s
class_name:%s
class_file:%s
</dtml-comment>
<params>%s</params>
%s""" % (self.title, self.connection_id,
         self.max_rows_, self.max_cache_, self.cache_time_,
         self.class_name_, self.class_file_,
         self.arguments_src, self.src)

# This function doesn't take care about properties by default
def DA_PUT(self, REQUEST, RESPONSE):
    """Handle put requests"""
    if RESPONSE is not None: self.dav__init(REQUEST, RESPONSE)
    if RESPONSE is not None: self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
    body = REQUEST.get('BODY', '')
    m = re.match('\s*<dtml-comment>(.*?)</dtml-comment>\s*\n', body, re.I | re.S)
    if m:
        property_src = m.group(1)
        parameters = {}
        for line in property_src.split('\n'):
          pair = line.split(':',1)
          if len(pair)!=2:
            continue
          parameters[pair[0].strip().lower()]=pair[1].strip()
        # check for required and optional parameters
        max_rows = parameters.get('max_rows',1000)
        max_cache = parameters.get('max_cache',100)
        cache_time = parameters.get('cache_time',0)
        class_name = parameters.get('class_name','')
        class_file = parameters.get('class_file','')
        title = parameters.get('title','')
        connection_id = parameters.get('connection_id','')
        self.manage_advanced(max_rows, max_cache, cache_time, class_name, class_file)
        self.title = str(title)
        self.connection_id = str(connection_id)
        body = body[m.end():]
    m = re.match('\s*<params>(.*)</params>\s*\n', body, re.I | re.S)
    if m:
        self.arguments_src = m.group(1)
        self._arg=parse(self.arguments_src)
        body = body[m.end():]
    template = body
    self.src = template
    self.template=t=self.template_class(template)
    t.cook()
    self._v_cache={}, Bucket()
    if RESPONSE is not None: RESPONSE.setStatus(204)
    return RESPONSE


DA.fromFile = DA_fromFile
DA.fromText = DA_fromText
DA.manage_FTPget = DA_manage_FTPget
DA.PUT = DA_PUT
