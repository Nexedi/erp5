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


from zLOG import LOG
from string import join

##############################################################################
# Folder naming: member folder should be names as a singular in small caps
from Products.CMFDefault.MembershipTool import MembershipTool
MembershipTool.membersfolder_id = 'member'

##############################################################################
# Import: add rename feature
from OFS.ObjectManager import ObjectManager, customImporters
class PatchedObjectManager(ObjectManager):
    def _importObjectFromFile(self, filepath, verify=1, set_owner=1, id=None):
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
PropertyManager.hasProperty = ERP5PropertyManager.hasProperty


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

    # This function doesn't take care about properties by default
    def PUT(self, REQUEST, RESPONSE):
        """Handle put requests"""
        if RESPONSE is not None: self.dav__init(REQUEST, RESPONSE)
        if RESPONSE is not None: self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
        body = REQUEST.get('BODY', '')
        m = re.match('\s*<dtml-comment>(.*)</dtml-comment>\s*\n', body, re.I | re.S)
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
        def _listGlobalActions(user=None, id=None):
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
          return map((lambda (id, val): val), res)

        # Return Cache
        _listGlobalActions = CachingMethod(_listGlobalActions, id='listGlobalActions', cache_duration = 300)
        user = str(_getAuthenticatedUser(self))
        return _listGlobalActions(user=user, id=self.id)


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

##############################################################################
# Stribger repair of BTreeFolder2

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition, StateChangeInfo, ObjectMoved, createExprContext, aq_parent, aq_inner
from Products.DCWorkflow import DCWorkflow
from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD

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
                LOG('_executeTransition', 0, "script = %s, sci = %s" % (repr(script), repr(sci)))
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
            sci.setWorkflowVariable(ob, error_message = before_script_error_message)
            return new_sdef

        # Update state.
        status[self.state_var] = new_state
        tool = aq_parent(aq_inner(self))
        tool.setStatusOf(self.id, ob, status)

        # Make sure that the error message is empty.
        sci = StateChangeInfo(
            ob, self, status, tdef, old_sdef, new_sdef, kwargs)
        sci.setWorkflowVariable(ob, error_message = '')

        # Update role to permission assignments.
        self.updateRoleMappingsFor(ob)

        # Execute the "after" script.
        if tdef is not None and tdef.after_script_name:
            # Script can be either script or workflow method
            if tdef.after_script_name in filter(lambda k: self.transitions[k].trigger_type == TRIGGER_WORKFLOW_METHOD,
                                                                                     new_sdef.transitions):
              script = getattr(ob, tdef.after_script_name)
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
