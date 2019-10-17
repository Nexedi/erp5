# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.ERP5Type.Core.Predicate import Predicate

class SolverTypeInformation(Predicate, ERP5TypeInformation):
  """
    A Type Information class which (will) implement
    all Solver related methods
  """
  # CMF Type Definition
  meta_type = 'ERP5 Solver Type Information'
  portal_type = 'Solver Type'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.BaseType
                    , PropertySheet.SolverType
                    , PropertySheet.Configurable
                    )

  def getSolverConflictMessageList(self, movement, configuration_mapping, solver_dict, movement_dict):
    """
    Returns the list of conflictings messgaes if the solver and configuration_mapping
    conflicts with another solver

    movement -- a movement

    configuration_mapping -- a mapping of configuration parameters sorted in
                             canonical way. ((c1, v1), (c2, v2 ))

    solver_dict -- a dictionary of configuration parameters for
                   each solver
                      solver_dict[solver] = {
                         movement : [((c1, v1), (c2, v2 )),
                                     ((c1, v1), (c2, v2 )),
                                    ],}

    movement_dict -- a dictionary of solver and configuration parameters for
                     each movement
                       movement_dict[movement] = {
                                     solver : [((c1, v1), (c2, v2 )),
                                               ((c1, v1), (c2, v2 )),
                                              ],}
    """
    method = self._getTypeBasedMethod('getSolverConflictMessageList')
    if method is not None:
      return method(movement, configuration_mapping, solver_dict, movement_dict)

    # Default Implementation (use categories and trivial case)
    #  this default implementation should be applicable to most
    #  solvers so that use of Type Based methods is very rare
    message_list = []
    for solver, configuration_list in movement_dict[movement].items():
      if solver is not self and configuration_mapping in configuration_list:
        # TODO: Use Message() class and avoid duplicate (this method will be
        # called for the other solver and add the same message again...)
        message_list.append(
          "%s: Solver conflict on %r between '%s' and '%s'" % \
          (movement.getRelativeUrl(), configuration_mapping, self, solver))

    return message_list

  def getSolverProcessGroupingKey(self, movement, configuration_mapping, solver_dict, movement_dict):
    """
    Returns a key which can be used to group solvers during the
    process to build Targer Solver instances from Solver Decisions.
    This key depends on the movement and on the configuration_dict.

    For example, the movement dependent key for a solver which reduces
    produced quantity is the releative URL of the production order which
    this movement depends from (if it depennds on a single production
    order). If the same movement relates to multiple production orders,
    then the movement dependent grouping key should be None, but this
    could generate a different group for movements which depend on
    a single production order and for movements which depend on
    multiple production orders. For this purpose, the grouping key
    can be decided by looking up other_movement_list, a dictionnary
    which provides for each movement solver by the same solver the
    configuration parameters.

    The configuration dependent key for a "universal" solver (ex.
    Adopt, Accept) which tested property is configurable, is the
    tested property itself.

    movement -- a movement

    configuration_mapping -- a mapping of configuration parameters sorted in
                             canonical way. ((c1, v1), (c2, v2 ))

    solver_dict -- a dictionary of configuration parameters for
                   each solver
                      solver_dict[solver] = {
                         movement : [((c1, v1), (c2, v2 )),
                                     ((c1, v1), (c2, v2 )),
                                    ],}

    movement_dict -- a dictionary of solver and configuration parameters for
                     each movement
                       movement_dict[movement] = {
                                     solver : [((c1, v1), (c2, v2 )),
                                               ((c1, v1), (c2, v2 )),
                                              ],}
    """
    method = self._getTypeBasedMethod('getSolverProcessGroupingKey')
    if method is not None:
      return method(movement, configuration_mapping, solver_dict, movement_dict)

    # Default Implementation (read solver type properties and implement XXX-TODO)
    if self.isLineGroupable():
      return ()

    return movement.getRelativeUrl()

  def getDefaultConfigurationPropertyDict(self, configurable):
    """
    Returns a dictionary of default properties for specified
    configurable object
    (implementation)

    configurable -- a configurable document (Solver Decision
                    or Target Solver)
    """
    method_id = self.getDefaultConfigurationPropertyDictMethodId()
    if method_id:
      return self._callMethod(configurable, method_id, {})
    else:
      return {}

  def getDefaultConfigurationProperty(self, property, configurable):
    """
    Returns the default value for a given property
    (public API)

    configurable -- a configurable document (Solver Decision
                    or Target Solver)

    TODO: XXX-JPS unify with IConfigurable
    """
    return self.getDefaultConfigurationPropertyDict().get(property, None)

  def getConfigurationPropertyListDict(self, configurable):
    """
    Returns a dictionary of possible values for specified
    configurable object
    (implementation)

    configurable -- a configurable document (Solver Decision
                    or Target Solver)
    """
    method_id = self.getConfigurationPropertyListDictMethodId()
    if method_id:
      return self._callMethod(configurable, method_id, {})
    else:
      return {}

  def getConfigurationPropertyList(self, property, configurable):
    """
    Returns a list of possible values for a given property
    (public API)

    configurable -- a configurable document (Solver Decision
                    or Target Solver)
    """
    return self.getConfigurationPropertyListDict().get(property, [])

  def _callMethod(self, configurable, method_id, default=None):
    # Implemented through type based method
    # and using read transaction cache
    portal_type = configurable.getPortalType()
    if portal_type == 'Solver Decision':
      try:
        solver_portal_type = configurable.getSolverValue().getId()
        solver = configurable.getParentValue().newContent(
          portal_type=solver_portal_type,
          temp_object=True,
          delivery_list=configurable.getDeliveryList(),
          causality_value=configurable)
      except AttributeError:
        return default
    elif interfaces.ISolver.providedBy(configurable):
      solver_portal_type = portal_type
      solver = configurable
    else:
      raise NotImplementedError, '%s is not supported for configurable argument' % portal_type

    method = getattr(solver, method_id)
    return method()

  def solve(self, delivery_list=None, configuration_dict=None,
            activate_kw=None, **kw):
    if delivery_list is None:
      return
    if configuration_dict is None:
      configuration_dict = {}
    solver_process_tool = self.getPortalObject().portal_solver_processes
    solver_process = solver_process_tool.newContent(
      portal_type='Solver Process',
      temp_object=True)
    solver = solver_process.newContent(portal_type=self.getId(),
                                       delivery_list=delivery_list)
    solver.updateConfiguration(**configuration_dict)
    if self.getPortalObject().portal_workflow.isTransitionPossible(
      solver, 'start_solving'):
      solver.startSolving()
    solver.solve(activate_kw=activate_kw)
