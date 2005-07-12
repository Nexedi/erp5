##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Jean-Paul Smets-Solanes <jp@nexedi.com>
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


from zLOG import LOG, INFO, ERROR, WARNING
from string import join
from DateTime import DateTime

##############################################################################
# Folder naming: member folder should be names as a singular in small caps
from Products.CMFDefault.MembershipTool import MembershipTool
MembershipTool.membersfolder_id = 'member'

##############################################################################
# Import: add rename feature
from OFS.ObjectManager import ObjectManager, customImporters
class PatchedObjectManager(ObjectManager):
    def _importObjectFromFile(self, filepath, verify=1, set_owner=1, id=None):
        #LOG('_importObjectFromFile, filepath',0,filepath)
        # locate a valid connection
        connection=self._p_jar
        obj=self

        while connection is None:
            obj=obj.aq_parent
            connection=obj._p_jar
        ob=connection.importFile(
            filepath, customImporters=customImporters)
        if verify: self._verifyObjectPaste(ob, validate_src=0)
        if id is None:
          id=ob.id
        if hasattr(id, 'im_func'): id=id()
        self._setObject(id, ob, set_owner=set_owner)

        # try to make ownership implicit if possible in the context
        # that the object was imported into.
        ob=self._getOb(id)
        ob.manage_changeOwnershipType(explicit=0)

ObjectManager._importObjectFromFile=PatchedObjectManager._importObjectFromFile

##############################################################################
# Properties
from OFS.PropertyManager import PropertyManager, type_converters
from OFS.PropertyManager import escape
from Globals import DTMLFile
from Products.ERP5Type.Utils import createExpressionContext
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.CMFCore.Expression import Expression

class ERP5PropertyManager(PropertyManager):

  manage_propertiesForm=DTMLFile('dtml/properties', globals(),
                                  property_extensible_schema__=1)


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
      #LOG('_updateProperty', 0, 'self = %r, id = %r, value = %r' % (self, id, value))
      self._setPropValue(id, value)

  def hasProperty(self, id):
      """Return true if object has a property 'id'"""
      for p in self.propertyIds():
          if id==p:
              return 1
      return 0

  def getProperty(self, id, d=None, evaluate=1):
      """Get the property 'id', returning the optional second
          argument or None if no such property is found."""
      type = self.getPropertyType(id)
      if evaluate and type == 'tales':
          value = getattr(self, id)
          expression = Expression(value)
          econtext = createExpressionContext(self)
          return expression(econtext)
      elif type:
        return getattr(self, id)
      return d

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

  def manage_addProperty(self, id, value, type, REQUEST=None):
      """Add a new property via the web. Sets a new property with
      the given id, type, and value."""
      if type_converters.has_key(type):
          value=type_converters[type](value)
      #LOG('manage_addProperty', 0, 'id = %r, value = %r, type = %r, REQUEST = %r' % (id, value, type, REQUEST))
      self._setProperty(id.strip(), value, type)
      if REQUEST is not None:
          return self.manage_propertiesForm(self, REQUEST)

PropertyManager.manage_addProperty = ERP5PropertyManager.manage_addProperty
PropertyManager.manage_propertiesForm = ERP5PropertyManager.manage_propertiesForm
PropertyManager._updateProperty = ERP5PropertyManager._updateProperty
PropertyManager.getPropertyType = ERP5PropertyManager.getPropertyType
PropertyManager._setProperty = ERP5PropertyManager._setProperty
PropertyManager._delProperty = ERP5PropertyManager._delProperty
PropertyManager.propertyIds = ERP5PropertyManager.propertyIds
PropertyManager.propertyValues = ERP5PropertyManager.propertyValues
PropertyManager.propertyItems = ERP5PropertyManager.propertyItems
PropertyManager._propertyMap = ERP5PropertyManager._propertyMap
PropertyManager.propdict = ERP5PropertyManager.propdict
PropertyManager.hasProperty = ERP5PropertyManager.hasProperty
PropertyManager.getProperty = ERP5PropertyManager.getProperty
ERP5TypeInformation.manage_propertiesForm = ERP5PropertyManager.manage_propertiesForm

from ZPublisher.Converters import type_converters, field2string

type_converters['tales'] = field2string

##############################################################################
# XML content of zsql methods
import re
try: from IOBTree import Bucket
except: Bucket=lambda:{}
from Shared.DC.ZRDB.Aqueduct import decodestring, parse
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

    # This function doesn't take care about properties by default
    def PUT(self, REQUEST, RESPONSE):
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


DA.fromFile = PatchedDA.fromFile
DA.fromText = PatchedDA.fromText
DA.manage_FTPget = PatchedDA.manage_FTPget
DA.PUT = PatchedDA.PUT

##############################################################################
# Optimized rendering of global actions (cache)

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from AccessControl import getSecurityManager, ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from DocumentTemplate.DT_Util import TemplateDict
from Products.CMFCore.utils import  _getAuthenticatedUser
from time import time
from Products.ERP5Type.Cache import CachingMethod

class PatchedDCWorkflowDefinition(DCWorkflowDefinition):

    def listGlobalActions(self, info):
        '''
        Allows this workflow to
        include actions to be displayed in the actions box.
        Called on every request.
        Returns the actions to be displayed to the user.
        '''
        def _listGlobalActions(user=None, id=None, portal_path=None):
          if not self.worklists:
              return None  # Optimization
          sm = getSecurityManager()
          portal = self._getPortalRoot()
          res = []
          fmt_data = None
          # We want to display some actions depending on the current date
          # So, we can now put this kind of expression : <= "%(now)s"
          # May be this patch should be moved to listFilteredActions in the future
          info.now = DateTime()
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
                      # LOG("PatchedDCWorkflowDefinition", 0, dict)
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
          return map((lambda (id, val): val), res)

        # Return Cache
        _listGlobalActions = CachingMethod(_listGlobalActions, id='listGlobalActions', cache_duration = 300)
        user = str(_getAuthenticatedUser(self))
        return _listGlobalActions(user=user, id=self.id, portal_path=self._getPortalRoot().getPhysicalPath())


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
                #LOG('Added All Object in BTree mti',0, map(lambda x:str(x), mt_index.keys()))
                self._mt_index = OOBTree(mt_index)
            except:
                LOG('BTreeFolder2', ERROR, 'Failed to fix %s.' % path,
                    error=sys.exc_info())
                raise
            else:
                LOG('BTreeFolder2', INFO, 'Fixed %s.' % path)
            return 0

