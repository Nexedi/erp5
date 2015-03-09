##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#               2015 Wenjie Zheng <wenjie.zheng@tiolive.com>
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

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Accessor.Base import _evaluateTales
from Products.ERP5Type.Globals import PersistentMapping
from Products.DCWorkflow.Expression import StateChangeInfo
from zLOG import LOG, ERROR, DEBUG, WARNING
from Products.ERP5Type.Utils import convertToUpperCase, convertToMixedCase
from Products.DCWorkflow.DCWorkflow import ObjectDeleted, ObjectMoved
from copy import deepcopy
from Persistence import Persistent

class Transition(XMLObject):
  """
  A ERP5 Transition.
  """

  meta_type = 'ERP5 Transition'
  portal_type = 'Transition'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
             PropertySheet.Base,
             PropertySheet.XMLObject,
             PropertySheet.CategoryCore,
             PropertySheet.DublinCore,
             PropertySheet.Transition,
  )

  def execute(self, document, form_kw=None):
    """
    Execute transition.
    """
    sci = None
    econtext = None
    moved_exc = None
    validation_exc = None

    # Figure out the old and new states.
    if form_kw is None:
      form_kw = {}
    workflow = self.getParentValue()
    # Get variable values
    state_bc_id = workflow.getStateBaseCategory()
    status_dict = workflow.getCurrentStatusDict(document)
    state_object = workflow._getOb(status_dict[state_bc_id])

    old_state = state_object.getId()
    new_state = document.unrestrictedTraverse(self.getDestination()).getId()

    if new_state is None:
        new_state = document.unrestrictedTraverse(workflow.getSource()).getId()
        if not new_state:
            # Do nothing if there is no initial state. We may want to create
            # workflows with no state at all, only for worklists.
            return
        former_status = {}
    else:
        former_status = state_object.getId()
    old_sdef = state_object
    try:
        new_sdef = document.unrestrictedTraverse(self.getDestination())
    except KeyError:
        raise WorkflowException('Destination state undefined: ' + new_state)

    # Execute the "before" script.
    before_script_success = 1
    script_id = self.getBeforeScriptId()
    if script_id:
      script = self.getParent()._getOb(script_id)
      # Pass lots of info to the script in a single parameter.
      kwargs = form_kw
      sci = StateChangeInfo(
            document, workflow, former_status, self, old_sdef, new_sdef, kwargs)
      try:
        #LOG('_executeTransition', 0, "script = %s, sci = %s" % (repr(script), repr(sci)))
        script.execute(sci)  # May throw an exception.
      except ValidationFailed, validation_exc:
        before_script_success = 0
        before_script_error_message = deepcopy(validation_exc.msg)
        validation_exc_traceback = sys.exc_traceback
      except ObjectMoved, moved_exc:
        ob = moved_exc.getNewObject()
        # Re-raise after transition

    # Do not proceed in case of failure of before script
    if not before_script_success:
      former_status = old_state # Remain in state
      self.setStatusOf(workflow.getId(), document, status_dict)
      sci = StateChangeInfo(
        document, workflow, former_status, self, old_sdef, new_sdef, kwargs)
        # put the error message in the workflow history
      sci.setWorkflowVariable(error_message=before_script_error_message)
      if validation_exc :
        # reraise validation failed exception
        raise validation_exc, None, validation_exc_traceback
      return new_sdef

    # update state
    self._changeState(document)
    ### zwj: update Role mapping, also in Workflow, initialiseDocument()
    self.getParent().updateRoleMappingsFor(document)

    status_dict['undo'] = 0
    status_dict['action'] = self.getId()

    # Modify workflow history
    #status_dict[state_bc_id] = document.getCategoryMembershipList(state_bc_id)[0]
    status_dict[state_bc_id] = new_state
    object = workflow.getStateChangeInformation(document, state_object, transition=self)

    # Update all variables
    for variable in workflow.contentValues(portal_type='Variable'):
      if variable.getAutomaticUpdate():
        # if we have it in form get it from there
        # otherwise use default
        variable_title = variable.getTitle()
        if variable_title in form_kw:
           status_dict[variable_title] = form_kw[variable_title]
        else:
          status_dict[variable_title] = variable.getInitialValue(object=object)

    # Update all transition variables
    if form_kw is not None:
      object.REQUEST.other.update(form_kw)
    # zwj: The transition variable is replaced by a base category; thus this part is not in use.
    for variable in self.contentValues(portal_type='Transition Variable'):
      status_dict[variable.getCausalityTitle()] = variable.getInitialValue(object=object)

    #workflow._updateWorkflowHistory(document, status_dict)
    self.setStatusOf(workflow.getId(), document, status_dict)
    # Execute the "after" script.
    script_id = self.getAfterScriptId()
    if script_id is not None:
      kwargs = form_kw
      # Script can be either script or workflow method
      if script_id in old_sdef.getDestinationTitleList():
        getattr(workflow, convertToMixedCase(script_id)).execute(document)
      else:
        script = self.getParent()._getOb(script_id)
        # Pass lots of info to the script in a single parameter.
        sci = StateChangeInfo(
            document, workflow, former_status, self, old_sdef, new_sdef, kwargs)
        script.execute(sci)  # May throw an exception.

    # Return the new state object.
    if moved_exc is not None:
        # Propagate the notification that the object has moved.
        raise moved_exc
    else:
        return new_sdef

  def _changeState(self, document):
    """
    Change the state of the object.
    """
    state = self.getDestination()
    if state is not None:
      # Some transitions don't update the state
      state_bc_id = self.getParentValue().getStateBaseCategory()
      document.setCategoryMembership(state_bc_id, state)

  def _checkPermission(self, document):
    """
    Check if transition is allowed.
    """
    expr_value = self.getGuardExpression(evaluate=0)
    if expr_value is not None:
      # do not use 'getGuardExpression' to calculate tales because
      # it caches value which is bad. Instead do it manually
      value = _evaluateTales(document, expr_value)
    else:
      value = True
    #print "CALC", expr_value, '-->', value
    return value

  def setStatusOf(self, wf_id, ob, status):
    """ Append an entry to the workflow history.

    o Invoked by transition execution.
    """
    wfh = None
    has_history = 0
    if getattr(aq_base(ob), 'workflow_history', None) is not None:
        history = ob.workflow_history
        if history is not None:
            has_history = 1
            wfh = history.get(wf_id, None)
            if wfh is not None and not isinstance(wfh, WorkflowHistoryList):
                wfh = WorkflowHistoryList(list(wfh))
                ob.workflow_history[wf_id] = wfh
    if wfh is None:
        wfh = WorkflowHistoryList()
        if not has_history:
            ob.workflow_history = PersistentMapping()
        ob.workflow_history[wf_id] = wfh
    wfh.append(status)

