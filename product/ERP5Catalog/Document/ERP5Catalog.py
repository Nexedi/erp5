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
from zLOG import LOG, INFO, TRACE, WARNING, ERROR

import time
import urllib.request, urllib.parse, urllib.error

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
      return self[key]
    except KeyError:
      return default

  def __setitem__(self, key, value):
     self._method._setProperty(key, value)

  def __iter__(self):
    return iter(('type', 'expression_cache_key', 'expression',
                 'filtered', 'expression_instance'))

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

  ERP5 Catalog:
  filter_dict = self._getFilterDict() == FilterDict(class) == {Instance of this class}

  Now, both the filter_dict would have same behaviour without having any impact
  on performance or so. The major use of this is in _catalogObjectList, where
  we get Filter object, which is easily accessible via __getitem__ for this
  class.
  """

  def __init__(self, catalog):
     self._catalog = catalog
     self._filterable = self._catalog.getFilterableMethodList()

  def __getitem__(self, key):
    method = self._catalog._getOb(key)
    if method in  self._filterable and method.isFiltered():
      return Filter(method)
    raise KeyError(key)

  def __setitem__(self, key, item):
    filter_ = self[key]
    for k, v in item.iteritems():
      filter_[k] = v

  def get(self, key, default=None):
    # First check if the key is in keys list of the FilterDict, because
    # it is possible that the item can be get by doing `self[key]`, even though
    # key doesn't exist in self.keys(). So, instead of doing `try : except`,
    # we use `if : else`
    try:
      return self[key]
    except KeyError:
      return default

  def __delitem__(self, key):
    filter_ = self[key]
    for prop_id in ('type', 'expression_cache_key', 'expression',
                    'filtered', 'expression_instance'):
      filter_._method._delPropValue(prop_id)

class ERP5Catalog(Folder, Catalog):
  """
  Catalog Folder inside ERP5 to store indexes
  """

  meta_type = "ERP5 Catalog"
  portal_type = 'Catalog'
  allowed_types = 'External Method', 'Python Script', 'SQL Method'
  #TODO(low priority): Add an icon to display at ERP5 Zope interface
  icon = None
  # Activate isRADContent cause we need to generate accessors and default values
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Explicitly add tabs for manage_options
  manage_options = ({'label': 'Contents', 'action': 'manage_main'},
                    {'label': 'View', 'action': 'view'},
                    {'label': 'Security', 'action': 'manage_access'},
                    {'label': 'Undo', 'action': 'manage_UndoForm'},
                    {'label': 'Ownership', 'action': 'manage_owner'},
                    {'label': 'Interfaces', 'action': 'manage_interfaces'},
                    {'label': 'Find', 'action': 'manage_findForm'},
                    {'label': 'History', 'action': 'manage_change_history_page'},
                    {'label': 'Workflows', 'action': 'manage_workflowsTab'},
                   )

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.Folder
                    , PropertySheet.CategoryCore
                    , PropertySheet.Catalog
                    )

  # Use functions inherited from SQLCatalog for property setters
  _setPropValue = Catalog._setPropValue
  getProperty = Folder.getProperty
  _updateProperty = PropertyManager._updateProperty
  # We don't want to index catalog as it might create circular dependencies
  isIndexable = 0
  __class_init__  = Catalog.__class_init__

  # Note: superclass supports older variants of these metatypes, but we do not
  # expect these as content here. So just override superclass properties with
  # the new metatypes.
  HAS_ARGUMENT_SRC_METATYPE_SET = (
    "ERP5 SQL Method",
  )
  HAS_FUNC_CODE_METATYPE_SET = (
    "ERP5 External Method",
    "ERP5 Python Script",
  )

  def __init__(self, id, title='', container=None):
    # Initialize both SQLCatalog as well as Folder
    Catalog.__init__(self, id, title, container)
    Folder.__init__(self, id)

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
      property_map = getattr(self, '_local_properties', ())
    else:
      property_map = self._propertyMap()
    for md in property_map:
      property_id = md.get('base_id', md['id'])
      if property_id == id:
        return md.get('type', 'string')
    return None

  ##### Overriding setters functions for multple_selection properties #######
  #####   Required as after every edit we expect the values sorted    #######

  def _setSqlClearCatalogList(self, value, **kw):
    self._baseSetSqlClearCatalogList(sorted(value), **kw)

  def _setSqlCatalogFullTextSearchKeysList(self, value, **kw):
    self._baseSetSqlCatalogFullTextSearchKeysList(sorted(value), **kw)

  def _setSqlCatalogObjectListList(self, value, **kw):
    self._baseSetSqlCatalogObjectListList(sorted(value), **kw)

  def _setSqlUncatalogObjectList(self, value, **kw):
    self._baseSetSqlUncatalogObjectList(sorted(value), **kw)

  def _setSqlSearchTablesList(self, value, **kw):
    self._baseSetSqlSearchTablesList(sorted(value), **kw)

  def _setSqlCatalogDatetimeSearchKeysList(self, value, **kw):
    self._baseSetSqlCatalogDatetimeSearchKeysList(sorted(value), **kw)

  def _setSqlCatalogKeywordSearchKeysList(self, value, **kw):
    self._baseSetSqlCatalogKeywordSearchKeysList(sorted(value), **kw)

  def _setSqlCatalogMultivalueKeysList(self, value, **kw):
    self._baseSetSqlCatalogMultivalueKeysList(sorted(value), **kw)

  def _setSqlCatalogRequestKeysList(self, value, **kw):
    self._baseSetSqlCatalogRequestKeysList(sorted(value), **kw)

  def _setSqlCatalogIndexOnOrderKeysList(self, value, **kw):
    self._baseSetSqlCatalogIndexOnOrderKeysList(sorted(value), **kw)

  def _setSqlCatalogTableVoteScriptsList(self, value, **kw):
    self._baseSetSqlCatalogTableVoteScriptsList(sorted(value), **kw)

  def _setSqlSearchResultKeysList(self, value, **kw):
    self._baseSetSqlSearchResultKeysList(sorted(value), **kw)

  security.declarePublic('getCatalogMethodIds')
  def getCatalogMethodIds(self, valid_method_meta_type_list=
      HAS_ARGUMENT_SRC_METATYPE_SET + HAS_FUNC_CODE_METATYPE_SET):
    """Find ERP5 SQL methods in the current folder and above
    This function return a list of ids.
    """
    return super(ERP5Catalog, self).getCatalogMethodIds(
                                      valid_method_meta_type_list)

  security.declarePublic('getPythonMethodIds')
  def getPythonMethodIds(self):
    """
      Returns a list of all python scripts available in
      current sql catalog.
    """
    return self.getCatalogMethodIds(valid_method_meta_type_list=(
      'ERP5 External Method',
      'ERP5 Python Script'))

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

  def _getFilterDict(self):
    return FilterDict(self)

  def _getCatalogMethod(self, method_name):
    return self._getOb(method_name)

  security.declarePrivate('isMethodFiltered')
  def isMethodFiltered(self, method_name):
    """
    Returns 1 if the mehtod is filtered,
    else it returns o
    """
    method =  self._getOb(method_name)

    if method is None:
      return 0
    return method.isFiltered()

  security.declarePrivate('getExpression')
  def getExpression(self, method_name):
    """ Get the filter expression text for this method.
    """
    method =  self._getOb(method_name)

    if method is None:
      return ""
    return method.getExpression()

  security.declarePrivate('getExpressionCacheKey')
  def getExpressionCacheKey(self, method_name):
    """ Get the key string which is used to cache results
        for the given expression.
    """
    method =  self._getOb(method_name)

    if method is None:
      return ""
    return ' '.join(method.getExpressionCacheKeyList())

  security.declarePrivate('getExpressionInstance')
  def getExpressionInstance(self, method_name):
    """ Get the filter expression instance for this method.
    """
    method =  self._getOb(method_name)

    if method is None:
      return None
    return method.getExpressionInstance()

  security.declarePrivate('setFilterExpression')
  def setFilterExpression(self, method_name, expression):
    """ Set the Expression for a certain method name. This allow set
        expressions by scripts.
    """
    method = self._getOb(method_name)

    if method is None:
      return None
    method.setExpression(expression)

InitializeClass(ERP5Catalog)

class ERP5CatalogError(CatalogError): pass