BTreeFolder2Base._cleanup = ERP5BTreeFolder2Base._cleanup

##############################################################################
# Stribger repair of BTreeFolder2

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition, StateChangeInfo, ObjectMoved, createExprContext, aq_parent, aq_inner
from Products.DCWorkflow import DCWorkflow
from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.ERP5Type.Utils import convertToMixedCase

class ValidationFailed(Exception):
    """Transition can not be executed because data is not in consistent state"""

DCWorkflow.ValidationFailed = ValidationFailed

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products.DCWorkflow.DCWorkflow').declarePublic('ValidationFailed')


class ERP5DCWorkflowDefinition (DCWorkflowDefinition):

    def _executeTransition(self, ob, tdef=None, kwargs=None):
        '''
        Private method.
        Puts object in a new state.
        '''
        sci = None
        econtext = None
        moved_exc = None

        # Figure out the old and new states.
        old_sdef = self._getWorkflowStateOf(ob)
        old_state = old_sdef.getId()
        if tdef is None:
            new_state = self.initial_state
            former_status = {}
        else:
            new_state = tdef.new_state_id
            if not new_state:
                # Stay in same state.
                new_state = old_state
            former_status = self._getStatusOf(ob)
        new_sdef = self.states.get(new_state, None)
        if new_sdef is None:
            raise WorkflowException, (
                'Destination state undefined: ' + new_state)

        # Execute the "before" script.
        before_script_success = 1
        if tdef is not None and tdef.script_name:
            script = self.scripts[tdef.script_name]
            # Pass lots of info to the script in a single parameter.
            sci = StateChangeInfo(
                ob, self, former_status, tdef, old_sdef, new_sdef, kwargs)
            try:
                #LOG('_executeTransition', 0, "script = %s, sci = %s" % (repr(script), repr(sci)))
                script(sci)  # May throw an exception.
            except ValidationFailed, validation_exc:
                before_script_success = 0
                before_script_error_message = validation_exc
            except ObjectMoved, moved_exc:
                ob = moved_exc.getNewObject()
                # Re-raise after transition

        # Update variables.
        state_values = new_sdef.var_values
        if state_values is None: state_values = {}
        tdef_exprs = None
        if tdef is not None: tdef_exprs = tdef.var_exprs
        if tdef_exprs is None: tdef_exprs = {}
        status = {}
        for id, vdef in self.variables.items():
            if not vdef.for_status:
                continue
            expr = None
            if state_values.has_key(id):
                value = state_values[id]
            elif tdef_exprs.has_key(id):
                expr = tdef_exprs[id]
            elif not vdef.update_always and former_status.has_key(id):
                # Preserve former value
                value = former_status[id]
            else:
                if vdef.default_expr is not None:
                    expr = vdef.default_expr
                else:
                    value = vdef.default_value
            if expr is not None:
                # Evaluate an expression.
                if econtext is None:
                    # Lazily create the expression context.
                    if sci is None:
                        sci = StateChangeInfo(
                            ob, self, former_status, tdef,
                            old_sdef, new_sdef, kwargs)
                    econtext = createExprContext(sci)
                value = expr(econtext)
            status[id] = value

        # Do not proceed in case of failure of before script
        if not before_script_success:
            status[self.state_var] = old_state # Remain in state
            tool = aq_parent(aq_inner(self))
            tool.setStatusOf(self.id, ob, status)
            sci = StateChangeInfo(
                ob, self, status, tdef, old_sdef, new_sdef, kwargs)
            sci.setWorkflowVariable(ob, workflow_id=self.id, error_message = before_script_error_message)
            return new_sdef

        # Update state.
        status[self.state_var] = new_state
        tool = aq_parent(aq_inner(self))
        tool.setStatusOf(self.id, ob, status)

        # Make sure that the error message is empty. # Why ?
        #sci = StateChangeInfo(
        #    ob, self, status, tdef, old_sdef, new_sdef, kwargs)
        #sci.setWorkflowVariable(ob, error_message = '')

        # Update role to permission assignments.
        self.updateRoleMappingsFor(ob)

        # Execute the "after" script.
        if tdef is not None and tdef.after_script_name:
            # Script can be either script or workflow method
            #LOG('_executeTransition', 0, 'new_sdef.transitions = %s' % (repr(new_sdef.transitions)))
            if tdef.after_script_name in filter(lambda k: self.transitions[k].trigger_type == TRIGGER_WORKFLOW_METHOD,
                                                                                     new_sdef.transitions):
              script = getattr(ob, convertToMixedCase(tdef.after_script_name))
              script()
            else:
              script = self.scripts[tdef.after_script_name]
              # Pass lots of info to the script in a single parameter.
              sci = StateChangeInfo(
                  ob, self, status, tdef, old_sdef, new_sdef, kwargs)
              script(sci)  # May throw an exception.

        # Return the new state object.
        if moved_exc is not None:
            # Propagate the notification that the object has moved.
            raise moved_exc
        else:
            return new_sdef


DCWorkflowDefinition._executeTransition = ERP5DCWorkflowDefinition._executeTransition

# This patch allows to use workflowmethod as an after_script
# However, the right way of doing would be to have a combined state of TRIGGER_USER_ACTION and TRIGGER_WORKFLOW_METHOD
# as well as workflow inheritance. This way, different user actions and dialogs can be specified easliy
# For now, we split UI transitions and logics transitions so that UI can be different and logics the same
from Products.DCWorkflow.Transitions import TransitionDefinition

class ERP5TransitionDefinition (TransitionDefinition):

    def getAvailableScriptIds(self):
        return self.getWorkflow().scripts.keys() +  filter(
          lambda k: self.getWorkflow().transitions[k].trigger_type == TRIGGER_WORKFLOW_METHOD, self.getWorkflow().transitions.keys())

TransitionDefinition.getAvailableScriptIds = ERP5TransitionDefinition.getAvailableScriptIds

##############################################################################
# Adding commit_prepare to the zodb transaction
from ZODB import Transaction

#class ERP5Transaction(Transaction):

hosed = Transaction.hosed
free_transaction = Transaction.free_transaction
jar_cmp = Transaction.jar_cmp

