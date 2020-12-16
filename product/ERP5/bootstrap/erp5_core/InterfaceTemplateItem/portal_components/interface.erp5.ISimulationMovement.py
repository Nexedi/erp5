# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
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
"""
erp5.component.interface.ISimulationMovement
"""

from Products.ERP5.interfaces.property_recordable import IPropertyRecordable
from erp5.component.interface.IMovement import IMovement
from erp5.component.interface.IDivergenceController import IDivergenceController
from erp5.component.interface.IExplainable import IExplainable

class ISimulationMovement(IMovement, IPropertyRecordable, IDivergenceController, IExplainable):
  """Simulation Movement interface specification

  The ISimulationMovement interface introduces in addition
  to IMovement the possibility to record properties by
  inheriting IPropertyRecordable, and to track rounding
  or non linearities of quantity at build time.

  The main equation to consider is:
      quantity(SM) + delivery_error (SM) =
        quantity(DL) * delivery_ratio(SM)
  where SM is a simulation movement and DL a delivery line.

  During the expand process, parent applied rules
  may define the quantity of the simulation movement,
  but not the delivery_error.

  During the build process, delivery_error can be used
  to store on the simulation movement amounts related
  to rounding or to floating point precision errors.

  During the expand process, child applied rules
  use getDeliveryQuantity rather than getQuantity.

  Solving quantity divergences can thus be obtained either
  by changing quantity (which then needs to backtracking)
  or by changing delivert_error (no backtracking needed)
  """
  def getDeliveryRatio():
    """
    Returns ratio to apply on the quantity
    property of the corresponding delivery
    to obtain the current quantity

    NOTE: redundant with Simulation Property Sheet
    """

  def getDeliveryError():
    """
    Returns correction to make the match
    between delivery quantity and simulation
    quantity consistent

    NOTE: redundant with Simulation Property Sheet
    """

  def getDeliveryQuantity():
    """ Returns quantity which was actually shipped, taking
    into account the errors of the simulation fixed by
    the delivery:

       quantity + delivery_error
    """

  def isDeletable():
    """Returns True if this simulation movement can be deleted, False
    else. A simulation movement can be deleted if it is not frozen,
    and if all its children can be deleted or if it has no child.
    """

  def isCompleted():
    """Returns True if the simulation state of this simulation movement
    is considered as completed by the business path which this simulation
    movement relates to through causality base category.

    NOTE: simulation movements can be completed (ex. in started state) but
    not yet frozen (ex. in delivered state). This is the case for example
    of accounting movements which are completed as soon as they are posted
    (to allow next steps in the business process) but can still be modified
    are thus not yet frozen.
    """

  def isFrozen():
    """Returns True if the simulation state of this simulation movement
    is considered as frozen by the business path which this simulation
    movement relates to through causality base category.

    Frozen means that simulation movement cannot be modified anylonger.

    NOTE: simulation movements can be frozen (ex. in stopped state) but
    not yet completed (ex. in delivered state). This is the case of
    sales purchase movements which are frozen as soon they are received
    because they should not be modified any longer but are only completed
    once some extra steps bring them to delivered state, thus allowing the
    generation of planned purchase invoice.
    """