class WorkflowHistoryList(Persistent):
  _bucket_size = 16

  def __init__(self, iterable=None, prev=None):
    self._prev = prev
    self._slots = []
    if iterable is not None:
      for x in iterable:
        self.append(x)

  def __add__(self, iterable):
    return self.__class__(tuple(self) + tuple(iterable))

  def __contains__(self, item):
    return item in tuple(self)

  def __eq__(self, other):
    return tuple(self) == tuple(other)

  def __getitem__(self, index):
    if index == -1:
      return self._slots[-1]
    elif isinstance(index, (int, long)):
      if index < 0:
        # XXX this implementation is not so good, but rarely used.
        index += len(self)
      iterator = self.__iter__()
      for i in xrange(index):
        iterator.next()
      return iterator.next()
    elif isinstance(index, slice):
      return self.__class__((self[x] for x in
                                   xrange(*index.indices(len(self)))))
    else:
      raise TypeError, 'tuple indices must be integers'

  def __getslice__(self, start, end):
    return self.__getitem__(slice(start, end))

  def __getstate__(self):
    return (self._prev, self._slots)

  def __iter__(self):
    bucket = self
    stack = []
    while bucket is not None:
      stack.append(bucket)
      bucket = bucket._prev
    for i in reversed(stack):
      for j in i._slots:
        yield j

  def __len__(self):
    length = len(self._slots)
    bucket = self._prev
    while bucket is not None:
      length += len(bucket._slots)
      bucket = bucket._prev
    return length

  def __mul__(self, x):
    return self.__class__(tuple(self) * x)

  def __nonzero__(self):
    return len(self._slots) != 0 or self._prev is not None

  def __repr__(self):
    #return '%s' % repr(tuple(self.__iter__()))
    return '<%s object at 0x%x %r>' % (self.__class__.__name__, id(self), tuple(self))

  def __rmul__(self, x):
    return self.__class__(x * tuple(self))

  def __setstate__(self, state):
    self._prev, self._slots = state

  def append(self, value):
    if len(self._slots) < self._bucket_size:
      self._slots.append(value)
      self._p_changed = 1
    else:
      self._prev = self.__class__(self._slots, prev=self._prev)
      self._slots = [value]