def commit(self, subtransaction=None):
    """Finalize the transaction."""
    objects = self._objects

    subjars = []
    if subtransaction:
        if self._sub is None:
            # Must store state across multiple subtransactions
            # so that the final commit can commit all subjars.
            self._sub = {}
    else:
        if self._sub is not None:
            # This commit is for a top-level transaction that
            # has previously committed subtransactions.  Do
            # one last subtransaction commit to clear out the
            # current objects, then commit all the subjars.
            if objects:
                self.commit(1)
                objects = []
            subjars = self._sub.values()
            subjars.sort(jar_cmp)
            self._sub = None

            # If there were any non-subtransaction-aware jars
            # involved in earlier subtransaction commits, we need
            # to add them to the list of jars to commit.
            if self._non_st_objects is not None:
                objects.extend(self._non_st_objects)
                self._non_st_objects = None

    if (objects or subjars) and hosed:
        # Something really bad happened and we don't
        # trust the system state.
        raise POSException.TransactionError, hosed_msg

    # It's important that:
    #
    # - Every object in self._objects is either committed or
    #   aborted.
    #
    # - For each object that is committed we call tpc_begin on
    #   it's jar at least once
    #
    # - For every jar for which we've called tpc_begin on, we
    #   either call tpc_abort or tpc_finish. It is OK to call
    #   these multiple times, as the storage is required to ignore
    #   these calls if tpc_begin has not been called.
    #
    # - That we call tpc_begin() in a globally consistent order,
    #   so that concurrent transactions involving multiple storages
    #   do not deadlock.
    try:
        ncommitted = 0
        # Do prepare until number of jars is stable - this could
        # create infinite loop
        jars_len = -1
        jars = self._get_jars(objects, subtransaction)
        while len(jars) != jars_len:
          jars_len = len(jars)
          self._commit_prepare(jars, subjars, subtransaction)
          jars = self._get_jars(objects, subtransaction)
        try:
            # If not subtransaction, then jars will be modified.
            self._commit_begin(jars, subjars, subtransaction)
            ncommitted += self._commit_objects(objects)
            if not subtransaction:
                # Unless this is a really old jar that doesn't
                # implement tpc_vote(), it must raise an exception
                # if it can't commit the transaction.
                for jar in jars:
                    try:
                        vote = jar.tpc_vote
                    except AttributeError:
                        pass
                    else:
                        vote(self)

            # Handle multiple jars separately.  If there are
            # multiple jars and one fails during the finish, we
            # mark this transaction manager as hosed.
            if len(jars) == 1:
                self._finish_one(jars[0])
            else:
                self._finish_many(jars)
        except:
            # Ugh, we got an got an error during commit, so we
            # have to clean up.  First save the original exception
            # in case the cleanup process causes another
            # exception.
            error = sys.exc_info()
            try:
                self._commit_error(objects, ncommitted, jars, subjars)
            except:
                LOG('ZODB', ERROR,
                    "A storage error occured during transaction "
                    "abort.  This shouldn't happen.",
                    error=error)
            raise error[0], error[1], error[2]
    finally:
        del objects[:] # clear registered
        if not subtransaction and self._id is not None:
            free_transaction()

def _commit_prepare(self, jars, subjars, subtransaction):
    if subtransaction:
        assert not subjars
        for jar in jars:
            try:
                jar.tpc_prepare(self, subtransaction)
            except TypeError:
                # Assume that TypeError means that tpc_begin() only
                # takes one argument, and that the jar doesn't
                # support subtransactions.
                jar.tpc_prepare(self)
            except AttributeError:
                # Assume that KeyError means that tpc_prepare
                # not available
                pass
    else:
        # Merge in all the jars used by one of the subtransactions.

        # When the top-level subtransaction commits, the tm must
        # call commit_sub() for each jar involved in one of the
        # subtransactions.  The commit_sub() method should call
        # tpc_begin() on the storage object.

        # It must also call tpc_begin() on jars that were used in
        # a subtransaction but don't support subtransactions.

        # These operations must be performed on the jars in order.

        # Modify jars inplace to include the subjars, too.
        jars += subjars
        jars.sort(jar_cmp)
        # assume that subjars is small, so that it's cheaper to test
        # whether jar in subjars than to make a dict and do has_key.
        for jar in jars:
            #if jar in subjars:
            #  pass
            #else:
            try:
                jar.tpc_prepare(self)
            except AttributeError:
                # Assume that KeyError means that tpc_prepare
                # not available
                pass

Transaction.Transaction.commit = commit
Transaction.Transaction._commit_prepare = _commit_prepare



##############################################################################
# Make sure Interaction Workflows are called even if method not wrapped

from Products.CMFCore.WorkflowTool import WorkflowTool

class ERP5WorkflowTool(WorkflowTool):

    def wrapWorkflowMethod(self, ob, method_id, func, args, kw):

        """ To be invoked only by WorkflowCore.
            Allows a workflow definition to wrap a WorkflowMethod.

            By default, the workflow tool takes the first workflow wich
            support the method_id. In ERP5, with Interaction Worfklows, we
            may have many workflows wich can support a worfklow method,
            that's why we need this patch

            We should have 1 or 0 classic workflow (ie a DCWorkflow), and
            0 or many Interaction workflows. We should take care that the
            method will be called once
        """
        wf_list = []
        wfs = self.getWorkflowsFor(ob)
        if wfs:
            for w in wfs:
                #LOG('ERP5WorkflowTool.wrapWorkflowMethod, is wfMSupported', 0, repr(( w.isWorkflowMethodSupported(ob, method_id), w.getId(), ob, method_id )))
                if (hasattr(w, 'isWorkflowMethodSupported')
                    and w.isWorkflowMethodSupported(ob, method_id)):
                    #wf = w
                    #break
                    wf_list.append(w)
        else:
            wfs = ()
        if len(wf_list)==0:
            return apply(func, args, kw)
        no_interaction = 0
        for w in wf_list:
          if w.__class__.__name__ != 'InteractionWorkflowDefinition':
            no_interaction = 1
        for w in wfs:
            w.notifyBefore(ob, method_id, args=args, kw=kw)
        # Check if there is at least 1 non interaction workflow
        if no_interaction:
          for w in wf_list:
             if w.__class__.__name__ != 'InteractionWorkflowDefinition':
              result = self._invokeWithNotification(
                  [], ob, method_id, w.wrapWorkflowMethod,
                  (ob, method_id, func, args, kw), {})
        else:
          result = apply(func, args, kw)
        for w in wfs:
            w.notifySuccess(ob, method_id, result, args=args, kw=kw)

