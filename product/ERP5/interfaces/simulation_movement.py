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
Products.ERP5.interfaces.simulation_movement
"""

from Products.ERP5.interfaces.property_recordable import IPropertyRecordable
from Products.ERP5.interfaces.movement import IMovement
from Products.ERP5.interfaces.divergence_controller import IDivergenceController
from Products.ERP5.interfaces.business_completable import IBusinessCompletable

class ISimulationMovement(IMovement, IPropertyRecordable, IDivergenceController, IBusinessCompletable):
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
    """
    Returns quantity which was actually shipped, taking
    into account the errors of the simulation fixed by
    the delivery:
      quantity + delivery_error
    """

  def isDeletable():
    """
    Returns True is this simumlation can be deleted, False
    else.
    """
