# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Products.ERP5Type.Interactor.Interactor import Interactor

class PortalTypeClassInteractor(Interactor):
  """
    This interactor handles all the calls to resetDynamicDocuments
    which must be trigered whenever some parts of ERP5
    are modified and require to generate again accessors
    and dynamic properties.
  """
  def install(self):
    from Products.ERP5Type import WITH_LEGACY_WORKFLOW
    if WITH_LEGACY_WORKFLOW:
      from Products.DCWorkflow.Transitions import Transitions
      self.on(Transitions, 'addTransition').doAfter(self.resetDynamic)
      self.on(Transitions, 'deleteTransitions').doAfter(self.resetDynamic)
      from Products.DCWorkflow.Transitions import TransitionDefinition
      self.on(TransitionDefinition, 'setProperties').doAfter(self.resetDynamic)
      from Products.DCWorkflow.Variables import Variables
      self.on(Variables, 'setStateVar').doAfter(self.resetDynamic)

    from Products.Localizer.Localizer import Localizer
    self.on(Localizer, 'add_language').doAfter(self.resetDynamic)
    self.on(Localizer, 'del_language').doAfter(self.resetDynamic)

  def resetDynamic(self, method_call_object, *args, **kw):
    """
    Call resetDynamicDocuments at the end of the transaction
    """
    from Products.ERP5.ERP5Site import getSite
    # method_call_object might be an unwrapped DCWorflowDefinition method,
    # no even belonging to a container.
    portal = getSite()
    types_tool = getattr(portal, 'portal_types', None)
    if types_tool is None:
      return
    types_tool.resetDynamicDocumentsOnceAtTransactionBoundary()