WorkflowTool.wrapWorkflowMethod = ERP5WorkflowTool.wrapWorkflowMethod

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition

class ERP5DCWorkflow(DCWorkflowDefinition):

    def notifyBefore(self, ob, action, args=None, kw=None):
        '''
        Notifies this workflow of an action before it happens,
        allowing veto by exception.  Unless an exception is thrown, either
        a notifySuccess() or notifyException() can be expected later on.
        The action usually corresponds to a method name.
        '''
        pass

    def notifySuccess(self, ob, action, result, args=None, kw=None):
        '''
        Notifies this workflow that an action has taken place.
        '''
        pass

DCWorkflowDefinition.notifyBefore = ERP5DCWorkflow.notifyBefore
DCWorkflowDefinition.notifySuccess = ERP5DCWorkflow.notifySuccess

##############################################################################
# Make sure the xml export will be ordered

from Shared.DC.xml import ppml
from base64 import encodestring
from cStringIO import StringIO
from ZODB.referencesf import referencesf
from ZODB.ExportImport import TemporaryFile
from pickle import Pickler, EMPTY_DICT, MARK, DICT
from cPickle import loads, dumps
from types import *

# Jython has PyStringMap; it's a dict subclass with string keys
try:
    from org.python.core import PyStringMap
except ImportError:
    PyStringMap = None

# Ordered pickles
class OrderedPickler(Pickler):

    dispatch = Pickler.dispatch.copy()

    def save_dict(self, obj):
        write = self.write

        if self.bin:
            write(EMPTY_DICT)
        else:   # proto 0 -- can't use EMPTY_DICT
            write(MARK + DICT)

        self.memoize(obj)
        item_list = obj.items() # New version by JPS for sorting
        item_list.sort(lambda a, b: cmp(a[0], b[0])) # New version by JPS for sorting
        self._batch_setitems(item_list.__iter__())

    dispatch[DictionaryType] = save_dict
    if not PyStringMap is None:
        dispatch[PyStringMap] = save_dict

def reorderPickle(jar, p):
    from ZODB.ExportImport import Ghost, Unpickler, Pickler, StringIO, persistent_id

    oids = {}
    storage = jar._storage
    new_oid = storage.new_oid
    store = storage.store

    def persistent_load(ooid,
                        Ghost=Ghost,
                        oids=oids, wrote_oid=oids.has_key,
                        new_oid=storage.new_oid):

        "Remap a persistent id to an existing ID and create a ghost for it."

        if type(ooid) is TupleType: ooid, klass = ooid
        else: klass=None

        Ghost=Ghost()
        Ghost.oid=ooid
        return Ghost


    # Reorder pickle by doing I/O
    pfile = StringIO(p)
    unpickler=Unpickler(pfile)
    unpickler.persistent_load=persistent_load

    newp=StringIO()
    pickler=OrderedPickler(newp,1)
    pickler.persistent_id=persistent_id

    pickler.dump(unpickler.load())
    obj = unpickler.load()
    pickler.dump(obj)
    p=newp.getvalue()
    return obj, p

def XMLrecord(oid, plen, p, id_mapping):
    # Proceed as usual
    q=ppml.ToXMLUnpickler
    f=StringIO(p)
    u=q(f)
    id=ppml.u64(oid)
    id = id_mapping[id]
    old_aka = encodestring(oid)[:-1]
    aka=encodestring(ppml.p64(long(id)))[:-1]  # Rebuild oid based on mapped id
    id_mapping.setConvertedAka(old_aka, aka)
    u.idprefix=str(id)+'.'
    p=u.load(id_mapping=id_mapping).__str__(4)
    if f.tell() < plen:
        p=p+u.load(id_mapping=id_mapping).__str__(4)
    String='  <record id="%s" aka="%s">\n%s  </record>\n' % (id, aka, p)
    return String

from OFS import XMLExportImport
XMLExportImport.XMLrecord = XMLrecord

def exportXML(jar, oid, file=None):

    if file is None: file=TemporaryFile()
    elif type(file) is StringType: file=open(file,'w+b')
    id_mapping = ppml.MinimalMapping()
    #id_mapping = ppml.IdentityMapping()
    write=file.write
    write('<?xml version="1.0"?>\012<ZopeData>\012')
    version=jar._version
    ref=referencesf
    oids=[oid]
    done_oids={}
    done=done_oids.has_key
    load=jar._storage.load
    original_oid = oid
    reordered_pickle = []
    # Build mapping for refs
    while oids:
        oid=oids[0]
        del oids[0]
        if done(oid): continue
        done_oids[oid]=1
        try: p, serial = load(oid, version)
        except: pass # Ick, a broken reference
        else:
            o, p = reorderPickle(jar, p)
            reordered_pickle.append((oid, o, p))
            XMLrecord(oid,len(p),p, id_mapping)
            # Determine new oids added to the list after reference calculation
            old_oids = tuple(oids)
            ref(p, oids)
            new_oids = []
            for i in oids:
                if i not in old_oids: new_oids.append(i)
            # Sort new oids based on id of object
            new_oidict = {}
            for oid in new_oids:
                try:
                    p, serial = load(oid, version)
                    o, p = reorderPickle(jar, p)
                    new_oidict[oid] = getattr(o, 'id', None)
                except:
                    new_oidict[oid] = None # Ick, a broken reference
            new_oids.sort(lambda a,b: cmp(new_oidict[a], new_oidict[b]))
            # Build new sorted oids
            oids = list(old_oids) + new_oids
    # Do real export
    for (oid, o, p) in reordered_pickle:
        write(XMLrecord(oid,len(p),p, id_mapping))
    write('</ZopeData>\n')
    return file

XMLExportImport.exportXML = exportXML

######################################################################################
# Shared/DC/xml/ppml patch

# Import everything right now, not after
# or new patch will not work
from Shared.DC.xml.ppml import *

class Global:

    def __init__(self, module, name, mapping):
        self.module=module
        self.name=name
        self.mapping = mapping

    def __str__(self, indent=0):
        id = ''
        if hasattr(self, 'id'):
            if self.mapping.isMarked(self.id): id=' id="%s"' % self.mapping[self.id]
        name=string.lower(self.__class__.__name__)
        return '%s<%s%s name="%s" module="%s"/>\n' % (
            ' '*indent, name, id, self.name, self.module)

from Shared.DC.xml import ppml
ppml.Global = Global

