##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Jean-Paul Smets-Solane <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
#
# Based on: PropertyManager in OFS
#
##############################################################################


from zLOG import LOG
from string import join

##############################################################################
# Properties
from OFS.PropertyManager import PropertyManager, type_converters

class ERP5PropertyManager(PropertyManager):

  def _updateProperty(self, id, value):
      # Update the value of an existing property. If value
      # is a string, an attempt will be made to convert
      # the value to the type of the existing property.
      self._wrapperCheck(value)
      if not hasattr(self, 'isRADContent'):
        if not self.hasProperty(id):
            raise 'Bad Request', 'The property %s does not exist' % escape(id)
      if type(value)==type(''):
          proptype=self.getPropertyType(id) or 'string'
          if type_converters.has_key(proptype):
              value=type_converters[proptype](value)
      self._setPropValue(id, value)

  def hasProperty(self, id):
      """Return true if object has a property 'id'"""
      for p in self.propertyIds():
          if id==p:
              return 1
      return 0

  def getPropertyType(self, id):
      """Get the type of property 'id', returning None if no
        such property exists"""
      for md in self._propertyMap():
          if md['id']==id:
              return md.get('type', 'string')
      return None

  def _setProperty(self, id, value, type=None):
      # for selection and multiple selection properties
      # the value argument indicates the select variable
      # of the property

      if type is None:
        # Generate a default type
        value_type = type(value)
        if value_type in (type([]), type(())):
          type = 'lines'
        elif value_type is type(1):
          type = 'int'
        elif value_type is type(1L):
          type = 'long'
        elif value_type is type(1.0):
          type = 'float'
        elif value_type is type('a'):
          if len(value_type.split('\n')) > 1:
            type = 'text'
          else:
            type = 'string'
        else:
          type = 'string'

      self._wrapperCheck(value)
      if not self.valid_property_id(id):
          raise 'Bad Request', 'Invalid or duplicate property id'

      if type in ('selection', 'multiple selection'):
          if not hasattr(self, value):
              raise 'Bad Request', 'No select variable %s' % value
          self._local_properties=getattr(self, '_local_properties', ()) + (
              {'id':id, 'type':type, 'select_variable':value},)
          if type=='selection':
              self._setPropValue(id, '')
          else:
              self._setPropValue(id, [])
      else:
          self._local_properties=getattr(self, '_local_properties', ())+({'id':id,'type':type},)
          self._setPropValue(id, value)

  def _delProperty(self, id):
      if not self.hasProperty(id):
          raise ValueError, 'The property %s does not exist' % escape(id)
      self._delPropValue(id)
      self._local_properties=tuple(filter(lambda i, n=id: i['id'] != n,
                                    getattr(self, '_local_properties', ())))

  def propertyIds(self):
      """Return a list of property ids """
      return map(lambda i: i['id'], self._propertyMap())

  def propertyValues(self):
      """Return a list of actual property objects """
      return map(lambda i,s=self: getattr(s,i['id']), self._propertyMap())

  def propertyItems(self):
      """Return a list of (id,property) tuples """
      return map(lambda i,s=self: (i['id'],getattr(s,i['id'])), self._propertyMap())

  def _propertyMap(self):
      """Return a tuple of mappings, giving meta-data for properties """
      return tuple(list(self._properties) + list(getattr(self, '_local_properties', ())))

  def propdict(self):
      dict={}
      for p in self._propertyMap():
          dict[p['id']]=p
      return dict

PropertyManager._updateProperty = ERP5PropertyManager._updateProperty
PropertyManager.getPropertyType = ERP5PropertyManager.getPropertyType
PropertyManager._setProperty = ERP5PropertyManager._setProperty
PropertyManager._delProperty = ERP5PropertyManager._delProperty
PropertyManager.propertyIds = ERP5PropertyManager.propertyIds
PropertyManager.propertyValues = ERP5PropertyManager.propertyValues
PropertyManager.propertyItems = ERP5PropertyManager.propertyItems
PropertyManager._propertyMap = ERP5PropertyManager._propertyMap
PropertyManager.propdict = ERP5PropertyManager.propdict


##############################################################################
# XML content of zsql methods
from Shared.DC.ZRDB.DA import DA

class PatchedDA(DA):

    def fromFile(self, filename):
      """
        Read the file and update self
      """
      f = file(filename)
      s = f.read()
      f.close()
      self.fromText(s)

    def fromText(self, text):
      """
        Read the string 'text' and updates self
      """
      start = text.rfind('<dtml-comment>')
      end = text.rfind('</dtml-comment>')
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
      #print "arguments = %s" % str(arguments)
      self.manage_edit(title=title, connection_id=connection_id,
                       arguments=arguments, template=template)
      self.manage_advanced(max_rows, max_cache, cache_time, class_name, class_file)

    def manage_FTPget(self):
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

DA.fromFile = PatchedDA.fromFile
DA.fromText = PatchedDA.fromText
DA.manage_FTPget = PatchedDA.manage_FTPget

##############################################################################
# Optimized rendering of global actions (cache)

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from AccessControl import getSecurityManager, ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from DocumentTemplate.DT_Util import TemplateDict
from Products.CMFCore.utils import  _getAuthenticatedUser
from time import time

GLOBAL_WORKFLOW_ACTION_CACHE_DURATION = 300
cached_workflow_global_actions = {}
cached_workflow_global_actions_time = {}

