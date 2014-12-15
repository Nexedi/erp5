##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.Accessor import WorkflowState
from Products.ERP5Type import Permissions
from tempfile import mktemp
import os
from Products.DCWorkflowGraph.config import DOT_EXE
from Products.DCWorkflowGraph.DCWorkflowGraph import bin_search, getGraph
from Products.ERP5Type.Utils import UpperCase
from Acquisition import aq_base

from DateTime import DateTime

class Workflow(XMLObject):
  """
  A ERP5 Workflow.
  """

  meta_type = 'ERP5 Workflow'
  portal_type = 'Workflow'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  ### register the variable given by "base category value"
  #state_var = 'state'
  ### In DCworkflow; state/transition can be registered inside workflow 

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.Workflow,
  )

  def initializeDocument(self, document):
    """
    Set initial state on the Document
    """
    state_bc_id = self.getStateBaseCategory()
    document.setCategoryMembership(state_bc_id, self.getSource())

    object = self.getStateChangeInformation(document, self.getSourceValue())

    # Initialize workflow history
    status_dict = {state_bc_id: self.getSource()}
    variable_list = self.contentValues(portal_type='Variable')
    for variable in variable_list:
      status_dict[variable.getTitle()] = variable.getInitialValue(object=object)
    self._updateWorkflowHistory(document, status_dict)

  def _generateHistoryKey(self):
    """
    Generate a key used in the workflow history.
    """
    return self.getRelativeUrl()

  def _updateWorkflowHistory(self, document, status_dict):
    """
    Change the state of the object.
    """
    # Create history attributes if needed
    if getattr(aq_base(document), 'workflow_history', None) is None:
      document.workflow_history = PersistentMapping()
      # XXX this _p_changed is apparently not necessary
      document._p_changed = 1

    # Add an entry for the workflow in the history
    workflow_key = self._generateHistoryKey()
    if not document.workflow_history.has_key(workflow_key):
      document.workflow_history[workflow_key] = ()

    # Update history
    document.workflow_history[workflow_key] += (status_dict, )
    # XXX this _p_changed marks the document modified, but the
    # only the PersistentMapping is modified
    document._p_changed = 1
    # XXX this _p_changed is apparently not necessary
    document.workflow_history._p_changed = 1

  def getCurrentStatusDict(self, document):
    """
    Get the current status dict.
    """
    workflow_key = self._generateHistoryKey()

    # Copy is requested
    result = document.workflow_history[workflow_key][-1].copy()
    return result

  def getDateTime(self):
    """
    Return current date time.
    """
    return DateTime()

  def getStateChangeInformation(self, document, state, transition=None):
    """
    Return an object used for variable tales expression.
    """
    if transition is None:
      transition_url = None
    else:
      transition_url = transition.getRelativeUrl()
    return self.asContext(document=document,
                          transition=transition,
                          transition_url=transition_url,
                          state=state)
# ========== Workflow5 Project, Wenjie, Dec 2014 ===============================
  def isWorkflow5MethodSupported(self, document, transition, wf_id):
    state = self._getWorkflow5StateOf(document, wf_id)
    #state = document.getCategoryStateValue()
    if state is None:
      return 0
    if transition in state.getDestinationValueList():
      return 1
    return 0

### get workflow state from base category value:
  def _getWorkflow5StateOf(self, ob, wf_id):
    ### the problem is that: How to pass state_id from base_category
    getter = WorkflowState.Getter
    #ptype_klass = self.getPortalObject().portal_types.getPortalTypeClass(ob.getTypeInfo().getId())
    ptype_klass = ob.getTypeInfo().__class__
    #raise NotImplementedError (ptype_klass)#class 'erp5.portal_type.Base Type'
    StateGetter = getter('get%s'%UpperCase(self.getStateBaseCategory()), wf_id)
    ptype_klass.registerAccessor(StateGetter)
    # raise NotImplementedError (StateGetter._id)# getCategoryState
    state_path = ob.getCategoryState()
    ###
    if state_path is not None:
      state = self.restrictedTraverse(state_path)
      #state = self._getOb(state_id)
    else: state = None
    return state

# =========== WF5 ==============================================================
  ###########
  ## Graph ##
  ############

  getGraph = getGraph

  def getPOT(self, *args, **kwargs):
      """
      get the pot, copy from:
      "dcworkfow2dot.py":http://awkly.org/Members/sidnei/weblog_storage/blog_27014
      and Sidnei da Silva owns the copyright of the this function
      """
      out = []
      transition_dict = {}
      out.append('digraph "%s" {' % self.getTitle())
      transition_with_init_state_list = []
      for state in self.contentValues(portal_type='State'):
        out.append('%s [shape=box,label="%s",' \
                     'style="filled",fillcolor="#ffcc99"];' % \
                     (state.getId(), state.getTitle()))
        # XXX Use API instead of getDestinationValueList
        for available_transition in state.getDestinationValueList():
          transition_with_init_state_list.append(available_transition.getId())
          destination_state = available_transition.getDestinationValue()
          if destination_state is None:
            # take care of 'remain in state' transitions
            destination_state = state
          #
          key = (state.getId(), destination_state.getId())
          value = transition_dict.get(key, [])
          value.append(available_transition.getTitle())
          transition_dict[key] = value

      # iterate also on transitions, and add transitions with no initial state
      for transition in self.contentValues(portal_type='Transition'):
        trans_id = transition.getId()
        if trans_id not in transition_with_init_state_list:
          destination_state = transition.getDestinationValue()
          if destination_state is None:
            dest_state_id = None
          else:
            dest_state_id = destination_state.getId()

          key = (None, dest_state_id)
          value = transition_dict.get(key, [])
          value.append(transition.getTitle())
          transition_dict[key] = value

      for k, v in transition_dict.items():
          out.append('%s -> %s [label="%s"];' % (k[0], k[1],
                                                 ',\\n'.join(v)))

      out.append('}')
      return '\n'.join(out)