class Scalar:

    def __init__(self, v, mapping):
        self._v=v
        self.mapping = mapping

    def value(self): return self._v

    def __str__(self, indent=0):
        id = ''
        name=string.lower(self.__class__.__name__)
        result = '%s<%s%s>%s</%s>\n' % (
            ' '*indent, name, id, self.value(), name)
        if hasattr(self, 'id'):
            # The value is Immutable - let us add it the the immutable mapping
            # to reduce the number of unreadable references
            self.mapping.setImmutable(self.id, Immutable(value = result))
        return result

ppml.Scalar = Scalar

class Immutable:
    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

class String(Scalar):
    def __init__(self, v, mapping, encoding=''):
        encoding, v = convert(v)
        self.encoding=encoding
        self._v=v
        self.mapping = mapping
    def __str__(self,indent=0,map_value=0):
        v = self.value()
        if map_value:
            # This is used when strings represent references which need to be converted
            if self.encoding == 'base64':
                v = self.mapping.convertBase64(v)
            else:
                # Make sure we never produce this kind of xml output
                raise
        id = ''
        encoding=''
        if hasattr(self, 'encoding'):
            if self.encoding != 'repr':
                # JPS repr is default encoding
                encoding=' encoding="%s"' % self.encoding
        name=string.lower(self.__class__.__name__)
        result = '%s<%s%s%s>%s</%s>\n' % (
            ' '*indent, name, id, encoding, v, name)
        if hasattr(self, 'id'):
            # The value is Immutable - let us add it the the immutable mapping
            # to reduce the number of unreadable references
            self.mapping.setImmutable(self.id, Immutable(value = result))
        return result

ppml.String = String

class Unicode(String):
    def value(self):
        return self._v.encode('utf-8')

ppml.Unicode = Unicode

class Wrapper:

    def __init__(self, v, mapping):
        self._v=v
        self.mapping = mapping

    def value(self): return self._v

    def __str__(self, indent=0):
        id = ''
        if hasattr(self, 'id'):
            if self.mapping.isMarked(self.id): id=' id="%s"' % self.mapping[self.id]
        name=string.lower(self.__class__.__name__)
        v=self._v
        i=' '*indent
        if isinstance(v,Scalar):
            return '%s<%s%s> %s </%s>\n' % (i, name, id, str(v)[:-1], name)
        else:
            v=v.__str__(indent+2)
            return '%s<%s%s>\n%s%s</%s>\n' % (i, name, id, v, i, name)

ppml.Wrapper = Wrapper

class Collection:

    def __init__(self, mapping):
        self.mapping = mapping

    def __str__(self, indent=0):
        id = ''
        if hasattr(self, 'id'):
            if self.mapping.isMarked(self.id): id=' id="%s"' % self.mapping[self.id]
        name=string.lower(self.__class__.__name__)
        i=' '*indent
        if self:
            return '%s<%s%s>\n%s%s</%s>\n' % (
                i, name, id, self.value(indent+2), i, name)
        else:
            return '%s<%s%s/>\n' % (i, name, id)

ppml.Collection = Collection

class Dictionary(Collection):
    def __init__(self, mapping):
        self.mapping = mapping
        self._d=[]
    def __len__(self): return len(self._d)
    def __setitem__(self, k, v): self._d.append((k,v))
    def value(self, indent):
        #self._d.sort(lambda a, b: cmp(a[0]._v, b[0]._v)) # Sort the sequence by key JPS Improvement
        return string.join(
            map(lambda i, ind=' '*indent, indent=indent+4:
                '%s<item>\n'
                '%s'
                '%s'
                '%s</item>\n'
                %
                (ind,
                 Key(i[0], self.mapping).__str__(indent),
                 Value(i[1], self.mapping).__str__(indent),
                 ind),
                self._d
                ),
            '')

ppml.Dictionary = Dictionary

class Sequence(Collection):

    def __init__(self, mapping, v=None):
        if not v: v=[]
        self._subs=v
        self.mapping = mapping

    def __len__(self): return len(self._subs)

    def append(self, v): self._subs.append(v)

    # Bugfix JPS
    def extend(self, v): self._subs.extend(v)

    def value(self, indent):
        return string.join(map(
            lambda v, indent=indent: v.__str__(indent),
            self._subs),'')

ppml.Sequence = Sequence

class Persistent(Wrapper):

    def __str__(self, indent=0):
        id = ''
        if hasattr(self, 'id'):
            if self.mapping.isMarked(self.id): id=' id="%s"' % self.mapping[self.id]
        name=string.lower(self.__class__.__name__)
        v=self._v
        i=' '*indent
        if isinstance(v,String):
            return '%s<%s%s> %s </%s>\n' % (i, name, id, v.__str__(map_value=1)[:-1], name)
        elif isinstance(v,Scalar):
            return '%s<%s%s> %s </%s>\n' % (i, name, id, str(v)[:-1], name)
        else:
            v=v.__str__(indent+2)
            return '%s<%s%s>\n%s%s</%s>\n' % (i, name, id, v, i, name)

ppml.Persistent = Persistent

class Reference(Scalar):
    def __init__(self, v, mapping):
        self._v=v
        self.mapping = mapping
    def __str__(self, indent=0):
        v=self._v
        name=string.lower(self.__class__.__name__)
        #LOG('Reference', 0, str(v))
        if self.mapping.hasImmutable(v):
          return self.mapping.getImmutable(v).getValue()
        #LOG('noImmutable', 0, "%s mapped to %s" % (v, self.mapping[v]))
        self.mapping.mark(v)
        return '%s<%s id="%s"/>\n' % (' '*indent,name,self.mapping[v])

ppml.Reference = Reference
Get = Reference
ppml.Get = Get

class Object(Sequence):
    def __init__(self, klass, args, mapping):
        self._subs=[Klass(klass, mapping), args]
        self.mapping = mapping

    def __setstate__(self, v): self.append(State(v, self.mapping))

ppml.Object = Object

class IdentityMapping:

    def __init__(self):
      self.immutable = {}

    def resetMapping(self):
      pass

    def __getitem__(self, id):
      return id

    def setConvertedAka(self, old, new):
      pass

    def convertBase64(self, s):
      return s

    def mark(self, v):
      pass

    def isMarked(self, v):
      return 1

    def setImmutable(self, k, v):
      self.immutable[k] = v

    def getImmutable(self, k):
      return self.immutable[k]

    def hasImmutable(self, k):
      return self.immutable.has_key(k)