class PatchedDCWorkflowDefinition(DCWorkflowDefinition):

    def listGlobalActions(self, info):
        '''
        Allows this workflow to
        include actions to be displayed in the actions box.
        Called on every request.
        Returns the actions to be displayed to the user.
        '''
        # Return Cache
        user = str(_getAuthenticatedUser(self))
        if cached_workflow_global_actions.has_key((user, self.id)):
          if time() - cached_workflow_global_actions_time[(user, self.id)] < GLOBAL_WORKFLOW_ACTION_CACHE_DURATION:
            return cached_workflow_global_actions[(user, self.id)]

        if not self.worklists:
            return None  # Optimization
        sm = getSecurityManager()
        portal = self._getPortalRoot()
        res = []
        fmt_data = None
        for id, qdef in self.worklists.items():
            if qdef.actbox_name:
                guard = qdef.guard
                # Patch for ERP5 by JP Smets in order
                # to implement worklists and search of local roles
                searchres_len = 0
                var_match_keys = qdef.getVarMatchKeys()
                if var_match_keys:
                    # Check the catalog for items in the worklist.
                    catalog = getToolByName(self, 'portal_catalog')
                    dict = {}
                    for k in var_match_keys:
                        v = qdef.getVarMatch(k)
                        v_fmt = map(lambda x, info=info: x%info, v)
                        dict[k] = v_fmt
                    # Patch for ERP5 by JP Smets in order
                    # to implement worklists and search of local roles
                    if not (guard is None or guard.check(sm, self, portal)):
                        dict['local_roles'] = guard.roles
                    # Patch to use ZSQLCatalog and get high speed
                    # LOG("PatchedDCWorkflowDefinition", 0, str(dict))
                    searchres_len = int(apply(catalog.countResults, (), dict)[0][0])
                    if searchres_len == 0:
                        continue
                if fmt_data is None:
                    fmt_data = TemplateDict()
                    fmt_data._push(info)
                fmt_data._push({'count': searchres_len})
                # Patch for ERP5 by JP Smets in order
                # to implement worklists and search of local roles
                if dict.has_key('local_roles'):
                  fmt_data._push({'local_roles': join(guard.roles,';')})
                else:
                  fmt_data._push({'local_roles': ''})
                res.append((id, {'name': qdef.actbox_name % fmt_data,
                                 'url': qdef.actbox_url % fmt_data,
                                 'worklist_id': id,
                                 'workflow_title': self.title,
                                 'workflow_id': self.id,
                                 'permissions': (),  # Predetermined.
                                 'category': qdef.actbox_category}))
                fmt_data._pop()
        res.sort()
        cached_workflow_global_actions[(user, self.id)] = map((lambda (id, val): val), res)
        cached_workflow_global_actions_time[(user, self.id)] = time()
        return cached_workflow_global_actions[(user, self.id)]

DCWorkflowDefinition.listGlobalActions = PatchedDCWorkflowDefinition.listGlobalActions

##############################################################################
# Stribger repair of BTreeFolder2
import sys
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from BTrees.OIBTree import OIBTree, union
from BTrees.Length import Length
from OFS.ObjectManager import BadRequestException, BeforeDeleteException
from zLOG import LOG, INFO, ERROR, WARNING
from Products.ZCatalog.Lazy import LazyMap

class ERP5BTreeFolder2Base (BTreeFolder2Base):

    def _cleanup(self):
        """Cleans up errors in the BTrees.

        Certain ZODB bugs have caused BTrees to become slightly insane.
        Fortunately, there is a way to clean up damaged BTrees that
        always seems to work: make a new BTree containing the items()
        of the old one.

        Returns 1 if no damage was detected, or 0 if damage was
        detected and fixed.
        """
        from BTrees.check import check
        path = '/'.join(self.getPhysicalPath())
        try:
            check(self._tree)
            for key in self._tree.keys():
                if not self._tree.has_key(key):
                    raise AssertionError(
                        "Missing value for key: %s" % repr(key))
            check(self._mt_index)
            for key, object in self._tree.items():
                meta_type = getattr(object, 'meta_type', None)
                if meta_type is not None:
                  if not self._mt_index.has_key(meta_type):
                      raise AssertionError(
                          "Missing meta_type index for key: %s" % repr(key))
            for key, value in self._mt_index.items():
                if (not self._mt_index.has_key(key)
                    or self._mt_index[key] is not value):
                    raise AssertionError(
                        "Missing or incorrect meta_type index: %s"
                        % repr(key))
                check(value)
                for k in value.keys():
                    if not value.has_key(k) or not self._tree.has_key(k):
                        raise AssertionError(
                            "Missing values for meta_type index: %s"
                            % repr(key))
            return 1
        except (AssertionError, KeyError):
            LOG('BTreeFolder2', WARNING,
                'Detected damage to %s. Fixing now.' % path,
                error=sys.exc_info())
            try:
                self._tree = OOBTree(self._tree)
                mt_index = OOBTree()
                for id, object in self._tree.items():
                  # Update the meta type index.
                  meta_type = getattr(object, 'meta_type', None)
                  if meta_type is not None:
                      ids = mt_index.get(meta_type, None)
                      if ids is None:
                          ids = OIBTree()
                          mt_index[meta_type] = ids
                      ids[id] = 1
                LOG('Added All Object in BTree mti',0, map(lambda x:str(x), mt_index.keys()))
                self._mt_index = OOBTree(mt_index)
            except:
                LOG('BTreeFolder2', ERROR, 'Failed to fix %s.' % path,
                    error=sys.exc_info())
                raise
            else:
                LOG('BTreeFolder2', INFO, 'Fixed %s.' % path)
            return 0

BTreeFolder2Base._cleanup = ERP5BTreeFolder2Base._cleanup
