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
from Products.ERP5Workflow.Document.Workflow import Workflow
from Products.ERP5Type.Globals import PersistentMapping

from tempfile import mktemp
import os
from Products.DCWorkflowGraph.config import DOT_EXE
from Products.DCWorkflowGraph.DCWorkflowGraph import bin_search, getGraph

from Acquisition import aq_base

from DateTime import DateTime

class ConfigurationWorkflow(Workflow):
  """
  A Business Configuration Workflow.
  """

  meta_type = 'ERP5 Workflow'
  portal_type = 'Configuration Workflow'
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
    PropertySheet.Workflow,
    PropertySheet.ConfigurationWorkflow,
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
    variable_list = self.contentValues(portal_type='Workflow Variable')
    for variable in variable_list:
      status_dict[variable.getTitle()] = variable.getVariableValue(object=object)
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

  def _getWorkflowStateOf(self, ob, id_only=0):
      tool = self.getPortalObject().portal_workflow
      id = self.getId()
      status = tool.getStatusOf(id, ob)
      if status is None:
          state = self.getSourceValue()
      else:
          state_id = status.get(self.getStateVariable(), None)
          state = self._getOb(state_id)
          if state is None:
              state = self.getSourceValue()
      if id_only:
          return state.getId()
      else:
          return state
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
      for state in self.contentValues(portal_type='Configuration State'):
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
      for transition in self.contentValues(portal_type='Configuration Transition'):
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