ppml.IdentityMapping = IdentityMapping

class MinimalMapping(IdentityMapping):
    def __init__(self):
      self.mapped_id = {}
      self.mapped_core_id = {}
      self.last_sub_id = {}
      self.last_id = 1
      self.converted_aka = {}
      self.marked_reference = {}
      self.immutable = {}

    def resetMapping(self):
      self.mapped_id = {}
      self.mapped_core_id = {}
      self.last_sub_id = {}
      self.last_id = 1
      self.converted_aka = {}
      self.marked_reference = {}

    def __getitem__(self, id):
      id = str(id)
      split_id = id.split('.')
      if len(split_id) == 2:
        (core_id, sub_id) = split_id
      elif len(split_id) == 1:
        core_id = split_id[0]
        sub_id = None
      else:
        raise
      if not self.mapped_id.has_key(core_id):
        if sub_id is not None:
          # Use existing id
          self.mapped_id[core_id] = {}
          self.mapped_core_id[core_id] = self.last_id - 1
          self.last_sub_id[core_id] = 1
        else:
          # Create new core_id if not defined
          self.mapped_id[core_id] = {}
          self.mapped_core_id[core_id] = self.last_id
          self.last_sub_id[core_id] = 1
          self.last_id = self.last_id + 1
      if sub_id is None:
        return self.mapped_core_id[core_id]
      if not self.mapped_id[core_id].has_key(sub_id):
        # Create new sub_id if not defined
        self.mapped_id[core_id][sub_id] = self.last_sub_id[core_id]
        self.last_sub_id[core_id] = self.last_sub_id[core_id] + 1
      return "%s.%s" % (self.mapped_core_id[core_id], self.mapped_id[core_id][sub_id])

    def convertBase64(self, s):
      return self.converted_aka.get(s, s)

    def setConvertedAka(self, old, new):
      self.converted_aka[old] =  new

    def mark(self, v):
      self.marked_reference[v] = 1

    def isMarked(self, v):
      return self.marked_reference.has_key(v)

    def __str__(self, a):
      return "Error here"

ppml.MinimalMapping = MinimalMapping

class List(Sequence): pass
class Tuple(Sequence): pass

class Klass(Wrapper): pass
class State(Wrapper): pass
class Pickle(Wrapper): pass

class Int(Scalar): pass
class Float(Scalar): pass

class Key(Wrapper): pass
class Value(Wrapper): pass

class Long(Scalar):
    def value(self):
        result = str(self._v)
        if result[-1:] == 'L':
            return result[:-1]
        return result

class ToXMLUnpickler(Unpickler):

    def load(self, id_mapping=None):
      if id_mapping is None:
        self.id_mapping = IdentityMapping()
      else:
        self.id_mapping = id_mapping
      return Pickle(Unpickler.load(self), self.id_mapping)

    dispatch = {}
    dispatch.update(Unpickler.dispatch)

    def persistent_load(self, v):
        return Persistent(v, self.id_mapping)

    def load_persid(self):
        pid = self.readline()[:-1]
        self.append(self.persistent_load(String(pid, self.id_mapping)))
    dispatch[PERSID] = load_persid

    def load_none(self):
        self.append(none)
    dispatch[NONE] = load_none

    def load_int(self):
        self.append(Int(string.atoi(self.readline()[:-1]), self.id_mapping))
    dispatch[INT] = load_int

    def load_binint(self):
        self.append(Int(mloads('i' + self.read(4)), self.id_mapping))
    dispatch[BININT] = load_binint

    def load_binint1(self):
        self.append(Int(mloads('i' + self.read(1) + '\000\000\000'), self.id_mapping))
    dispatch[BININT1] = load_binint1

    def load_binint2(self):
        self.append(Int(mloads('i' + self.read(2) + '\000\000'), self.id_mapping))
    dispatch[BININT2] = load_binint2

    def load_long(self):
        self.append(Long(string.atol(self.readline()[:-1], 0), self.id_mapping))
    dispatch[LONG] = load_long

    def load_float(self):
        self.append(Float(string.atof(self.readline()[:-1]), self.id_mapping))
    dispatch[FLOAT] = load_float

    def load_binfloat(self, unpack=struct.unpack):
        self.append(Float(unpack('>d', self.read(8))[0], self.id_mapping))
    dispatch[BINFLOAT] = load_binfloat

    def load_string(self):
        self.append(String(eval(self.readline()[:-1],
                                {'__builtins__': {}}), self.id_mapping)) # Let's be careful
    dispatch[STRING] = load_string

    def load_binstring(self):
        len = mloads('i' + self.read(4))
        self.append(String(self.read(len), self.id_mapping))
    dispatch[BINSTRING] = load_binstring

    def load_unicode(self):
        self.append(Unicode(unicode(eval(self.readline()[:-1],
                                         {'__builtins__': {}})), self.id_mapping)) # Let's be careful
    dispatch[UNICODE] = load_unicode

    def load_binunicode(self):
        len = mloads('i' + self.read(4))
        self.append(Unicode(unicode(self.read(len), 'utf-8'), self.id_mapping))
    dispatch[BINUNICODE] = load_binunicode

    def load_short_binstring(self):
        len = mloads('i' + self.read(1) + '\000\000\000')
        self.append(String(self.read(len), self.id_mapping))
    dispatch[SHORT_BINSTRING] = load_short_binstring

    def load_tuple(self):
        k = self.marker()
        #LOG('load_tuple, k',0,k)
        #LOG('load_tuple, stack[k+1:]',0,self.stack[k+1:])
        self.stack[k:] = [Tuple(self.id_mapping, v=self.stack[k+1:])]
    dispatch[TUPLE] = load_tuple

    def load_empty_tuple(self):
        self.stack.append(Tuple(self.id_mapping))
    dispatch[EMPTY_TUPLE] = load_empty_tuple

    def load_empty_list(self):
        self.stack.append(List(self.id_mapping))
    dispatch[EMPTY_LIST] = load_empty_list

    def load_empty_dictionary(self):
        self.stack.append(Dictionary(self.id_mapping))
    dispatch[EMPTY_DICT] = load_empty_dictionary

    def load_list(self):
        k = self.marker()
        self.stack[k:] = [List(self.id_mapping, v=self.stack[k+1:])]
    dispatch[LIST] = load_list

    def load_dict(self):
        k = self.marker()
        d = Dictionary(self.id_mapping)
        items = self.stack[k+1:]
        for i in range(0, len(items), 2):
            key = items[i]
            value = items[i+1]
            d[key] = value
        self.stack[k:] = [d]
    dispatch[DICT] = load_dict

    def load_inst(self):
        k = self.marker()
        args = Tuple(self.id_mapping, v=self.stack[k+1:])
        del self.stack[k:]
        module = self.readline()[:-1]
        name = self.readline()[:-1]
        value=Object(Global(module, name, self.id_mapping), args, self.id_mapping)
        self.append(value)
    dispatch[INST] = load_inst

    def load_obj(self):
        stack = self.stack
        k = self.marker()
        klass = stack[k + 1]
        del stack[k + 1]
        args = Tuple(self.id_mapping, v=stack[k + 1:])
        del stack[k:]
        value=Object(klass,args, self.id_mapping)
        self.append(value)
    dispatch[OBJ] = load_obj

    def load_global(self):
        module = self.readline()[:-1]
        name = self.readline()[:-1]
        self.append(Global(module, name, self.id_mapping))
    dispatch[GLOBAL] = load_global

    def load_reduce(self):
        stack = self.stack

        callable = stack[-2]
        arg_tup  = stack[-1]
        del stack[-2:]

        value=Object(callable, arg_tup, self.id_mapping)
        self.append(value)
    dispatch[REDUCE] = load_reduce

    idprefix=''

    def load_get(self):
        self.append(Get(self.idprefix+self.readline()[:-1], self.id_mapping))
    dispatch[GET] = load_get

    def load_binget(self):
        i = mloads('i' + self.read(1) + '\000\000\000')
        self.append(Get(self.idprefix+`i`, self.id_mapping))
    dispatch[BINGET] = load_binget

    def load_long_binget(self):
        i = mloads('i' + self.read(4))
        self.append(Get(self.idprefix+`i`, self.id_mapping))
    dispatch[LONG_BINGET] = load_long_binget

    def load_put(self):
        self.stack[-1].id=self.idprefix+self.readline()[:-1]
    dispatch[PUT] = load_put

    def load_binput(self):
        i = mloads('i' + self.read(1) + '\000\000\000')
        #LOG('load_binput', 0, 'self.stack = %r, self.idprefix+`i` = %r' % (self.stack, self.idprefix+`i`))
        self.stack[-1].id=self.idprefix+`i`
    dispatch[BINPUT] = load_binput

    def load_long_binput(self):
        i = mloads('i' + self.read(4))
        self.stack[-1].id=self.idprefix+`i`
    dispatch[LONG_BINPUT] = load_long_binput

    class LogCall:
      def __init__(self, func):
        self.func = func

      def __call__(self, context):
        #LOG('LogCall', 0, 'self.stack = %r, func = %s' % (context.stack, self.func.__name__))
        return self.func(context)

    #for code in dispatch.keys():
    #  dispatch[code] = LogCall(dispatch[code])

