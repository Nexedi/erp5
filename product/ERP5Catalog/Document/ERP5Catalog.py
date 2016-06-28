# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ayush Tiwari <ayush.tiwari@nexedi.com>
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

from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import Base
from Products.ERP5Type import PropertySheet
from Products.ERP5Type.patches.PropertyManager import PropertyManager
from Products.ZSQLCatalog.SQLCatalog import Catalog, CatalogError

import OFS.History
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.CMFCore.Expression import Expression
from zLOG import LOG, INFO, TRACE, WARNING, ERROR

import time
import urllib

def manage_addERP5Catalog(self, id, title,
             vocab_id='create_default_catalog_',
             REQUEST=None,
             **kw):
  """Add a Catalog object
  """
  id = str(id)
  title = str(title)
  vocab_id = str(vocab_id)
  if vocab_id == 'create_default_catalog_':
    vocab_id = None

  c = ERP5Catalog(id, title, self)
  self._setObject(id, c)
  c = self._getOb(id)
  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect( 'manage_main' )
  return c

class ERP5Catalog(Folder, Catalog):
  """
  Catalog Folder inside ERP5 to store indexes
  """

  meta_type = "ERP5 Catalog"
  portal_type = 'Catalog'
  allowed_types = ('Python Script', 'SQL Method',)
  #TODO(low priority): Add an icon to display at ERP5 Zope interface
  icon = None
  # Activate isRADContent cause we need to generate accessors and default values
  isRADContent = 1
  global valid_method_meta_type_list_new
  valid_method_meta_type_list_new = ('ERP5 SQL Method', 'ERP5 Python Script')

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
  security.declareProtected(Permissions.ManagePortal,
                              'manage_editProperties',
                              'manage_changeProperties',
                              'manage_propertiesForm',
                                )

  manage_options = ( Folder.manage_options+
                     OFS.History.Historical.manage_options
                   )

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.Folder
                    , PropertySheet.CategoryCore
                    , PropertySheet.Catalog
                    )

  # Declarative Constructors
  constructors = (manage_addERP5Catalog,)

  # Use functions inherited from SQLCatalog for property setters
  _setPropValue = Catalog._setPropValue
  getProperty = Folder.getProperty
  _updateProperty = PropertyManager._updateProperty
  isIndexable = Catalog.isIndexable
  __class_init__  = Catalog.__class_init__

  def __init__(self, id, title='', container=None):
    # Initialize both SQLCatalog as well as Folder
    Catalog.__init__(self, id, title, container)
    Folder.__init__(self, id)
    # Add for compatibility
    self._properties = ()

  # Filter content (ZMI))
  def filtered_meta_types(self, user=None):
    # Filters the list of available meta types.
    meta_types = []
    for meta_type in self.all_meta_types():
      if meta_type['name'] in self.allowed_types:
        meta_types.append(meta_type)
    return meta_types

  def getPropertyType(self, id, local_properties=False):
    """
    Overriding the function so as to maintain consistency
    between what is returned by 1 and 2

    1. erp5_catalog.getProperty(<some_multivalued_property>)
    2. sql_catalog.getProperty(<some_multivalued_property>)

    This difference arose as now we use ERP5 PropertySheet to define
    properties for Catalog which, for the multivalued properties,
    generate '<id>' as '<id>_list' and a new attribute 'base_id' in the
    propertyMap for the object.
    """
    if local_properties:
      property_map = getattr(self, '_local_properties', [])
    else:
      property_map = self._propertyMap()
    for md in property_map:
      property_id = md.get('base_id', md['id'])
      if property_id==id:
        return md.get('type', 'string')
    return None

  security.declarePublic('getCatalogMethodIds')
  def getCatalogMethodIds(self,
      valid_method_meta_type_list=valid_method_meta_type_list_new):
    """Find ERP5 SQL methods in the current folder and above
    This function return a list of ids.
    """
    return super(ERP5Catalog, self).getCatalogMethodIds(
      valid_method_meta_type_list=valid_method_meta_type_list_new)

  def manage_catalogReindex(self, REQUEST, RESPONSE=None, URL1=None):
    """ Clear the catalog and reindex everything for the erp5 catalog.
    """
    elapse = time.time()
    c_elapse = time.clock()

    self.aq_parent.refreshCatalog(clear=1)

    elapse = time.time() - elapse
    c_elapse = time.clock() - c_elapse

    # Redirect the response to view url
    url = self.absolute_url() + '/view' + '?portal_status_message=' \
                                  + urllib.quote(
                                  'Catalog Updated\r'
                                  'Total time: %s\r'
                                  'Total CPU time: %s' % (`elapse`, `c_elapse`))
    return REQUEST.RESPONSE.redirect(url)

  def manage_catalogClear(self, REQUEST=None, RESPONSE=None, URL1=None):
    """ Clears the catalog
    """
    self.beforeCatalogClear()

    self._clear()

    if REQUEST is None:
      return

    response = REQUEST.response
    if response:
      # Redirect the response to view url
      url = self.absolute_url() + '/view' \
                              + '?portal_status_message=Catalog%20Cleared'
      return response.redirect(url)

  def manage_catalogClearReserved(self, REQUEST=None, RESPONSE=None, URL1=None):
    """ Clears reserved uids """
    self._clearReserved()

    if REQUEST is None:
      return

    response = REQUEST.response
    if response:
      # Redirect the response to view url
      url = self.absolute_url() + '/view' \
                              + '?portal_status_message=Reserve%20UIDs%20Cleared'
      return REQUEST.RESPONSE.redirect(url)

  def _catalogObjectList(self, object_list, method_id_list=None,
                         disable_cache=0, check_uid=1, idxs=None):
    """This is the real method to catalog objects.

    This method overrides the method from SQLCatalog.Catalog, mainly because of
    the changes being done in filter_dict, which now is dictionary of properties
    of SQLMethod(s).
    """
    LOG('ERP5Catalog', TRACE, 'catalogging %d objects' % len(object_list))
    if idxs not in (None, []):
      LOG('ERP5Catalog.ERP5Catalog:catalogObjectList', WARNING,
          'idxs is ignored in this function and is only provided to be compatible with CMFCatalogAware.reindexCatalogObject.')

    if not self.isIndexable():
      return

    # Reminder about optimization: It might be possible to issue just one
    # query to get enought results to check uid & path consistency.
    path_uid_dict = {}
    uid_path_dict = {}

    if check_uid:
      path_list = []
      path_list_append = path_list.append
      uid_list = []
      uid_list_append = uid_list.append
      for object in object_list:
        path = object.getPath()
        if path is not None:
          path_list_append(path)
        uid = object.uid
        if uid is not None:
          uid_list_append(uid)
      path_uid_dict = self.getUidDictForPathList(path_list=path_list)
      uid_path_dict = self.getPathDictForUidList(uid_list=uid_list)

    # This dict will store uids and objects which are verified below.
    # The purpose is to prevent multiple objects from having the same
    # uid inside object_list.
    assigned_uid_dict = {}

    for object in object_list:
      uid = getattr(aq_base(object), 'uid', None)
      # Several Tool objects have uid=0 (not 0L) from the beginning, but
      # we need an unique uid for each object.
      if uid is None or isinstance(uid, int) and uid == 0:
        try:
          object.uid = self.newUid()
        except ConflictError:
          raise
        except:
          raise RuntimeError, 'could not set missing uid for %r' % (object,)
      elif check_uid:
        if uid in assigned_uid_dict:
            error_message = 'uid of %r is %r and ' \
                  'is already assigned to %s in catalog !!! This can be fatal.' % \
                  (object, uid, assigned_uid_dict[uid])
            if not self.sql_catalog_raise_error_on_uid_check:
                LOG("ERP5Catalog.catalogObjectList", ERROR, error_message)
            else:
                raise ValueError(error_message)

        path = object.getPath()
        index = path_uid_dict.get(path)
        if index is not None:
          if index < 0:
            raise CatalogError, 'A negative uid %d is used for %s. Your catalog is broken. Recreate your catalog.' % (index, path)
          if uid != index or isinstance(uid, int):
            # We want to make sure that uid becomes long if it is an int
            error_message = 'uid of %r changed from %r (property) to %r '\
	                    '(catalog, by path) !!! This can be fatal' % (object, uid, index)
            if not self.sql_catalog_raise_error_on_uid_check:
              LOG("ERP5Catalog.catalogObjectList", ERROR, error_message)
            else:
              raise ValueError(error_message)
        else:
          # Make sure no duplicates - ie. if an object with different path has same uid, we need a new uid
          # This can be very dangerous with relations stored in a category table (CMFCategory)
          # This is why we recommend completely reindexing subobjects after any change of id
          if uid in uid_path_dict:
            catalog_path = uid_path_dict.get(uid)
          else:
            catalog_path = self.getPathForUid(uid)
          #LOG('catalogObject', 0, 'uid = %r, catalog_path = %r' % (uid, catalog_path))
          if catalog_path == "reserved":
            # Reserved line in catalog table
            lock = self.__class__._reserved_uid_lock
            try:
              lock.acquire()
              uid_buffer = self.getUIDBuffer()
              if uid_buffer is not None:
                # This is the case where:
                #   1. The object got an uid.
                #   2. The catalog was cleared.
                #   3. The catalog produced the same reserved uid.
                #   4. The object was reindexed.
                # In this case, the uid is not reserved any longer, but
                # Catalog believes that it is still reserved. So it is
                # necessary to remove the uid from the list explicitly.
                try:
                  uid_buffer.remove(uid)
                except ValueError:
                  pass
            finally:
              lock.release()
          elif catalog_path == 'deleted':
            # Two possible cases:
            # - Reindexed object's path changed (ie, it or at least one of its
            #   parents was renamed) but unindexObject was not called yet.
            #   Reindexing is harmelss: unindexObject and then an
            #   immediateReindexObject will be called.
            # - Reindexed object was deleted by a concurrent transaction, which
            #   committed after we got our ZODB snapshot of this object.
            #   Reindexing is harmless: unindexObject will be called, and
            #   cannot be executed in parallel thanks to activity's
            #   serialisation_tag (so we cannot end up with a fantom object in
            #   catalog).
            # So we index object.
            # We could also not index it to save the time needed to index, but
            # this would slow down all regular case to slightly improve an
            # exceptional case.
            pass
          elif catalog_path is not None:
            # An uid conflict happened... Why?
            # can be due to path length
            if len(path) > MAX_PATH_LEN:
              LOG('ERP5Catalog', ERROR, 'path of object %r is too long for catalog. You should use a shorter path.' %(object,))

            LOG('ERP5Catalog', ERROR,
                'uid of %r changed from %r to %r as old one is assigned'
                ' to %s in catalog !!! This can be fatal.' % (
                object, uid, object.uid, catalog_path))

            error_message = 'uid of %r is %r and ' \
                            'is already assigned to %s in catalog !!! This can be fatal.' \
                            % (object, uid, catalog_path)
            if not self.sql_catalog_raise_error_on_uid_check:
                LOG('ERP5Catalog', ERROR, error_message)
            else:
                raise ValueError(error_message)
            uid = object.uid

        assigned_uid_dict[uid] = object

    if method_id_list is None:
      method_id_list = self.sql_catalog_object_list
    econtext = getEngine().getContext()
    if disable_cache:
      argument_cache = DummyDict()
    else:
      argument_cache = {}

    with (noReadOnlyTransactionCache if disable_cache else
          readOnlyTransactionCache)():
      filter_dict = self.getFilterDict()
      catalogged_object_list_cache = {}
      for method_name in method_id_list:
        # We will check if there is an filter on this
        # method, if so we may not call this zsqlMethod
        # for this object
        expression = None
        try:
          filter = filter_dict[method_name]
          method = getattr(self, method_name, None)
          if filter['filtered']:
            if filter.get('type'):
              expression = Expression('python: context.getPortalType() in '
                                      + repr(tuple(filter['type'])))
              LOG('ERP5Catalog', WARNING,
                  "Convert deprecated type filter for %r into %r expression"
                  % (method_name, expression.text))
              method.setType = ()
              method.setExpression(expression.text)
              method.setExpressionInstance(expression)
            else:
              expression = filter['expression_instance']
        except KeyError:
          pass
        if expression is None:
          catalogged_object_list = object_list
        else:
          text = expression.text
          catalogged_object_list = catalogged_object_list_cache.get(text)
          if catalogged_object_list is None:
            catalogged_object_list_cache[text] = catalogged_object_list = []
            append = catalogged_object_list.append
            old_context = new_context_search(text) is None
            if old_context:
              warnings.warn("Filter expression for %r (%r): using variables"
                            " other than 'context' is deprecated and slower."
                            % (method_name, text), DeprecationWarning)
            expression_cache_key_list = filter.get('expression_cache_key', ())
            expression_result_cache = {}
            for object in object_list:
              if expression_cache_key_list:
                # Expressions are slow to evaluate because they are executed
                # in restricted environment. So we try to save results of
                # expressions by portal_type or any other key.
                # This cache is built each time we reindex
                # objects but we could also use over multiple transactions
                # if this can improve performance significantly
                # ZZZ - we could find a way to compute this once only
                cache_key = tuple(object.getProperty(key) for key
                                  in expression_cache_key_list)
                try:
                  if expression_result_cache[cache_key]:
                    append(object)
                  continue
                except KeyError:
                  pass
              if old_context:
                result = expression(self.getExpressionContext(object))
              else:
                econtext.setLocal('context', object)
                result = expression(econtext)
              if expression_cache_key_list:
                expression_result_cache[cache_key] = result
              if result:
                append(object)

        if not catalogged_object_list:
          continue

        #LOG('catalogObjectList', 0, 'method_name = %s' % (method_name,))
        method = getattr(self, method_name)
        if method.meta_type == "LDIF Method":
          # Build the dictionnary of values
          arguments = method.arguments_src.split()
        elif method.meta_type == "ERP5 SQL Method":
          arguments = method.getArgumentsSrc().split()
        elif method.meta_type == "ERP5 Python Script":
          arguments = \
            method.func_code.co_varnames[:method.func_code.co_argcount]
        else:
          arguments = []
        kw = {x: LazyIndexationParameterList(catalogged_object_list,
                                             x, argument_cache)
          for x in arguments}

        # Alter/Create row
        try:
          #start_time = DateTime()
          #LOG('catalogObjectList', DEBUG, 'kw = %r, method_name = %r' % (kw, method_name))
          method(**kw)
          #end_time = DateTime()
          #if method_name not in profile_dict:
          #  profile_dict[method_name] = end_time.timeTime() - start_time.timeTime()
          #else:
          #  profile_dict[method_name] += end_time.timeTime() - start_time.timeTime()
          #LOG('catalogObjectList', 0, '%s: %f seconds' % (method_name, profile_dict[method_name]))

        except ConflictError:
          raise
        except:
          LOG('ERP5Catalog', WARNING, 'could not catalog objects %s with method %s' % (object_list, method_name),
              error=sys.exc_info())
          raise

  if psyco is not None:
    psyco.bind(_catalogObjectList)

  def manage_exportProperties(self, REQUEST=None, RESPONSE=None):
    """
    Export properties to an XML file.
    """
    f = StringIO()
    f.write('<?xml version="1.0"?>\n<CatalogData>\n')
    property_id_list = self.propertyIds()
    # Get properties and values
    property_list = []
    for property_id in property_id_list:
      value = self.getProperty(property_id)
      if value is not None:
        property_list.append((property_id, value))
    # Sort for easy diff
    property_list.sort(key=lambda x: x[0])
    for property in property_list:
      property_id = property[0]
      value       = property[1]
      if isinstance(value, basestring):
        f.write('  <property id=%s type="str">%s</property>\n' % (quoteattr(property_id), escape(value)))
      elif isinstance(value, (tuple, list)):
        f.write('  <property id=%s type="tuple">\n' % quoteattr(property_id))
        # Sort for easy diff
        item_list = []
        for item in value:
          if isinstance(item, basestring):
            item_list.append(item)
        item_list.sort()
        for item in item_list:
          f.write('    <item type="str">%s</item>\n' % escape(str(item)))
        f.write('  </property>\n')
    # filter_dict is now properties of SQL Methods now.
    # Outputting them here, juts for the comaptibility of results with ...
    # ... ERP5Catalog.ERP5Catalog.Catalog object
    filter_dict = self.getFilterDict()
    if filter_dict:
      filter_list = []
      for filter_id in self.filter_dict.keys():
        filter_definition = self.filter_dict[filter_id]
        filter_list.append((filter_id, filter_definition))
      # Sort for easy diff
      filter_list.sort(key=lambda x: x[0])
      for filter_item in filter_list:
        filter_id  = filter_item[0]
        filter_def = filter_item[1]
        if not filter_def['filtered']:
          # If a filter is not activated, no need to output it.
          continue
        if not filter_def['expression']:
          # If the expression is not specified, meaningless to specify it.
          continue
        f.write('  <filter id=%s expression=%s />\n' % (quoteattr(filter_id), quoteattr(filter_def['expression'])))
        # For now, portal types are not exported, because portal types are too specific to each site.
    f.write('</CatalogData>\n')

    if RESPONSE is not None:
      RESPONSE.setHeader('Content-type','application/data')
      RESPONSE.setHeader('Content-Disposition',
                          'inline;filename=properties.xml')
    return f.getvalue()

  def manage_importProperties(self, file):
    """
    Import properties from an XML file.
    We also set filter properties to methods here.
    """
    with open(file) as f:
      doc = parse(f)
      root = doc.documentElement
      try:
        for prop in root.getElementsByTagName("property"):
          id = prop.getAttribute("id")
          type = prop.getAttribute("type")
          if not id or not hasattr(self, id):
            raise CatalogError, 'unknown property id %r' % (id,)
          if type not in ('str', 'tuple'):
            raise CatalogError, 'unknown property type %r' % (type,)
          if type == 'str':
            value = ''
            for text in prop.childNodes:
              if text.nodeType == text.TEXT_NODE:
                value = str(text.data)
                break
          else:
            value = []
            for item in prop.getElementsByTagName("item"):
              item_type = item.getAttribute("type")
              if item_type != 'str':
                raise CatalogError, 'unknown item type %r' % (item_type,)
              for text in item.childNodes:
                if text.nodeType == text.TEXT_NODE:
                  value.append(str(text.data))
                  break
            value = tuple(value)

          setattr(self, id, value)

        # Update filter properties for the objects.
        for filt in root.getElementsByTagName("filter"):
          id = str(filt.getAttribute("id"))
          expression = filt.getAttribute("expression")
          method = getattr(self, 'id', None)
          if method:
            # Use property setters for setting method properties
            method.setFiltered(1)
            method.setType([])
            if expression:
              expr_instance = Expression(expression)
              method.setExpression(expression)
              method.setExpressionInstance(expr_instance)
            else:
              method.setExpression("")
              method.setExpressionInstance(None)
      finally:
        doc.unlink()

  def manage_editFilter(self, REQUEST=None, RESPONSE=None, URL1=None):
    """
    XXX: Deprecated
    Overriding the function manage_editFilter from SQLCatalog so that we
    don't waste time in setting/creating filter_dict object.

    Also, from inside ERP5, we won;t be having anything to call manage_editFilter
    but it is being called at some places in tests, and its better to deprecate
    useless methods.
    """
    raise ERP5CatalogError, 'manage_editFilter function is depreacted. Please \
                            refrain from using it'

  security.declarePrivate('isMethodFiltered')
  def isMethodFiltered(self, method_name):
    """
    Returns 1 if the mehtod is filtered,
    else it returns o
    """
    method =  aq_base(self)._getOb(method_name)

    if method is None:
      return 0
    return method.isFiltered()

  security.declarePrivate('getExpression')
  def getExpression(self, method_name):
    """ Get the filter expression text for this method.
    """
    method =  aq_base(self)._getOb(method_name)

    if method is None:
      return ""
    return method.getExpression()

  security.declarePrivate('getExpressionCacheKey')
  def getExpressionCacheKey(self, method_name):
    """ Get the key string which is used to cache results
        for the given expression.
    """
    method =  aq_base(self)._getOb(method_name)

    if method is None:
      return ""
    return ' '.join(method.getExpressionCacheKeyList())

  security.declarePrivate('getExpressionInstance')
  def getExpressionInstance(self, method_name):
    """ Get the filter expression instance for this method.
    """
    method =  aq_base(self)._getOb(method_name)

    if method is None:
      return None
    return method.getExpressionInstance()

  security.declarePrivate('setFilterExpression')
  def setFilterExpression(self, method_name, expression):
    """ Set the Expression for a certain method name. This allow set
        expressions by scripts.
    """
    method = aq_base(self)._getOb(method_name)

    if method is None:
      return None
    method.setExpression(expression)

    if expression:
      expression_instance = Expression(expression)
    else:
      expression_instance = None
    method.setExpressionInstance(expression)

  security.declarePrivate('isPortalTypeSelected')
  def isPortalTypeSelected(self, method_name, portal_type):
    """
    XXX Deprecated: Override so as not to fail tests
    """
    return 0

  security.declarePrivate('getFilterDict')
  def getFilterDict(self):
    """
      Utility Method.
      Filter Dict is a dictionary and used at Python Scripts,
      This method returns a filter dict as a dictionary.
    """
    filter_dict = {}
    method_list = self.getFilterableMethodList()
    for method in method_list:
      key = method.getId()
      if method.isFiltered():
        filter_dict[key] = {
                      'type': method.getTypeList(),
                      'filtered': 1,
                      'expression': method.getExpression(),
                      'expression_instance': method.getExpressionInstance(),
                      'expression_cache_key': method.getExpressionCacheKeyList()
                      }
    return filter_dict

InitializeClass(ERP5Catalog)

class ERP5CatalogError(CatalogError): pass
