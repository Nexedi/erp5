##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

"""Utility functions and classes for unit testing
"""
import errno
import os
import logging
import random
import socket
import sys
import transaction
import ZODB
import zLOG
from App.config import getConfiguration
from ZConfig.matcher import SectionValue
from Zope2.Startup.datatypes import ZopeDatabase
import Products.ERP5Type
from Products.MailHost.MailHost import MailHost
from email import message_from_string
import backportUnittest
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.Utils import simple_decorator
from Products.ZSQLCatalog.SQLCatalog import Catalog

class FileUpload(file):
  """Act as an uploaded file.
  """
  __allow_access_to_unprotected_subobjects__ = 1
  def __init__(self, path, name):
    self.filename = name
    file.__init__(self, path)
    self.headers = {}

# dummy objects
class DummyMailHostMixin(object):
  """Dummy Mail Host that doesn't really send messages and keep a copy in
  _last_message attribute.
  """
  _last_message = ()
  _previous_message = ()
  _message_list = []

  @classmethod
  def _send(cls, mfrom, mto, messageText, immediate=False):
    """Record message in _last_message."""
    cls._previous_message = cls._last_message
    cls._last_message = (mfrom, mto, messageText)
    cls._message_list.append(cls._last_message)

  @staticmethod
  def _decodeMessage(messageText):
    """ Decode message"""
    message_text = messageText
    for part in message_from_string(messageText).walk():
      if part.get_content_type() in ['text/plain', 'text/html' ] \
                  and not part.is_multipart():
        message_text = part.get_payload(decode=1)
    return message_text

  @classmethod
  def getMessageList(cls, decode=True):
    """ Return message list"""
    if decode:
      return [(m[0], m[1], cls._decodeMessage(m[2])) for m in cls._message_list]
    return cls._message_list

  @classmethod
  def getLastLog(cls):
    """ Return last message """
    return cls._last_message

  @classmethod
  def reset(cls):
    cls._last_message = ()
    cls._previous_message = ()
    cls._message_list = []

class DummyMailHost(DummyMailHostMixin, MailHost):
  pass


class DummyTranslationService:
  """A dummy translation service where you can access translated msgids and
  mappings in _translated.
  """
  _translated = {}
  def translate(self, domain, msgid, mapping=None, *args, **kw):
    self._translated.setdefault(domain, []).append((msgid, mapping))
    return msgid

class DummyMessageCatalog:
  __allow_access_to_unprotected_subobjects__ = 1
  def __init__(self):
    self._translated = []
  def gettext(self, word, lang=None, add=1, default=None, **kw):
    self._translated.append(word)
    if default is None:
      return word
    else:
      return default
  def translate(self, msgid, mapping=None, context=None,
                target_language=None, default=None):
    return default

class DummyLocalizer:
  """A replacement for stock cookie - based localizer.

  You can change the current language by calling 'changeLanguage'
  You can access the translated messages in _translated attribute from erp5_ui
  and erp5_content message catalogs. It's a list.
  """
  __allow_access_to_unprotected_subobjects__ = 1
  def __init__(self):
    self.erp5_ui = self.ui = DummyMessageCatalog()
    self.erp5_content = self.content = DummyMessageCatalog()
    self.default = DummyMessageCatalog()
    self.lang = 'en'

  def __getitem__(self, key):
    if hasattr(self, key):
      return getattr(self, key)
    raise KeyError, key

  def get_selected_language(self):
    return self.lang
  
  def get_languages_map(self):
    return [{'selected': True, 'id': 'en', 'title': 'English'},
            {'selected': False, 'id': 'pl', 'title': 'Polish'},
            {'selected': False, 'id': 'fr', 'title': 'French'},]

  def get_supported_languages(self):
    return ('en', 'fr', 'pl')

  get_languages = get_supported_languages

  def changeLanguage(self, lang):
    self.lang = lang

  def translate(self, domain, msgid, lang=None, mapping=None, *args, **kw):
    params = dict()
    for key in ('lang', 'add', 'default'):
      if key in kw:
        params[key] = kw[key]
    if lang is not None:
      params['lang'] = lang
    if 'target_language' in kw:
      params['lang'] = kw['target_language']
    msg = getattr(self, domain, self.default).gettext(msgid, **params)
    if mapping:
      # this is a simpler version that does not handle unicode
      from string import Template
      return Template(msg).substitute(mapping)
    return msg
  
  def __call__(self, request, context):
    # the before traverse hook
    pass