ppml.ToXMLUnpickler = ToXMLUnpickler

def end_string(self, tag, data):
    v=data[2]
    a=data[1]
    encoding = a.get('encoding','repr') # JPS: repr is default encoding
    if encoding != '': # Bugfix since (is was used on string)
        v=unconvert(encoding,v)
    if a.has_key('id'): self._pickleids[a['id']]=v
    return v

ppml.end_string = end_string

def end_unicode(self, tag, data):
    return unicode(end_string(self, tag, data), 'utf-8')

ppml.end_unicode = end_unicode

class xmlUnpickler(NoBlanks, xyap):
    start_handlers={'pickle': start_pickle}
    end_handlers={
        'int':
        lambda self,tag,data,atoi=string.atoi,name=name:
            atoi(name(self, tag, data)),
        'long':
        lambda self,tag,data,atoi=string.atoi,name=name:
            atoi(name(self, tag, data)),
        'boolean':
        lambda self,tag,data,atoi=string.atoi,name=name:
            atoi(name(self, tag, data)),
        'string': end_string ,
        'unicode': end_unicode ,
        'double':
        lambda self,tag,data,atof=string.atof,name=name:
            atof(name(self, tag, data)),
        'float':
        lambda self,tag,data,atof=string.atof,name=name:
            atof(name(self, tag, data)),
        'none': lambda self, tag, data: None,
        'list': end_list,
        'tuple': end_tuple,
        'dictionary': end_dictionary,
        'key': lambda self, tag, data: data[2],
        'value': lambda self, tag, data: data[2],
        'item': lambda self, tag, data: data[2:],
        'reference': lambda self, tag, data: self._pickleids[data[1]['id']],
        'state': lambda self, tag, data: data[2],
        'klass': lambda self, tag, data: data[2],
        }

ppml.xmlUnpickler = xmlUnpickler

def save_string(self, tag, data):
    binary=self.binary
    v=''
    a=data[1]
    if len(data)>2:
        for x in data[2:]:
            v=v+x
    encoding=a.get('encoding','repr') # JPS: repr is default encoding
    if encoding is not '':
        v=unconvert(encoding,v)
    put='p'
    if binary:
        l=len(v)
        s=mdumps(l)[1:]
        if (l<256):
            v='U'+s[0]+v
        else:
            v='T'+s+v
        put='q'
    else: v="S'"+v+"'\012"
    return save_put(self, v, a)

ppml.save_string = save_string

def save_unicode(self, tag, data):
    binary=self.binary
    v=''
    a=data[1]
    if len(data)>2:
        for x in data[2:]:
            v=v+x
    encoding=a.get('encoding','repr') # JPS: repr is default encoding
    if encoding is not '':
        v=unconvert(encoding,v)
    if binary:
        l=len(v)
        s=mdumps(l)[1:]
        v=BINUNICODE+s+v
    else: v=UNICODE+"'"+v+"'\012"
    return save_put(self, v, a)

ppml.save_unicode = save_unicode

class xmlPickler(NoBlanks, xyap):
    start_handlers={
        'pickle': lambda self, tag, attrs: [tag, attrs],
        }
    end_handlers={
        'pickle': lambda self, tag, data: data[2]+'.',
        'none': lambda self, tag, data: 'N',
        'int': save_int,
        'long': lambda self, tag, data: 'L'+data[2]+'L\012',
        'float': save_float,
        'string': save_string,
        'unicode': save_unicode,
        'reference': save_reference,
        'tuple': save_tuple,
        'list': save_list,
        'dictionary': save_dict,
        'item': lambda self, tag, data, j=string.join: j(data[2:],''),
        'value': lambda self, tag, data: data[2],
        'key' : lambda self, tag, data: data[2],
        'object': save_object,
        'klass': lambda self, tag, data: data[2],
        'state': lambda self, tag, data: data[2],
        'global': save_global,
        'persistent': save_persis,
        }

