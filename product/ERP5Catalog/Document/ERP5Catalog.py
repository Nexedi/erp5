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

class Filter(object):
  """
  Class to act as filter object for filterable methods.
  Added to keep consistency between how filter objects used to behave earlier
  with old SQL Catalog and with the current ERP5 Catalog.

  Generally, we do have 5 fixed keys, aka properties for catalog methods.
  """

  def __init__(self, method):
     self._method = method

  def __getitem__(self, key):
    #XXX: Temporary hardcode for list_type objects
    if key in ('type', 'expression_cache_key'):
      return self._method.getPropertyList(key)
    return self._method.getProperty(key)

  def get(self, key, default=None):
    try:
      return self.__getitem__(key)
    except KeyError: return default

  def __setitem__(self, key, value):
     self._method._setProperty(key, value)

  def __iter__(self):
    return iter(('type', 'expression_cache_key', 'expression', 'filtered', 'expression_instance'))

class FilterDict(object):
  """
  Class to act as object everytime we need to use filter_dict as a
  dictionary. It doesn't change the fact that the filter properties
  are still the properties of catalog methods(SQL Method and Python Scripts).
  One of important need of this class is it reduces a lot of copy and patch
  which we might had to do to functions in ZSQLCatalog.SQLCatalog.Catalog
  class.

  Also, as in old SQLCatalog the filter_dict is used as an attribute
  of Catalog, but now we have moved it to properties of method,
  this class help in keeping the consistency between the old filter_dict
  and new filter_dict.

  For example:

  Old SQL Catalog:
  filter_dict = self._getFilterDict() == self.filter_dict == {Persistent Object}

  ERP5 Catlaog:
  filter_dict = self._getFilterDict() == FilterDict(class) == {Object of this class}

  Now, both the filter_dict would have same behaviour without having any impact
  on performance or so. The major use of this is in _catalogObjectList, where
  we get Filter object, which is easily accessible via __getitem__ for this
  class.
  """

  def __init__(self, catalog):
     self._catalog = catalog

  def __getitem__(self, key):
     return Filter(self._catalog._getOb(key))

  def keys(self):
    return self._catalog.getFilterDict().keys()

  def has_key(self, method_id):
    return method_id in self.keys()

  def __setitem__(self, key, item):
    filter_ = self.__getitem__(key)
    for k, v in item.items():
      filter_.__setitem__(k, v)

  def get(self, key, default=None):
    if key in self:
      return self.__getitem__(key)
    else:
      return default

  def __iter__(self):
    return iter(self.keys())

  def __contains__(self, item):
    return item in self.keys()

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
  # We don't want to index catalog as it might create circular dependencies
  isIndexable = 0
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

  ##### Overriding setters functions for multple_selection properties #######
  #####   Required as after every edit we expect the values sorted    #######

  def _setSqlClearCatalogList(self, value, **kw):
    value = sorted(value)
    self._baseSetSqlClearCatalogList(value, **kw)

  def _setSqlCatalogFullTextSearchKeysList(self, value, **kw):
    value = sorted(value)
    self._baseSetSqlCatalogFullTextSearchKeysList(value, **kw)

  def _setSqlCatalogObjectListList(self, value, **kw):
    value = sorted(value)
    self._baseSetSqlCatalogObjectListList(value, **kw)

  def _setSqlUncatalogObjectList(self, value, **kw):
    value = sorted(value)
    self._baseSetSqlUncatalogObjectList(value, **kw)

  def _setSqlSearchTablesList(self, value, **kw):
    value = sorted(value)
    self._baseSetSqlSearchTablesList(value, **kw)

  def _setSqlCatalogDatetimeSearchKeysList(self, value, **kw):
    value = sorted(value)
    self._baseSetSqlCatalogDatetimeSearchKeysList(value, **kw)

  def _setSqlCatalogKeywordSearchKeysList(self, value, **kw):
    value = sorted(value)
    self._baseSetSqlCatalogKeywordSearchKeysList(value, **kw)

  def _setSqlCatalogMultivalueKeysList(self, value, **kw):
    value = sorted(value)
    self._baseSetSqlCatalogMultivalueKeysList(value, **kw)

  def _setSqlCatalogRequestKeysList(self, value, **kw):
    value = sorted(value)
    self._baseSetSqlCatalogRequestKeysList(value, **kw)

  def _setSqlCatalogIndexOnOrderKeysList(self, value, **kw):
    value = sorted(value)
    self._baseSetSqlCatalogIndexOnOrderKeysList(value, **kw)

  def _setSqlCatalogTableVoteScriptsList(self, value, **kw):
    value = sorted(value)
    self._baseSetSqlCatalogTableVoteScriptsList(value, **kw)

  def _setSqlSearchResultKeysList(self, value, **kw):
    value = sorted(value)
    self._baseSetSqlSearchResultKeysList(value, **kw)

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

  def _getFilterDict(self):
    return FilterDict(self)

  def _getCatalogMethodArgumentList(self, method):
    if method.meta_type == "LDIF Method":
      # Build the dictionnary of values
      return method.arguments_src.split()
    elif method.meta_type == "ERP5 SQL Method":
      return method.getArgumentsSrc().split()
    elif method.meta_type == "ERP5 Python Script":
      return method.func_code.co_varnames[:method.func_code.co_argcount]
    return ()

  def _getCatalogMethod(self, method_name):
    return self._getOb(method_name)

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
