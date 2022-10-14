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
from Shared.DC.ZRDB.DA import DA, DatabaseError, SQLMethodTracebackSupplement
from Shared.DC.ZRDB import RDB
from Shared.DC.ZRDB.Results import Results
try: # BBB Zope 2.12
  from App.Extensions import getBrain
except ImportError:
  from Shared.DC.ZRDB.DA import getBrain
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.ERP5Type.Globals import InitializeClass
from Acquisition import aq_base, aq_parent
from zLOG import LOG, INFO, ERROR
from io import BytesIO
from Products.ERP5Type import Permissions
import six

security = ClassSecurityInfo()
DA.security = security

def DA_fromFile(self, filename):
  """
    Read the file and update self
  """
  f = open(filename)
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


def DA__call__(self, REQUEST=None, __ick__=None, src__=0, test__=0, **kw):
    """Call the database method

    The arguments to the method should be passed via keyword
    arguments, or in a single mapping object. If no arguments are
    given, and if the method was invoked through the Web, then the
    method will try to acquire and use the Web REQUEST object as
    the argument mapping.

    The returned value is a sequence of record objects.
    """
    __traceback_supplement__ = (SQLMethodTracebackSupplement, self)

    c = kw.pop("connection_id", None)
    #if c is not None:
      #LOG("DA", 300, "connection %s provided to %s" %(c, self.id))
    # patch: dynamic brain configuration
    zsql_brain = kw.pop('zsql_brain', None)
    # patch end


    if REQUEST is None:
        if kw: REQUEST=kw
        else:
            if hasattr(self, 'REQUEST'): REQUEST=self.REQUEST
            else: REQUEST={}

    # Patch to implement dynamic connection id
    # Connection id is retrieve from user preference
    if c is None:
      # XXX cleaner solution will be needed
      if not (self.connection_id in ('cmf_activity_sql_connection',
                                     'erp5_sql_transactionless_connection')
              or 'portal_catalog' in self.getPhysicalPath()):
        portal = self.getPortalObject()
        if 'portal_archives' in portal.__dict__:
          archive_id = portal.portal_preferences.getPreferredArchive()
          if archive_id:
            archive_id = archive_id.split('/')[-1]
            #LOG("DA__call__, archive_id 2", 300, archive_id)
            archive = portal.portal_archives._getOb(archive_id, None)
            if archive is not None:
              c = archive.getConnectionId()
              #LOG("DA call", INFO, "retrieved connection %s from preference" %(c,))

    if c is None:
      # connection hook
      c = self.connection_id
      # for backwards compatability
      hk = self.connection_hook
      # go get the connection hook and call it
      if hk: c = getattr(self, hk)()
    #LOG("DA__call__ connection", 300, c)
    try: dbc=getattr(self, c)
    except AttributeError:
        raise AttributeError(
            "The database connection <em>%s</em> cannot be found." % (
            c))

    try: DB__=dbc()
    except: raise DatabaseError(
        '%s is not connected to a database' % self.id)

    p = aq_parent(self) # None if no aq_parent

    argdata=self._argdata(REQUEST)
    argdata['sql_delimiter']='\0'
    argdata['sql_quote__']=dbc.sql_quote__

    security=getSecurityManager()
    security.addContext(self)
    try:
        query = self.template(p, **argdata)
    except TypeError as msg:
        msg = str(msg)
        if 'client' in msg:
            raise NameError("'client' may not be used as an "
                    "argument name in this context")
        raise
    finally:
        security.removeContext(self)

    if src__: return query

    if self.cache_time_ > 0 and self.max_cache_ > 0:
        result=self._cached_result(DB__, str2bytes(query), self.max_rows_, c)
    else:
      try:
        result=DB__.query(query, self.max_rows_)
      except:
        LOG("DA call raise", ERROR, "DB = %s, c = %s, query = %s" %(DB__, c, query), error=True)
        raise

    # patch: dynamic brain configuration
    if zsql_brain is not None:
        try:
          class_file_, class_name_ = zsql_brain.rsplit('.', 1)
        except:
          #import pdb; pdb.post_mortem()
          raise
        brain = getBrain(class_file_, class_name_)
        # XXX remove this logging for performance
        LOG(__name__, INFO, "Using special brain: %r\n" % (brain,))
    else:
        brain = getBrain(self.class_file_, self.class_name_)

    if type(result) is type(''):
        f=BytesIO()
        f.write(result)
        f.seek(0)
        result=RDB.File(f,brain,p)
    else:
        result=Results(result, brain, p)
    columns=result._searchable_result_columns()
    if test__ and columns != self._col: self._col=columns

    # If run in test mode, return both the query and results so
    # that the template doesn't have to be rendered twice!
    if test__: return query, result

    return result

def DA_upgradeSchema(self, connection_id=None, create_if_not_exists=False,
                           initialize=None, src__=0, **kw):
    return self.getPortalObject()[connection_id or self.connection_id]() \
        .upgradeSchema(self(src__=1, **kw), create_if_not_exists,
                       initialize, src__)

DA.__call__ = DA__call__
security.declarePrivate('fromFile')
DA.fromFile = DA_fromFile
security.declarePrivate('fromText')
DA.fromText = DA_fromText
DA.manage_FTPget = DA_manage_FTPget
DA.PUT = DA_PUT
DA._upgradeSchema = DA_upgradeSchema


# Patch to allow using ZODB components for brains
def getObjectMeta(original_function):
  def getObject(module, name, reload=0):
    # Modified version that ignore errors as long as the module can be be
    # imported, which is enough to use a ZODB Extension as a brain.
    try:
      m = __import__('erp5.component.extension.%s' % module, globals(),
                     {}, ['erp5.component.extension'] if six.PY2 else ['erp5'])

      o = getattr(m, name, None)
      if o is None:
        raise ImportError(
          "Cannot get %s from erp5.component.extension.%s" % (name, module))

      return o
    except ImportError:
      return original_function(module, name, reload=reload)

  return getObject

# This get Object exists both in App.Extensions.getObject and Shared.DC.ZRDB.DA
# for some versions of Zope/Products.ZSQLMethods, so we try to patch both if
# they exist
import Shared.DC.ZRDB.DA
if hasattr(Shared.DC.ZRDB.DA, 'getObject'):
  Shared.DC.ZRDB.DA.getObject = getObjectMeta(Shared.DC.ZRDB.DA.getObject)

import App.Extensions
App.Extensions.getObject = getObjectMeta(App.Extensions.getObject)
InitializeClass(DA)