ppml.xmlPickler = xmlPickler

class Tuple(Sequence): pass

ppml.Tuple = Tuple

######################################################################################
# Expression patch

from Products.CMFCore.Expression import Expression

def Expression_hash(self):
  return hash(self.text)

Expression.__hash__ = Expression_hash

######################################################################################
# dtml-sqlvar patch to convert None to NULL

from Shared.DC.ZRDB.sqlvar import SQLVar
from Shared.DC.ZRDB import sqlvar
from string import atoi,atof

def SQLVar_render(self, md):
    name=self.__name__
    args=self.args
    t=args['type']
    try:
        expr=self.expr
        if type(expr) is type(''): v=md[expr]
        else: v=expr(md)
    except:
        if args.has_key('optional') and args['optional']:
            return 'null'
        if type(expr) is not type(''):
            raise
        raise ValueError, 'Missing input variable, <em>%s</em>' % name

    if t=='int':
        try:
            if type(v) is StringType:
                if v[-1:]=='L':
                    v=v[:-1]
                atoi(v)
            else: v=str(int(v))
        except:
            if not v and args.has_key('optional') and args['optional']:
                return 'null'
            raise ValueError, (
                'Invalid integer value for <em>%s</em>' % name)
    elif t=='float':
        try:
            if type(v) is StringType:
                if v[-1:]=='L':
                    v=v[:-1]
                atof(v)
            else: v=str(float(v))
        except:
            if not v and args.has_key('optional') and args['optional']:
                return 'null'
            raise ValueError, (
                'Invalid floating-point value for <em>%s</em>' % name)
    # Patched by yo
    elif t=='datetime':
        if v is None:
            if args.has_key('optional') and args['optional']:
                return 'null'
            else:
                raise ValueError, (
                    'Invalid datetime value for <em>%s</em>: %r' % (name, v))

        try:
            if hasattr(v, 'ISO'):
                v=v.ISO()
            if hasattr(v, 'strftime'):
                v=v.strftime('%Y-%m-%d %H:%M:%S')
            else: v=str(v)
        except:
            if not v and args.has_key('optional') and args['optional']:
                return 'null'
            raise ValueError, (
                'Invalid datetime value for <em>%s</em>: %r' % (name, v))

        v=md.getitem('sql_quote__',0)(v)
    # End of patch
    else:
        # Patched by yo
        if v is None:
            if args.has_key('optional') and args['optional']:
                return 'null'
            else:
                raise ValueError, (
                    'Invalid string value for <em>%s</em>' % name)
        # End of patch

        if not isinstance(v, (str, unicode)):
            v=str(v)
        if not v and t=='nb':
            if args.has_key('optional') and args['optional']:
                return 'null'
            else:
                raise ValueError, (
                    'Invalid empty string value for <em>%s</em>' % name)

        v=md.getitem('sql_quote__',0)(v)
        #if find(v,"\'") >= 0: v=join(split(v,"\'"),"''")
        #v="'%s'" % v

    return v

# Patched by yo. datetime is added.
valid_type={'int':1, 'float':1, 'string':1, 'nb': 1, 'datetime' : 1}.has_key

SQLVar.render = SQLVar_render
SQLVar.__call__ = SQLVar_render
sqlvar.valid_type = valid_type


######################################################################################
# CMFCatalogAware patch for accepting arbitrary parameters.

from Products.CMFCore.CMFCatalogAware import CMFCatalogAware

def reindexObject(self, idxs=[], *args, **kw):
    """
        Reindex the object in the portal catalog.
        If idxs is present, only those indexes are reindexed.
        The metadata is always updated.

        Also update the modification date of the object,
        unless specific indexes were requested.
    """
    if idxs == []:
        # Update the modification date.
        if hasattr(aq_base(self), 'notifyModified'):
            self.notifyModified()
    catalog = getToolByName(self, 'portal_catalog', None)
    if catalog is not None:
        catalog.reindexObject(self, idxs=idxs, *args, **kw)

CMFCatalogAware.reindexObject = reindexObject


##########################################
# ZPublisher should drop requests without a good http referer

from ZPublisher.BaseRequest import BaseRequest

BaseRequest.erp5_old_traverse = BaseRequest.traverse

import AccessControl

def erp5_new_traverse(request, path, response=None, validated_hook=None):

  if response is None: response=request.response
  object = BaseRequest.erp5_old_traverse(request, path, response=response, validated_hook=validated_hook)
  http_url = request.get('ACTUAL_URL', '').strip()
  http_referer = request.get('HTTP_REFERER', '').strip()

  security_manager = AccessControl.getSecurityManager()
  user = security_manager.getUser()
  user_roles = user.getRolesInContext(object)

  # Manager can do anything
  if 'Manager' in user_roles:
    return object

  # are we within a portal ?
  try:
    context = getattr(object, 'im_self', None)
    if context is not None:
      try:
        portal_object = context.getPortalObject()
      except AttributeError:
        portal_object = object.getPortalObject()
    else :
      portal_object = object.getPortalObject()
  except AttributeError:
    pass
  else:
    if not getattr(portal_object, 'require_referer', 0):
      return object
    portal_url = portal_object.absolute_url()
    if http_referer != '':
      # if HTTP_REFERER is set, user can acces the object if referer is ok
      if http_referer.startswith(portal_url):
        return object
      else:
        LOG('HTTP_REFERER_CHECK : BAD REFERER !', 0, 'request : "%s", referer : "%s"' % (http_url, referer))
        response.unauthorized()
    else:
      # no HTTP_REFERER, we only allow to reach portal_url
      for i in ('/', '/index_html', '/login_form', '/view'):
        if http_url.endswith(i):
          http_url = http_url[:-len(i)]
          break
      if len(http_url) == 0 or not portal_url.startswith(http_url):
        LOG('HTTP_REFERER_CHECK : NO REFERER !', 0, 'request : "%s"' % http_url)
        response.unauthorized()

  return object

BaseRequest.traverse = erp5_new_traverse