# python scripts
def createZODBPythonScript(container, script_id, script_params,
                           script_content):
  """Creates a Python script `script_id` in the given `container`, with
  `script_params` and `script_content`.
  
  If the container already contains an object with id `script_id`, this
  object is removed first.
  """
  if script_id in container.objectIds():
    container.manage_delObjects([script_id])

  container.manage_addProduct['PythonScripts']\
                .manage_addPythonScript(id = script_id)
  script = container._getOb(script_id)
  script.ZPythonScript_edit(script_params, script_content)
  container.portal_url.getPortalObject().changeSkin(None)
  return script

def removeZODBPythonScript(container, script_id):
  """
  Removes a Python script `script_id` in the given `container`.
  """
  container.manage_delObjects([script_id])

# class tool
def installRealClassTool(portal):
  """Replaces portal_classes by a real class tool object.
  """
  Products.ERP5Type.allowClassTool = lambda: 1
  _recreateClassTool(portal)

def installDummyClassTool(portal):
  """Replaces portal_classes by a dummy class tool object.
  """
  Products.ERP5Type.allowClassTool = lambda: 0
  _recreateClassTool(portal)

def _recreateClassTool(portal):
  """Recreate the class tool for this portal.
  """
  from Products.ERP5Type.Tool import ClassTool
  reload(ClassTool)
  portal.manage_delObjects(['portal_classes'])
  portal._setObject('portal_classes', ClassTool.ClassTool())

# memcache tool
def installRealMemcachedTool(portal):
  """Replaces portal_memcached by a real memcached tool object.
  """
  _recreateMemcachedTool(portal)

def _recreateMemcachedTool(portal):
  """Recreate the memcached tool for this portal.
  """
  from Products.ERP5Type.Tool import MemcachedTool
  reload(MemcachedTool)
  portal.manage_delObjects(['portal_memcached'])
  portal.newContent(id='portal_memcached', portal_type="Memcached Tool")

# test runner shared functions
def getMySQLArguments():
  """Returns arguments to pass to mysql by heuristically converting the
  connection string.
  """
  connection_string = os.environ.get('erp5_sql_connection_string')
  if not connection_string:
    return '-u test test'

  password = ''
  host = ''
  db, user = connection_string.split(' ', 1)

  sock = ''
  if ' ' in user: # look for user password
    sp = user.split()
    if len(sp) == 2:
      user, password = sp
    elif len(sp) == 3:
      user, password, sock = sp
      sock = '--socket=%s' % sock
    password = '-p%s' % password

  if "@" in db: # look for hostname
    db, host = db.split('@')
    if ":" in host: # look for port
      host, port = host.split(':')
      host = '-h %s -P %s' % (host, port)
    else:
      host = '-h %s' % host

  return '-u %s %s %s %s %s' % (user, password, host, db, sock)

def getExtraSqlConnectionStringList():
  """Return list of extra available SQL connection string
  """
  return os.environ.get('extra_sql_connection_string_list',
                        'test2 test2,test3 test3').split(',')

instance_random = random.Random(hash(os.environ['INSTANCE_HOME']))

def parseListeningAddress(host_port=None, default_host='127.0.0.1'):
  """Parse string specifying the address to bind to

  If the specified address is incomplete or missing, several (host, random_port)
  will be returned. It must be used as follows (an appropriate error is raised
  if all returned values failed):

    for host, port in parseListeningAddress(os.environ.get('some_address')):
      try:
        s.bind((host, port))
        break
      except socket.error, e:
        if e[0] != errno.EADDRINUSE:
          raise
  """
  if host_port:
    host_port = host_port.rsplit(':', 1)
    if len(host_port) == 1:
      host_port = default_host, host_port[0]
    try:
      yield host_port[0], int(host_port[1])
      raise RuntimeError("Can't bind to %s:%s" % host_port)
    except ValueError:
      default_host = host_port[1]
  port_list = []
  for i in xrange(3):
    port_list.append(instance_random.randint(55000, 55500))
    yield default_host, port_list[-1]
  raise RuntimeError("Can't find free port (tried ports %s)\n"
                     % ', '.join(map(str, port_list)))

