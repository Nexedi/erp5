##############################################################################
#
# Copyright (c) 2002 Nexedi SARL. All Rights Reserved.
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from Persistence import Persistent
import Acquisition
import ExtensionClass
from string import lower, split, join
from thread import get_ident

from DateTime import DateTime
from Products.PluginIndexes.common.randid import randid
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent, aq_inner, aq_base, aq_self
from zLOG import LOG

import time
import sys

UID_BUFFER_SIZE = 900
MAX_UID_BUFFER_SIZE = 20000

class Catalog(Persistent, Acquisition.Implicit, ExtensionClass.Base):
  """ An Object Catalog

  An Object Catalog maintains a table of object metadata, and a
  series of manageable indexes to quickly search for objects
  (references in the metadata) that satisfy a search where_expression.

  This class is not Zope specific, and can be used in any python
  program to build catalogs of objects.  Note that it does require
  the objects to be Persistent, and thus must be used with ZODB3.

  uid -> the (local) universal ID of objects
  path -> the (local) path of objects


  bgrain defined in meyhods...

  TODO:

    - optmization: indexing objects should be deferred
      until timeout value or end of transaction
  """
  _after_clear_reserved = 0

  def __init__(self):
    self.schema = {}  # mapping from attribute name to column
    self.names = {}   # mapping from column to attribute name
    self.indexes = {}   # empty mapping

  def clear(self):
    """
    Clears the catalog by calling a list of methods
    """
    methods = self.sql_clear_catalog
    for method_name in methods:
      method = getattr(self,method_name)
      try:
        method()
      except:
        pass
    self._after_clear_reserved = 1

  def clearReserved(self):
    """
    Clears reserved uids
    """
    method_id = self.sql_catalog_clear_reserved
    method = getattr(self, method_id)
    method()
    self._after_clear_reserved = 1

  def __getitem__(self, uid):
    """
    Get an object by UID
    Note: brain is defined in Z SQL Method object
    """
    method = getattr(self,  self.sql_getitem_by_uid)
    search_result = method(uid = uid)
    if len(search_result) > 0:
      return search_result[0]
    else:
      return None

  def editSchema(self, names_list):
    """
    Builds a schema from a list of strings
    Splits each string to build a list of attribute names
    Columns on the database should not change during this operations
    """
    i = 0
    schema = {}
    names = {}
    for cid in self.getColumnIds():
      name_list = []
      for name in names_list[i].split():
        schema[name] = cid
        name_list += [name,]
      names[cid] = tuple(name_list)
      i += 1
    self.schema = schema
    self.names = names

  def getColumnIds(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids

    XXX This should be cached
    """
    method_name = self.sql_catalog_schema
    keys = {}
    for table in self.getCatalogSearchTableIds():
      try:
        method = getattr(self,  method_name)
        search_result = method(table=table)
        for c in search_result:
          keys[c.Field] = 1
          keys['%s.%s' % (table, c.Field)] = 1  # Is this inconsistent ?
      except:
        pass
    keys = keys.keys()
    keys.sort()
    return keys

  def getColumnMap(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids

    XXX This should be cached
    """
    method_name = self.sql_catalog_schema
    keys = {}
    for table in self.getCatalogSearchTableIds():
      try:
        method = getattr(self,  method_name)
        search_result = method(table=table)
        for c in search_result:
          key = c.Field
          if not keys.has_key(key): keys[c.Field] = []
          keys[key].append(table)
          key = '%s.%s' % (table, c.Field)
          if not keys.has_key(key): keys[key] = []
          keys[key].append(table) # Is this inconsistent ?
      except:
        pass
    return keys

  def getResultColumnIds(self):
    """
    Calls the show column method and returns dictionnary of
    Field Ids
    """
    method_name = self.sql_catalog_schema
    keys = {}
    for table in self.getCatalogSearchTableIds():
      try:
        method = getattr(self,  method_name)
        search_result = method(table=table)
        for c in search_result:
          keys['%s.%s' % (table, c.Field)] = 1
      except:
        pass
    keys = keys.keys()
    keys.sort()
    return keys

  def getTableIds(self):
    """
    Calls the show table method and returns dictionnary of
    Field Ids
    """
    keys = []
    method_name = self.sql_catalog_tables
    try:
      method = getattr(self,  method_name)
      search_result = method()
      for c in search_result:
        keys.append(c[0])
    except:
      pass
    return keys

  # the cataloging API
  def produceUid(self):
    """
      Produces reserved uids in advance
    """
    method_id = self.sql_catalog_produce_reserved
    method = getattr(self, method_id)
    thread_id = get_ident()
    uid_list = getattr(self, '_v_uid_buffer', [])
    if self._after_clear_reserved:
      # Reset uid list after clear reserved
      self._after_clear_reserved = 0
      uid_list = []
    if len(uid_list) < UID_BUFFER_SIZE:
      date = DateTime()
      new_uid_list = method(count = UID_BUFFER_SIZE, thread_id=thread_id, date=date)
      uid_list.extend( filter(lambda x: x != 0, map(lambda x: x.uid, new_uid_list )))
    self._v_uid_buffer = uid_list

  def newUid(self):
    """
      This is where uid generation takes place. We should consider a multi-threaded environment
      with multiple ZEO clients on a single ZEO server.

      The main risk is the following:

      - objects a/b/c/d/e/f are created (a is parent of b which is parent of ... of f)

      - one reindexing node N1 starts reindexing f

      - another reindexing node N2 starts reindexing e

      - there is a strong risk that N1 and N2 start reindexing at the same time
        and provide different uid values for a/b/c/d/e

      Similar problems may happen with relations and acquisition of uid values (ex. order_uid)
      with the risk of graph loops
    """
    self.produceUid()
    uid_list = getattr(self, '_v_uid_buffer', [])
    if len(uid_list) > 0:
      return uid_list.pop()
    else:
      raise CatalogError("Could not retrieve new uid")

  def catalogObject(self, object, path, is_object_moved=0):
    """
    Adds an object to the Catalog by calling
    all SQL methods and providing needed arguments.

    'object' is the object to be cataloged

    'uid' is the unique Catalog identifier for this object

    """
    #LOG('Catalog object:',0,str(path))

    # Prepare the dictionnary of values
    kw = {}

    # Check if already Catalogued
    if hasattr(aq_base(object), 'uid'):
      # Try to use existing uid
      # WARNING COPY PASTE....
      uid = object.uid
    else:
      # Look up in (previous) path
      uid = 0
    if is_object_moved:
      index = uid # We trust the current uid
    else:
      index = self.getUidForPath(path)
    if index:
      if (uid != index):
        # Update uid attribute of object
        uid = int(index)
        #LOG("Write Uid",0, "uid %s index %s" % (uid, index))
        object.uid = uid
      # We will check if there is an filter on this
      # method, if so we may not call this zsqlMethod
      # for this object
      for method_name in self.sql_update_object:
        if self.isMethodFiltered(method_name):
          if self.filter_dict.has_key(method_name):
            portal_type = object.getPortalType()
            if portal_type not in (self.filter_dict[method_name]['type']):
              #LOG('catalog_object',0,'XX1 this method is broken because not in types: %s' % method_name)
              continue
            else:
              expression = self.filter_dict[method_name]['expression_instance']
              if expression is not None:
                econtext = self.getExpressionContext(object)
                result = expression(econtext)
                if not result:
                  #LOG('catalog_object',0,'XX2 this method is broken because expression: %s' % method_name)
                  continue
        #LOG('catalog_object',0,'this method is not broken: %s' % method_name)
        # Get the appropriate SQL Method
        # Lookup by path is required because of OFS Semantics
        method = getattr(self, method_name)
        if method.meta_type == "Z SQL Method":
          # Build the dictionnary of values
          arguments = method.arguments_src
          for arg in split(arguments):
            try:
              value = getattr(object, arg)
              if callable(value):
                value = value()
              kw[arg] = value
            except:
              #LOG("SQLCatalog Warning: Callable value could not be called",0,str((path, arg, method_name)))
              kw[arg] = None
        method = aq_base(method).__of__(object.__of__(self)) # Use method in the context of object
        # Generate UID
        kw['path'] = path
        kw['uid'] = int(index)
        kw['insert_catalog_line'] = 0
        #LOG("SQLCatalog Warning: insert_catalog_line, case1 value",0,0)
        # LOG
        # LOG("Call SQL Method %s with args:" % method_name,0, str(kw))
        # Alter row
        #LOG("Call SQL Method %s with args:" % method_name,0, str(kw))
        method(**kw)
    else:
      # Get the appropriate SQL Method
      # Lookup by path is required because of OFS Semantics
      if uid:
        # Make sure no duplicates - ie. if an object with different path has same uid, we need a new uid
        # This can be very dangerous with relations stored in a category table (CMFCategory)
        # This is why we recommend completely reindexing subobjects after any change of id
        catalog_path = self.getPathForUid(uid)
        if catalog_path == "reserved":
          # Reserved line in catalog table
          insert_catalog_line = 0
          #LOG("SQLCatalog Warning: insert_catalog_line, case2",0,insert_catalog_line)
        elif catalog_path is None:
          # No line in catalog table
          insert_catalog_line = 1
          #LOG("SQLCatalog Warning: insert_catalog_line, case3",0,insert_catalog_line)
        else:
          #LOG('SQLCatalog WARNING',0,'assigning new uid to already catalogued object %s' % path)
          uid = 0
          insert_catalog_line = 0
          #LOG("SQLCatalog Warning: insert_catalog_line, case4",0,insert_catalog_line)
      if not uid:
        # Generate UID
        index = self.newUid()
        object.uid = index
        insert_catalog_line = 0
        #LOG("SQLCatalog Warning: insert_catalog_line, case5",0,insert_catalog_line)
      else:
        index = uid
      for method_name in self.sql_catalog_object:
        # We will check if there is an filter on this
        # method, if so we may not call this zsqlMethod
        # for this object
        if self.isMethodFiltered(method_name):
          if self.filter_dict.has_key(method_name):
            portal_type = object.getPortalType()
            if portal_type not in (self.filter_dict[method_name]['type']):
              #LOG('catalog_object',0,'XX1 this method is broken because not in types: %s' % method_name)
              continue
            else:
              expression = self.filter_dict[method_name]['expression_instance']
              if expression is not None:
                econtext = self.getExpressionContext(object)
                result = expression(econtext)
                if not result:
                  #LOG('catalog_object',0,'XX2 this method is broken because expression: %s' % method_name)
                  continue
        #LOG('catalog_object',0,'this method is not broken: %s' % method_name)

        method = getattr(self, method_name)
        if method.meta_type == "Z SQL Method":
          # Build the dictionnary of values
          arguments = method.arguments_src
          for arg in split(arguments):
            try:
              value = getattr(object, arg)
              if callable(value):
                value = value()
              kw[arg] = value
            except:
              #LOG("SQLCatalog Warning: Callable value could not be called",0,str((path, arg, method_name)))
              kw[arg] = None
        method = aq_base(method).__of__(object.__of__(self)) # Use method in the context of object
        # Generate UID
        kw['path'] = path
        kw['uid'] = index
        kw['insert_catalog_line'] = insert_catalog_line
        # Alter/Create row       
        try:
          zope_root = getToolByName(self, 'portal_url').getPortalObject().aq_parent
          root_indexable = int(getattr(zope_root,'isIndexable',1))
          if root_indexable:
            #LOG("Call SQL Method %s with args:" % method_name,0, str(kw))
            method(**kw)
        except:
          LOG("SQLCatalog Warning: could not catalog object with method %s" % method_name,100, str(path))
          raise
        #except:
        #  #  # This is a real LOG message
        #  #  # which is required in order to be able to import .zexp files
        #  LOG("SQLCatalog Warning: could not catalog object with method %s" % method_name,
        #                                                                   100,str(path))

  def uncatalogObject(self, path):
    """
    Uncatalog and object from the Catalog.

    Note, the uid must be the same as when the object was
    catalogued, otherwise it will not get removed from the catalog

    This method should not raise an exception if the uid cannot
    be found in the catalog.

    XXX Add filter of methods

    """
    #LOG('Uncatalog object:',0,str(path))

    uid = self.getUidForPath(path)
    methods = self.sql_uncatalog_object
    for method_name in methods:
      method = getattr(self, method_name)
      try:
        #if 1:
        method(uid = uid)
      except:
        # This is a real LOG message
        # which is required in order to be able to import .zexp files
        LOG("SQLCatalog Warning: could not uncatalog object uid %s with method %s" %
                                               (uid, method_name),0,str(path))

  def uniqueValuesFor(self, name):
    """ return unique values for FieldIndex name """
    method = getattr(self, self.sql_unique_values)
    return method()

  def getPaths(self):
    """ Returns all object paths stored inside catalog """
    method = getattr(self, self.sql_catalog_paths)
    return method()

  def getUidForPath(self, path):
    """ Looks up into catalog table to convert path into uid """
    try:
      if path is None:
        return None
      # Get the appropriate SQL Method
      method = getattr(self, self.sql_getitem_by_path)
      search_result = method(path = path)
      # If not emptyn return first record
      if len(search_result) > 0:
        return search_result[0].uid
      else:
        return None
    except:
      # This is a real LOG message
      # which is required in order to be able to import .zexp files
      LOG("Warning: could not find uid from path",0,str(path))
      return None

  def hasPath(self, path):
    """ Checks if path is catalogued """
    return self.getUidForPath(path) is not None

  def getPathForUid(self, uid):
    """ Looks up into catalog table to convert uid into path """
    try:
      if uid is None:
        return None
      # Get the appropriate SQL Method
      method = getattr(self, self.sql_getitem_by_uid)
      search_result = method(uid = uid)
      # If not empty return first record
      if len(search_result) > 0:
        return search_result[0].path
      else:
        return None
    except:
      # This is a real LOG message
      # which is required in order to be able to import .zexp files
      LOG("Warning: could not find path from uid",0,str(uid))
      return None

  def getMetadataForUid(self, uid):
    """ Accesses a single record for a given uid """
    if uid is None:
      return None
    # Get the appropriate SQL Method
    method = getattr(self, self.sql_getitem_by_uid)
    brain = method(uid = uid)[0]
    result = {}
    for k in brain.__record_schema__.keys():
      result[k] = getattr(brain,k)
    return result

  def getIndexDataForUid(self, uid):
    """ Accesses a single record for a given uid """
    return self.getMetadataForUid(uid)

  def getMetadataForPath(self, path):
    """ Accesses a single record for a given path """
    try:
      if uid is None:
        return None
      # Get the appropriate SQL Method
      method = getattr(self, self.sql_getitem_by_path)
      brain = method(path = path)[0]
      result = {}
      for k in brain.__record_schema__.keys():
        result[k] = getattr(brain,k)
      return result
    except:
      # This is a real LOG message
      # which is required in order to be able to import .zexp files
      LOG("Warning: could not find uid from path",0,str(path))
      return None

  def getIndexDataForPath(self, path):
    """ Accesses a single record for a given path """
    return self.getMetadataForPath(path)

  def buildSQLQuery(self, query_table='catalog', REQUEST=None, **kw):
    """ Builds a complex SQL query to simulate ZCalatog behaviour """
    # Get search arguments:
    if REQUEST is None and (kw is None or kw == {}):
      # We try to get the REQUEST parameter
      # since we have nothing handy
      try: REQUEST=self.REQUEST
      except AttributeError: pass

    # If kw is not set, then use REQUEST instead
    if kw is None or kw == {}:
      kw = REQUEST

    acceptable_key_map = self.getColumnMap()
    acceptable_keys = acceptable_key_map.keys()
    full_text_search_keys = self.sql_catalog_full_text_search_keys
    keyword_search_keys = self.sql_catalog_keyword_search_keys
    topic_search_keys = self.sql_catalog_topic_search_keys
    multivalue_tables = self.sql_catalog_multivalue_tables

    # We take additional parameters from the REQUEST
    # and give priority to the REQUEST
    if REQUEST is not None:
      for key in acceptable_keys:
        if REQUEST.has_key(key):
          # Only copy a few keys from the REQUEST
          if key in self.sql_catalog_request_keys:
            kw[key] = REQUEST[key]

    # Let us start building the where_expression
    if kw:
      where_expression = []
      from_table_dict = {'catalog': 1} # Always include catalog table
      # Rebuild keywords to behave as new style query (_usage='toto:titi' becomes {'toto':'titi'})
      new_kw = {}
      usage_len = len('_usage')
      for k, v in kw.items():
        if k.endswith('_usage'):
          new_k = k[0:-usage_len]
          if not new_kw.has_key(new_k): new_kw[new_k] = {}  
          if type(new_kw[new_k]) is not type({}): new_kw[new_k] = {'query': new_kw[new_k]}
          split_v = v.split(':') 
          new_kw[new_k] = {split_v[0]: split_v[1]}
        else:
          if not new_kw.has_key(k):
            new_kw[k] = v
          else:            
            new_kw[k]['query'] = v
      kw = new_kw
      #LOG('new kw', 0, str(kw))
      # We can now consider that old style query is changed into new style
      for key in kw.keys(): # Do not use kw.items() because this consumes much more memory
        value = kw[key]
        if key not in ('where_expression', 'sort-on', 'sort_on', 'sort-order', 'sort_order'):
          # Make sure key belongs to schema
          if key in acceptable_keys:
            if key.find('.') < 0:
              # if the key is only used by one table, just append its name
              if len(acceptable_key_map[key]) == 1 :
                key = acceptable_key_map[key][0] + '.' + key
              # query_table specifies what table name should be used
              elif query_table:
                key = query_table + '.' + key
              elif key == 'uid':
                # uid is always ambiguous so we can only change it here
                key = 'catalog.uid'
            # Add table to table dict
            from_table_dict[acceptable_key_map[key][0]] = 1 # We use catalog by default
            # Default case: variable equality
            if type(value) is type(''):
              if value != '':
                # we consider empty string as Non Significant
                if value == '=':
                  # But we consider the sign = as empty string
                  value=''
                if '%' in value:
                  where_expression += ["%s LIKE '%s'" % (key, value)]
                elif value[0] == '>':
                  where_expression += ["%s > '%s'" % (key, value[1:])]
                elif value[0] == '<':
                  where_expression += ["%s < '%s'" % (key, value[1:])]
                elif key in keyword_search_keys:
                  # We must add % in the request to simulate the catalog
                  where_expression += ["%s LIKE '%%%s%%'" % (key, value)]
                elif key in full_text_search_keys:
                  # We must add % in the request to simulate the catalog
                  where_expression += ["MATCH %s AGAINST ('%s')" % (key, value)]
                else:
                  where_expression += ["%s = '%s'" % (key, value)]
            elif type(value) is type([]) or type(value) is type(()):
              # We have to create an OR from tuple or list
              query_item = []
              for value_item in value:
                if value_item != '':
                  # we consider empty string as Non Significant
                  # also for lists
                  if type(value_item) in (type(1), type(1.0)):
                    query_item += ["%s = %s" % (key, value_item)]
                  else:
                    if '%' in value_item:
                      query_item += ["%s LIKE '%s'" % (key, str(value_item))]
                    elif key in keyword_search_keys:
                      # We must add % in the request to simulate the catalog
                      query_item += ["%s LIKE '%%%s%%'" % (key, str(value_item))]
                    elif key in full_text_search_keys:
                      # We must add % in the request to simulate the catalog
                      query_item +=  ["MATCH %s AGAINST ('%s')" % (key, value)]
                    else:
                      query_item += ["%s = '%s'" % (key, str(value_item))]
              if len(query_item) > 0:
                where_expression += ['(%s)' % join(query_item, ' OR ')]
            elif type(value) is type({}):
              # We are in the case of a complex query
              query_value = value['query']
              if value.has_key('range'):
                # This is a range
                range_value = value['range']            
                if range_value == 'min':
                  where_expression += ["%s >= '%s'" % (key, query_value)]
                elif range_value == 'max':
                  where_expression += ["%s < '%s'" % (key, query_value)]
            else:
              where_expression += ["%s = %s" % (key, value)]
          elif key in topic_search_keys: 
            # ERP5 CPS compatibility           
            topic_operator = 'or'
            if type(value) is type({}):          
              topic_operator = value.get('operator', 'or')            
              value = value['query']
            if type(value) is type(''):
              topic_value = [value]
            else:
              topic_value = value # list or tuple
            query_item = []
            for topic_key in topic_value:
              if topic_key in acceptable_keys:
                if topic_key.find('.') < 0:
                  # if the key is only used by one table, just append its name
                  if len(acceptable_key_map[topic_key]) == 1 :
                    topic_key = acceptable_key_map[topic_key][0] + '.' + topic_key
                  # query_table specifies what table name should be used
                  elif query_table:
                    topic_key = query_table + '.' + topic_key
                # Add table to table dict
                from_table_dict[acceptable_key_map[topic_key][0]] = 1 # We use catalog by default              
                query_item += ["%s = 1" % topic_key]
            # Join                              
            if len(query_item) > 0:
              where_expression += ['(%s)' % join(query_item, ' %s ' % topic_operator)]
        elif param_key == 'where_expression':
          # Not implemented yet
          pass
      if kw.get('where_expression'):
        if len(where_expression) > 0:
          where_expression = "(%s) AND (%s)" % (kw['where_expression'], join(where_expression, ' AND ') )
      else:
        where_expression = join(where_expression, ' AND ')

    # Compute "sort_index", which is a sort index, or none:
    if kw.has_key('sort-on'):
      sort_index=kw['sort-on']
    elif hasattr(self, 'sort-on'):
      sort_index=getattr(self, 'sort-on')
    elif kw.has_key('sort_on'):
      sort_index=kw['sort_on']
    else: sort_index=None

    # Compute the sort order
    if kw.has_key('sort-order'):
      so=kw['sort-order']
    elif hasattr(self, 'sort-order'):
      so=getattr(self, 'sort-order')
    elif kw.has_key('sort_order'):
      so=kw['sort_order']
    else: so=None

    # We must now turn so into a string
    if type(so) is not type('a'):
      so = 'ascending'

    # We must now turn sort_index into
    # a dict with keys as sort keys and values as sort order
    if type(sort_index) is type('a'):
      sort_index = [(sort_index, so)]
    elif type(sort_index) is not type(()) and type(sort_index) is not type([]):
      sort_index = None

    # If sort_index is a dictionnary
    # then parse it and change it
    sort_on = None
    if sort_index is not None:
      try:
        new_sort_index = []
        for (k , v) in sort_index:
          if len(acceptable_key_map[k]) == 1 :
            k = acceptable_key_map[k][0] + '.' + k
          elif query_table:
            k = query_table + '.' + k
          if v == 'descending' or v == 'reverse':
            from_table_dict[acceptable_key_map[k][0]] = 1 # We need this table to sort on it
            new_sort_index += ['%s DESC' % k]
          else:
            from_table_dict[acceptable_key_map[k][0]] = 1 # We need this table to sort on it
            new_sort_index += ['%s' % k]
        sort_index = join(new_sort_index,',')
        sort_on = str(sort_index)
      except:
        pass

    # Use a dictionary at the moment.
    return { 'from_table_list' : from_table_dict.keys(),
             'order_by_expression' : sort_on,
             'where_expression' : where_expression }

  def queryResults(self, sql_method, REQUEST=None, used=None, **kw):
    """ Returns a list of brains from a set of constraints on variables """
    query = self.buildSQLQuery(REQUEST=REQUEST, **kw)
    kw['where_expression'] = query['where_expression']
    kw['sort_on'] = query['order_by_expression']
    kw['from_table_list'] = query['from_table_list']
    # Return the result

    #LOG('acceptable_keys',0,'acceptable_keys: %s' % str(acceptable_keys))
    #LOG('acceptable_key_map',0,'acceptable_key_map: %s' % str(acceptable_key_map))
    #LOG('queryResults',0,'kw: %s' % str(kw))
    #LOG('queryResults',0,'from_table_list: %s' % str(from_table_dict.keys()))
    return sql_method(**kw)

  def searchResults(self, REQUEST=None, used=None, **kw):
    """ Builds a complex SQL where_expression to simulate ZCalatog behaviour """
    """ Returns a list of brains from a set of constraints on variables """
    # The used argument is deprecated and is ignored
    try:
      # Get the search method
      #LOG("searchResults: kw:",0,str(kw))
      method = getattr(self, self.sql_search_results)

      # Return the result
      kw['used'] = used
      kw['REQUEST'] = REQUEST
      return self.queryResults(method, **kw)
    except:
      LOG("Warning: could not search catalog",0,'', error=sys.exc_info())
      return []

  __call__ = searchResults

  def countResults(self, REQUEST=None, used=None, **kw):
    """ Builds a complex SQL where_expression to simulate ZCalatog behaviour """
    """ Returns the number of items which satisfy the where_expression """
    try:
      # Get the search method
      #LOG("countResults: scr:",0,str(self.sql_count_results))
      #LOG("countResults: used:",0,str(used))
      #LOG("countResults: kw:",0,str(kw))
      method = getattr(self, self.sql_count_results)

      # Return the result
      kw['used'] = used
      kw['REQUEST'] = REQUEST
      return self.queryResults(method, **kw)
    except:
      LOG("Warning: could not count catalog",0,str(self.sql_count_results), error=sys.exc_info())
      return [[0]]

class CatalogError(Exception): pass
