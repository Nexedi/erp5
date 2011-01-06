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
from zLOG import LOG, ERROR, DEBUG, WARNING
from Products.PageTemplates.Expressions import getEngine
from Products.ERP5Type.Accessor.Base import _evaluateTales

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
    # Call the before script
    self._executeBeforeScript(document)

    # Modify the state
    self._changeState(document)

    # Get variable values
    status_dict = self.getParentValue().getCurrentStatusDict(document)
    status_dict['undo'] = 0

    # Modify workflow history
    state_bc_id = self.getParentValue().getStateBaseCategory()
    status_dict[state_bc_id] = document.getCategoryMembershipList(state_bc_id)[0]

    state_object = document.unrestrictedTraverse(status_dict[state_bc_id])
    object = self.getParentValue().getStateChangeInformation(document, state_object, transition=self)

    # Update all variables
    variable_list = self.getParentValue().contentValues(portal_type='Variable')
    for variable in variable_list:
      if variable.getAutomaticUpdate():
        # if we have it in form get it from there 
        # otherwise use default
        variable_title = variable.getTitle()
        if form_kw.has_key(variable_title):
           status_dict[variable_title] = form_kw[variable_title] 
        else:
          status_dict[variable_title] = variable.getInitialValue(object=object)

    # Update all transition variables
    if form_kw is not None:
      object.REQUEST.other.update(form_kw)
    variable_list = self.contentValues(portal_type='Transition Variable')
    for variable in variable_list:
      status_dict[variable.getCausalityTitle()] = variable.getInitialValue(object=object)
        
    self.getParentValue()._updateWorkflowHistory(document, status_dict)

    # Call the after script
    self._executeAfterScript(document, form_kw=form_kw)


  def _changeState(self, document):
    """
    Change the state of the object.
    """
    state = self.getDestination()
    if state is not None:
      # Some transitions don't update the state
      state_bc_id = self.getParentValue().getStateBaseCategory()
      document.setCategoryMembership(state_bc_id, state)

  def _executeAfterScript(self, document, form_kw=None):
    """
    Execute post transition script.
    """
    if form_kw is None:
      form_kw = {}
    script_id = self.getAfterScriptId()
    if script_id is not None:
      script = getattr(document, script_id)
      script(**form_kw)

  def _executeBeforeScript(self, document, form_kw=None):
    """
    Execute pre transition script.
    """
    if form_kw is None:
      form_kw = {}
    script_id = self.getBeforeScriptId()
    if script_id is not None:
      import pdb;pdb.set_trace()
      script = getattr(document, script_id)
      script(**form_kw)

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