def createZServer(log=os.devnull, zserver_type='http'):
  import ZServer
  if zserver_type == 'http':
    zserver_class, zhandler_class = ZServer.zhttp_server, ZServer.zhttp_handler
  elif zserver_type == 'webdav':
    from ZServer.HTTPServer import zwebdav_server as zserver_class
    from ZServer.WebDAVSrcHandler import WebDAVSrcHandler as zhandler_class
  else:
    raise NotImplementedError
  lg = ZServer.logger.file_logger(log)
  class new_zserver(zserver_class):
    # I can't use __new__ because zhttp_handler is an old-style class :(
    def __init__(self):
      self.__class__, = self.__class__.__bases__
  for ip, port in parseListeningAddress(os.environ.get('zserver')):
    hs = new_zserver()
    try:
      hs.__init__(ip, port, resolver=None, logger_object=lg)
      hs.install_handler(zhandler_class(module='Zope2', uri_base=''))
      return hs
    except socket.error, e:
      if e[0] != errno.EADDRINUSE:
        raise
      hs.close()

class DbFactory(ZopeDatabase):

  def __init__(self, name, storage=None, **kw):
    ZopeDatabase.__init__(self, SectionValue({'container_class': None,
                                              'mount_points': [],
                                             }, name, None))
    if storage is not None:
      self.open = lambda database_name, databases: ZODB.DB(storage,
        database_name=database_name, databases=databases, **kw)
    getConfiguration().dbtab.db_factories[name] = self

  @staticmethod
  def get(*args, **kw):
    return getConfiguration().dbtab.getDatabaseFactory(*args, **kw)

  def addMountPoint(self, *mount_points):
    dbtab = getConfiguration().dbtab
    self.config.mount_points += mount_points
    for mount_point in self.getVirtualMountPaths():
      dbtab.mount_paths[mount_point] = self.name

  def close(self):
    dbtab = getConfiguration().dbtab
    for mount_point in self.getVirtualMountPaths():
      del dbtab.mount_paths[mount_point]
    del dbtab.db_factories[self.name]
    dbtab.databases.pop(self.name).close()

# decorators
@simple_decorator
def reindex(func):
  """Decorator to commit transaction and flush activities after the method is
  called.
  """
  def wrapper(self, *args, **kw):
    ret = func(self, *args, **kw)
    if kw.get('reindex', 1):
      transaction.commit()
      self.tic()
    return ret
  return wrapper

# Use this as a method or class decorator to tag it as TODO.
# The test will be skipped:
#  - the fixture itself is not run
#  - if a TODO test is in fact successful, no one will ever know
#
# Test cases using this decorator must extend backportUnittest.TestCase
todo_erp5 = backportUnittest.skip("TODO ERP5")

class LogInterceptor:
    '''Replacement for Products.CMFCore.tests.base.testcase.LogInterceptor

    On CMF 1, LogInterceptor would bail if a log record with too high
    severity would pass through, and it would monkey-patch zLOG.log_write to do
    its job, meaning it would take on all Zope messages.
    
    The CMF 2 LogInterceptor plugs itself as a filter on the requested logger
    (the root logger, by default), which meant it would only be called on
    log records at that exact subsystem (not lower subsystems), and it no
    longer raises AssertionError on messages with high severity.
    
    This replacement restore the original semantics while keeping close to the
    new implementation, so it can act on both "zLOG" and "logging" calls.
    '''
    logged = None
    installed = ()
    level = 0

    def _zLOGLSeverityToLoggingLevel(self, severity):
        '''Given a zLOG severity, return a logging level
        '''
        # inspired by zLOG.EventLogger.log_write
        from zLOG.EventLogger import zlog_to_pep282_severity_cache_get
        from zLOG.EventLogger import zlog_to_pep282_severity
        level = (zlog_to_pep282_severity_cache_get(severity) or
                 zlog_to_pep282_severity(severity))
        return level

    def _catch_log_errors(self, ignored_level=zLOG.WARNING, subsystem=''):
        if subsystem in self.installed:
            raise ValueError, 'Already installed filter!'

        root_logger = logging.getLogger(subsystem)
        self.installed += (subsystem,)
        self.level = self._zLOGLSeverityToLoggingLevel(ignored_level)
        # attach to a handler instead of a logger, since logger filters are
        # not always called. See http://bugs.python.org/issue7535
        for handler in root_logger.handlers:
          handler.addFilter(self)
          break
        else:
          raise ValueError('No handlers to attach in logging subsystem %r' %
                           subsystem or 'root')

    def filter(self, record):
        if record.levelno > self.level:
            raise AssertionError("%s(%s): %s" % 
                                 (record.name,
                                  record.levelname,
                                  record.getMessage()))
        if self.logged is None:
            self.logged = []
        self.logged.append(record)
        return True

    def _ignore_log_errors(self, subsystem=''):

        if subsystem not in self.installed:
            return

        root_logger = logging.getLogger(subsystem)
        for handler in root_logger.handlers:
            handler.removeFilter(self)
        self.installed = tuple([s for s in self.installed if s != subsystem])

