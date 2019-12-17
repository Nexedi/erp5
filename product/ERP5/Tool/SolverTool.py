# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

import zope.interface
import re

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions, interfaces
from Products.ERP5Type.Tool.TypesTool import TypeProvider
from Products.ERP5Type.Message import translateString

class SolverTool(TypeProvider):
  """ The SolverTool provides API to find out which solver can be applied in
  which case and contains SolverProcess instances which are used to keep track
  of solver decisions, solver history and global optimisation.
  It also contains solvers.
  """
  id = 'portal_solvers'
  meta_type = 'ERP5 Solver Tool'
  portal_type = 'Solver Tool'
  allowed_types = ( 'ERP5 Solver Type', )

  # Declarative Security
  security = ClassSecurityInfo()

  # Declarative interfaces
  zope.interface.implements(interfaces.IDeliverySolverFactory,)

  # IDeliverySolverFactory implementation
  security.declareProtected(Permissions.AccessContentsInformation,
                            'newDeliverySolver')
  def newDeliverySolver(self, portal_type, movement_list):
    """
    Return a new instance of delivery solver of the given
    portal_type and with appropriate parameters.

    portal_type -- the portal type of the delivery solver.

    movement_list -- movements to initialise the instance with
    """
    solver_type = self._getOb(portal_type)
    solver_class = re.sub('^add', 'newTemp',
                       solver_type.getTypeFactoryMethodId())
    module = __import__('Products.ERP5Type.Document', globals(), locals(),
                        [solver_class])
    tmp_solver = getattr(module, solver_class)(self, 'delivery_solver')
    tmp_solver.setDeliveryValueList(movement_list)
    return tmp_solver

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDeliverySolverTranslatedItemList')
  def getDeliverySolverTranslatedItemList(self, portal_type_list=None):
    """
    """
    return sorted([(translateString(x), 'portal_solvers/%s' % x) \
                   for x in self.getPortalDeliverySolverTypeList() \
                   if portal_type_list is None or x in portal_type_list],
                  key=lambda x:str(x[0]))

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSolverProcessValueList')
  def getSolverProcessValueList(self, delivery_or_movement=None, validation_state=None):
    """
    Returns the list of solver processes which are
    are in a given state and which apply to delivery_or_movement.
    This method is useful to find applicable solver processes
    for a delivery.

    delivery_or_movement -- a movement, a delivery,
                            or a list thereof

    validation_state -- a state of a list of states
                        to filter the result
    """

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSolverDecisionValueList')
  def getSolverDecisionValueList(self, delivery_or_movement=None, validation_state=None):
    """
    Returns the list of solver decisions which apply
    to a given movement.

    delivery_or_movement -- a movement, a simulation movement, a delivery,
                            or a list thereof

    validation_state -- a state of a list of states
                        to filter the result
    """

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSolverDecisionApplicationValueList')
  def getSolverDecisionApplicationValueList(self, movement, divergence_tester=None):
    """
    Returns the list of documents at which a given divergence resolution
    can be resolved at. For example, in most cases, date divergences can
    only be resolved at delivery level whereas quantities are usually
    resolved at cell level.

    The result of this method is a list of ERP5 documents.

    NOTE: renaming probably required. I do not like this name nor the one
    of the interface definition.
    """
    # Short Term Implementation Approach
    # XXX tested_property can be multiple for some testers like Net
    # Converted Quantity Divergence Tester or Variation Divergence
    # Tester.
    test_property = divergence_tester.getTestedProperty()
    application_value = movement
    try:
      while not application_value.hasProperty(test_property):
        application_value = application_value.getParentValue()
    except AttributeError:
      # if missing, it should be in Delivery level ?
      application_value = movement.getRootDeliveryValue()
    return [application_value]

    # Alternate short Term Implementation Approach
    return self.SolverTool_getSolverDecisionApplicationValueList(movement, divergence_tester)

    # Alternate short Term Implementation Approach
    return divergence_tester.getTypeBasedMethod('getSolverDecisionApplicationValueList')(
                                                movement, divergence_tester)

    # Mid-term implementation (we suppose movement is a delivery)
    # use delivery builders to find out at which level the given
    # property can be modified
    test_property = divergence_tester.getTestedProperty()
    application_value_level = {}
    for simulation_movement in movement.getDeliveryRelatedValueList():
      business_link = simulation_movement.getCausalityValue()
      for delivery_builder in business_link.getDeliveryBuilderValueList():
        for movement_group in delivery_builder.contentValues(): # filter missing
          if test_property in movement_group.getTestedPropertyList():
            application_value_level[movement_group.getCollectGroupOrder()] = None
    result = []
    # Delivery level
    if 'delivery' in application_value_level:
      result.append(movement.getDeliveryValue())
    # Line level
    if 'line' in application_value_level and not movement.isLine():
      result.append(movement)
    elif 'line' in application_value_level and not movement.isLine():
      result.append(movement.getParentValue())
    # Cell level
    if 'cell' in application_value_level and movement.isCell():
      result.append(movement)
    # Group of lines level (we try to find the most appropriate enclosing group)
    if 'group' in application_value_level:
      application_value = movement
      while not application_value.hasProperty(test_property):
        application_value = application_value.getParentValue()
      if application_value not in result: result.append(application_value)
    # Group of lines level (we try to find the most appropriate enclosing group)
    if 'all_group' in application_value_level:
      application_value = movement
      while not application_value.hasProperty(test_property):
        application_value = application_value.getParentValue()
        if application_value not in result: result.append(application_value)
    return result

    # Longer-term implementation (we suppose movement is a delivery)
    # use delivery builders to find out at which level the given
    # property can be modified
    test_property = divergence_tester.getTestedProperty()
    application_value_level = {}
    for simulation_movement in movement.getDeliveryRelatedValueList():
      business_link = simulation_movement.getCausalityValue()
      for delivery_builder in business_link.getDeliveryBuilderValueList():
        for property_group in delivery_builder.contentValues(portal_type="Property group"):
          if test_property in property_group.getTestedPropertyList():
            application_value_level[property_group.getCollectGroupOrder()] = None
    # etc. same

  security.declareProtected(Permissions.AccessContentsInformation,
                            'searchTargetSolverList')
  def searchTargetSolverList(self, divergence_tester,
                             simulation_movement,
                             automatic_solver_only=False, **kw):
    """
    this method returns a list of target solvers, as predicates against
    simulation movement.
    """
    solver_list = divergence_tester.getSolverValueList()
    if automatic_solver_only:
      return [x for x in solver_list if x.isAutomaticSolver() and \
              x.test(simulation_movement, **kw)]
    else:
      return [x for x in solver_list if x.test(simulation_movement, **kw)]

InitializeClass(SolverTool)
