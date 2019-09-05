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

from Products.ERP5.interfaces.amount import IAmount

class IAssetMovement(IAmount):
  """Asset Movement private interface specification

  Asset movements are use to represent the asset
  value of a movement of resources leaving a
  source and reach a destination.
  """
  # We must a find a way to use property sheets in or as interfaces
  # property_sheets = (PropertySheet.Price, )

  def getSourceAssetPrice():
    """
    Return the asset price for the source section,
    usually the price of the movement converted to
    the currency of the source section using the currency
    rate of the day. If no price is defined, an internal
    price may be looked up. It is also possible for
    a movement to have 'None' source asset price,
    for example for a movement with positive quantity
    going from one warehouse to another warehouse of
    the same company.
    """

  def getDestinationAssetPrice():
    """
    Return the asset price for the destination section,
    usually the price of the movement converted to
    the currency of the destination section using the currency
    rate of the day. If no price is defined, an internal
    price may be looked up first. It is also possible for
    a movement to have 'None' destination asset price,
    for example for a movement with negative quantity
    going from one warehouse to another warehouse of
    the same company.
    """

  def getSourceInventoriatedTotalAssetPrice():
    """
    Returns the total asset price for the source section, either
    defined explicitely by the source_asset_price property
    (as in accounting) or by calling getSourceAssetPrice and
    multiplying it by the quantity. If no asset price
    is defined, return None. Asset calculation methods
    (SimulationTool.getInventoryAssetPrice) interprete
    None using FIFO, FILO or Average algorithm.
    """

  def getDestinationInventoriatedTotalAssetPrice():
    """
    Returns the total asset price for the destination section, either
    defined explicitely by the destination_asset_price property
    (as in accounting) or by calling getDestinationAssetPrice and
    multiplying it by the quantity. If no asset price
    is defined, return None. Asset calculation methods
    (SimulationTool.getInventoryAssetPrice) interprete
    None using FIFO, FILO or Average algorithm.
    """