def to_utf8(text):
  """ Converts string to utf-8 if string is unicode """
  # BACK: The users of this function are probably reading the result of
  # PageTemplate rendering, which is unicode in Zope 2.12, but string in Zope
  # 2.8. When support for Zope 2.8 is dropped, rewrite the tests to assume
  # the rendering is unicode and deal with it appropriately.
  if isinstance(text, unicode):
    text = text.encode('utf-8')
  return text

def updateCellList(portal, line, cell_type, cell_range_method, cell_dict_list):
  """A matrixbox-like helper function to create cells at once.

    dicts in cell_dict_list can have following keys:
     - base_id
     - cell_range_kw
     - mapped_value_argument_list
     - table
     - variation_category_list_and_mapped_value_list (optional)

    Example:
      updateCellList(sale_order_line_1_1,
                     'Sale Order Cell',
                     'DeliveryLine_asCellRange',
                     ({'base_id':'movement',
                       'mapped_value_argument_list':('quantity',),
                       'table':(('product_packing/package', 1),
                                ('product_packing/case'   , 1),
                               )
                       },
                      )
                     )
    # Table structure examples
    one_dimension = (
      (line, mapped_value),
      (line, mapped_value),
      )
    two_dimension = (
      (        column,         column,),
      (line,   mapped_value,   mapped_value,),
      (line,   mapped_value,   mapped_value,),
      )
    three_dimension = (
      ((tab,),
      (        column,         column,),
      (line,   mapped_value,   mapped_value,),
      (line,   mapped_value,   mapped_value,),
      ),
      ((tab,),
      (        column,         column,),
      (line,   mapped_value,   mapped_value,),
      (line,   mapped_value,   mapped_value,),
      )
      )
    four_dimension = (
      ((tab,tab),
      (        column,         column,),
      (line,   mapped_value,   mapped_value,),
      (line,   mapped_value,   mapped_value,),
      ),
      ((tab,tab),
      (        column,         column,),
      (line,   mapped_value,   mapped_value,),
      (line,   mapped_value,   mapped_value,),
      )
      )

    Also you can pass variation_category_list_and_mapped_value_list. Then you do not
    have touse above table structure. variation_category_list_and_mapped_value_list
    structure should be like following:
      ((variation_category_list, mapped_value),
       (variation_category_list, mapped_value),
       (variation_category_list, mapped_value),)
  """
  def get_range_id_list(range_list):
    if not range_list:
      return []
    if len(range_list[0])>1:
      return [item[0] for item in range_list]
    else:
      return range_list

  def getSortedCategoryList(line, base_id, category_list):
    category_dict = {}
    for category in category_list:
      category_dict[category.split('/')[0]] = category
    result = []
    index_list = line.index[base_id].keys()
    index_list.sort()
    for index in index_list:
      if line.index[base_id][index]:
        base_category = line.index[base_id][index].keys()[0].split('/')[0]
        result.append(category_dict[base_category])
    return result
    
  for cell_dict in cell_dict_list:
    base_id = cell_dict['base_id']
    if callable(cell_range_method):
      cell_range_list = cell_range_method()
    else:
      cell_range_list = getattr(line, cell_range_method)(
        matrixbox=True,
        base_id=base_id,
        **cell_dict.get('cell_range_kw', {}))
    line.setCellRange(base_id=base_id,
                      *[get_range_id_list(cell_range)
                        for cell_range in cell_range_list]
                      )

    mapped_value_argument_list = cell_dict['mapped_value_argument_list']
    def getMappedValueDict(item):
      if len(mapped_value_argument_list)==1:
        return {mapped_value_argument_list[0]:item}
      else:
        result = {}
        for index, argument_name in enumerate(mapped_value_argument_list):
          result[argument_name] = item[index]
        return result

    data_list = []
    if cell_dict.get('variation_category_list_and_mapped_value_list'):
      for variation_category_list, mapped_value in cell_dict.get('variation_category_list_and_mapped_value_list'):
        data_list.append((variation_category_list, getMappedValueDict(mapped_value)))
    else:
      # verify table structure to know dimension.
      table = cell_dict['table']
      if len([True for item in table if len(item)!=2])==0:
        dimension = 1
      elif len(table)>1 and (len(table[0])+1)==len(table[1]):
        dimension = 2
      elif isinstance(table[0][0], (tuple, list)):
        dimension = 3
      else:
        raise RuntimeError, "Unsupported table structure!"

      if dimension==1:
        for table_line in table:
          data_list.append(([table_line[0]], getMappedValueDict(table_line[1])))
      elif dimension==2:
        column = table[0]
        for table_line in table[1:]:
          row = table_line[0]
          for index, item in enumerate(table_line[1:]):
            data_list.append(([row, column[index]], getMappedValueDict(item)))
      elif dimension==3:
        table_list = table
        for table in table_list:
          tab_list = list(table[0])
          tab_list.reverse()
          column = table[1]
          for table_line in table[2:]:
            row = table_line[0]
            for index, item in enumerate(table_line[1:]):
              data_list.append(([row, column[index]] + tab_list, getMappedValueDict(item)))

    for category_list, mapped_value_dict in data_list:
      category_list = getSortedCategoryList(line, base_id, category_list)
      cell = line.newCell(portal_type=cell_type,
                          base_id=base_id,
                          *category_list)

      cell.edit(**mapped_value_dict)
      cell.setMappedValuePropertyList(mapped_value_dict.keys())

      base_category_list = [category_path
                            for category_path in category_list
                            if (category_path.split('/')[0] in
                                portal.portal_categories.objectIds())
                            ]

      cell.setMembershipCriterionBaseCategoryList(base_category_list)
      membership_criterion_category_list = [
        category_path
        for category_path in category_list
        if category_path.split('/')[0] in base_category_list]
      cell.setMembershipCriterionCategoryList(membership_criterion_category_list)
      cell.edit(predicate_category_list=category_list,
                variation_category_list=category_list)

