# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Yusuke Muraoka <yusuke@nexedi.com>
#                    Łukasz Nowak <luke@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
from Products.ERP5.Document.Path import Path
from Products.ERP5Type.Core.Predicate import Predicate
from Products.ERP5.ExplanationCache import _getExplanationCache

import zope.interface

class BusinessLink(Path, Predicate):
  """
    The BusinessLink class embeds all information related to
    lead times and parties involved at a given phase of a business
    process. BusinessLink are also the most common way to trigger
    the build deliveries from buildable movements.

    The idea is to invoke isBuildable() on the collected simulation
    movements (which are orphan) during build "after select" process

    Here is the typical code of an alarm in charge of the building process::

      builder = portal_deliveries.a_delivery_builder
      for business_link in builder.getDeliveryBuilderRelatedValueList():
        builder.build(causality_uid=business_link.getUid(),) # Select movements

    WRONG - too slow

      Pros: global select is possible by not providing a causality_uid
      Cons: global select retrieves long lists of orphan movements which
            are not yet buildable the build process could be rather
            slow or require activities

    TODO:
    - IArrowBase implementation has too many comments which need to be
      fixed
    - _getExplanationRelatedMovementValueList may be superfluous. Make
      sure it is really needed
  """
  meta_type = 'ERP5 Business Link'
  portal_type = 'Business Link'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Folder
                    , PropertySheet.Reference
                    , PropertySheet.Comment
                    , PropertySheet.Arrow
                    , PropertySheet.Amount
                    , PropertySheet.Chain # XXX-JPS Why N
                    , PropertySheet.SortIndex
                    , PropertySheet.BusinessLink
                    , PropertySheet.FlowCapacity
                    , PropertySheet.Reference
                    , PropertySheet.PaymentCondition # XXX-JPS must be renames some day
                    )

  # Declarative interfaces
  zope.interface.implements(interfaces.IBusinessLink,
                            interfaces.IPredicate,
                            )

  # Helper Methods
  def _getExplanationRelatedSimulationMovementValueList(self, explanation):
    explanation_cache = _getExplanationCache(explanation)
    return explanation_cache.getBusinessLinkRelatedSimulationMovementValueList(self)

  def _getExplanationRelatedMovementValueList(self, explanation):
    explanation_cache = _getExplanationCache(explanation)
    return explanation_cache.getBusinessLinkRelatedMovementValueList(self)

  # IBusinessLink implementation
  security.declareProtected(Permissions.AccessContentsInformation,
                                            'getMovementCompletionDate')
  def getMovementCompletionDate(self, movement):
    """Returns the date of completion of the movemnet
    based on paremeters of the business path. This complete date can be
    the start date, the stop date, the date of a given workflow transition
    on the explaining delivery, etc.

    movement -- a Simulation Movement
    """
    method_id = self.getCompletionDateMethodId()
    method = getattr(movement, method_id) # We wish to raise if it does not exist
    return method()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCompletionDate')
  def getCompletionDate(self, explanation):
    """Returns the date of completion of business path in the
    context of the explanation. The completion date of the Business
    Path is the max date of all simulation movements which are
    related to the Business Link and which are part of the explanation.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union
                   business process.
    """
    date_list = []

    # First, let us try to find simulation movements in simulation
    # (hoping that it is already built)
    for movement in self._getExplanationRelatedSimulationMovementValueList(explanation):
      date_list.append(self.getMovementCompletionDate(movement))

    # Next, try to find delivery lines or cells which may provide
    # a good definition of completion date.
    if not date_list:
      for movement in self._getExplanationRelatedMovementValueList(explanation):
        date_list.append(self.getMovementCompletionDate(movement))

    return max(date_list)

  security.declareProtected(Permissions.AccessContentsInformation,
      'isCompleted')
  def isCompleted(self, explanation):
    """returns True if all related simulation movements for this explanation
    document are in a simulation state which is considered as completed
    according to the configuration of the current business path.
    Completed means that it is possible to move to next step
    of Business Process. This method does not check however whether previous
    trade states of a given business process are completed or not.
    Use instead IBusinessLinkProcess.isBusinessLinkCompleted for this purpose.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union
                   business process.

    NOTE: simulation movements can be completed (ex. in 'started' state) but
    not yet frozen (ex. in 'delivered' state).
    """
    acceptable_state_list = self.getCompletedStateList()
    for movement in self._getExplanationRelatedSimulationMovementValueList(
                                                                explanation):
      if movement.getSimulationState() not in acceptable_state_list:
        return False
    return True

  security.declareProtected(Permissions.AccessContentsInformation,
      'isPartiallyCompleted')
  def isPartiallyCompleted(self, explanation):
    """returns True if some related simulation movements for this explanation
    document are in a simulation state which is considered as completed
    according to the configuration of the current business path.
    Completed means that it is possible to move to next step
    of Business Process. This method does not check however whether previous
    trade states of a given business process are completed or not.
    Use instead IBusinessLinkProcess.isBusinessLinkCompleted for this purpose.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union
                   business process.
    """
    acceptable_state_list = self.getCompletedStateList()
    for movement in self._getExplanationRelatedSimulationMovementValueList(
                                                                explanation):
      if movement.getSimulationState() in acceptable_state_list:
        return True
    return False

  security.declareProtected(Permissions.AccessContentsInformation, 'isFrozen')
  def isFrozen(self, explanation):
    """returns True if all related simulation movements for this explanation
    document are in a simulation state which is considered as frozen
    according to the configuration of the current business path.
    Frozen means that simulation movement cannot be modified.
    This method does not check however whether previous
    trade states of a given business process are completed or not.
    Use instead IBusinessLinkProcess.isBusinessLinkCompleted for this purpose.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union
                   business process.

    NOTE: simulation movements can be frozen (ex. in 'stopped' state) but
    not yet completed (ex. in 'delivered' state).
    """
    acceptable_state_list = self.getFrozenStateList()
    movement_list = self._getExplanationRelatedSimulationMovementValueList(
                                                                explanation)
    if not movement_list:
      return False # Frozen is True only if some delivered movements exist
    for movement in movement_list:
      if movement.getSimulationState() not in acceptable_state_list:
        return False
    return True

  security.declareProtected(Permissions.AccessContentsInformation, 'isDelivered')
  def isDelivered(self, explanation):
    """Returns True is all simulation movements related to this
    Business Link in the context of given explanation are built
    and related to a delivery through the 'delivery' category.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union
                   business process.
    """
    for simulation_movement in self._getExplanationRelatedSimulationMovementValueList(
        explanation):
      if not simulation_movement.getDelivery():
        return False
    return True

  def build(self, explanation=None, **kw):
    """Builds all related movements in the simulation using the builders
    defined on the Business Link.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union
                   business process.
    kw -- optional parameters passed to build method
    """
    builder_list = self.getDeliveryBuilderValueList()
    for builder in builder_list: # XXX-JPS Do we really need a builder list ? wouldn't predicate be more useful ?
      # Call build on each builder
      # Provide 2 parameters: self and and explanation_cache
      builder.build(explanation=explanation, business_link=self, **kw)