def catalogObjectListWrapper(self, object_list, method_id_list=None,
    disable_cache=0, check_uid=1, idxs=None):
  """Wrapper to mark inside of portal object list of catalogged objects"""
  import transaction
  portal = self.getPortalObject()
  for q in object_list:
    portal.catalogged_object_path_dict[q.getPath()] = 1
  transaction.commit()

class SubcontentReindexingWrapper(object):
  def wrap_catalogObjectList(self):
    self.original_catalogObjectList = Catalog.catalogObjectList
    Catalog.catalogObjectList = catalogObjectListWrapper

  def unwrap_catalogObjectList(self):
    Catalog.catalogObjectList = self.original_catalogObjectList

  def _testSubContentReindexing(self, parent_document, children_document_list):
    """Helper method which shall be called *before* tic or commit"""
    # cleanup existing reindexing
    transaction.commit()
    self.tic()
    parent_document.reindexObject()
    self.portal.catalogged_object_path_dict = PersistentMapping()
    transaction.commit()
    expected_path_list = [q.getPath() for q in children_document_list +
        [parent_document]]
    try:
      # wrap call to catalogObjectList
      self.wrap_catalogObjectList()
      self.stepTic()
      self.assertSameSet(
        self.portal.catalogged_object_path_dict.keys(),
        expected_path_list
      )
      # do real assertions
      self.portal.catalogged_object_path_dict = PersistentMapping()
      transaction.commit()
      parent_document.reindexObject()
      self.stepTic()
      self.assertSameSet(
        self.portal.catalogged_object_path_dict.keys(),
        expected_path_list
      )
    finally:
      # unwrap catalogObjectList
      self.unwrap_catalogObjectList()
