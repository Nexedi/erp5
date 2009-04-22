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

from Interface import Interface

class IMovement(Interface):
  """
  A movement represents amount of resource how are changed
  on the path. The movement should be ables to provide how 
  amount is/was existed on node both source and destination.
  Because of movement may be affected on path.

  The movement interface can be represents any kind of delivery.
  It is useful to represent changed of between nodes.

  Equations:
    destination_quantity = source_quantity * efficiency
    (These values can be calculated by Amount)


    Production/Consumption

    (A -> B)
    if source_quantity > 0 and destination_quantity > 0
    production_quantity = destination_quantity
    consumption_quantity = source_quantity

    if source_quantity < 0 and destination_quantity < 0
    production_quantity = - source_quantity
    consumption_quantity = - destination_quantity

    if source_quantity < 0 and destination_quantity > 0
    or
    source_quantity > 0 and destination_quantity < 0
    raise 


    (A -> Nothing)
    if source_quantity > 0
    consumption_quantity = source_quantity
    production_quantity = 0

    if source_quantity < 0
    consumption_quantity = 0
    production_quantity = - source_quantity

    (Nothing -> B)
    if destination_quantity > 0
    consumption_quantity = 0
    production_quantity = destination_quantity

    if destination_quantity < 0
    consumption_quantity = - destination_quantity 
    production_quantity = 0


    Credit/Debit

    (A -> B)
    if source_quantity > 0 and destination_quantity > 0
    source_credit = - source_quantity
    source_debit = source_quantity
    destination_credit = destination_quantity
    destination_debit = - destination_quantity

    if source_quantity < 0 and destination_quantity < 0
    source_credit = source_quantity
    source_debit = - source_quantity
    destination_credit = - destination_quantity
    destination_debit = destination_quantity

    if source_quantity < 0 and destination_quantity > 0
    or
    source_quantity > 0 and destination_quantity < 0
    raise

    (A -> Nothing)
    if source_quantity > 0
    source_credit = source_quantity
    source_debit = - source_quantity
    destination_credit = 0
    destination_debit = 0

    if source_quantity < 0
    source_credit = - source_quantity
    source_debit = source_quantity
    destination_credit = 0 
    destination_debit = 0

    (Nothing -> B)
    if destination_quantity > 0
    source_credit = 0
    source_debit = 0
    destination_credit = destination_quantity
    destination_debit = - destination_quantity

    if destination_quantity < 0
    source_credit = 0
    source_debit = 0
    destination_credit = - destination_quantity
    destination_debit = destination_quantity

    source_asset_price = price
    destination_asset_price = price
  """

  # Conversion API for cataloging
  def getConvertedSourceQuantity():
    """
      Returns the quantity how are removed
      from source by the movement
    """

  def getConvertedDestinationQuantity():
    """
      Returns the quantity how are reached
      to destination by the movement
    """

  # Helper methods for Production
  def getConsumptionQuantity():
    """
      Returns the quantity how are consumed
      on the path by the movement
    """

  def getProductionQuantity():
    """
      Returns the quantity how are produced
      on the path by the movement
    """

  # Helper methods for Accounting
  def getSourceDebit():
    """
      Returns the quantity how are debited
      from source node by the movement
    """

  def getSourceCredit():
    """
      Returns the quantity how are credited
      from source node by the movement
    """

  def getDestinationDebit():
    """
      Returns the quantity how are debited
      to destination node by the movement
    """

  def getDestinationCredit():
    """
      Returns the quantity how are credited
      to destination node by the movement
    """

  def getSourceAssetPrice():
    """
      Returns the price how are taken
      from source by the movement
    """

  def getSourceInventoriatedTotalAssetPrice():
    """
      Returns a price which can be used
      to calculate stock value (asset)
    """

  def getSourceInventoriatedTotalAssetDebit():
    """
      Returns the debit part of inventoriated
      source total asset price.
    """

  def getSourceInventoriatedTotalAssetCredit():
    """
      Returns the credit part of inventoriated
      source total asset price.
    """

  def getSourceAssetDebit():
    """
      Return the debit part of the source total
      asset price.
    """

  def getSourceAssetCredit():
    """
      Return the credit part of the source total
      asset price.
    """

  def getDestinationAssetPrice():
    """
      Returns the price how are given
      to destination by the movement
    """

  def getDestinationInventoriatedTotalAssetPrice():
    """
      Returns a price which can be used
      to calculate stock value (asset)
    """

  def getDestinationInventoriatedTotalAssetDebit():
    """
      Returns the debit part of inventoriated
      destination total asset price.
    """

  def getDestinationInventoriatedTotalAssetCredit():
    """
      Returns the credit part of inventoriated
      destination total asset price.
    """

  def getDestinationAssetDebit():
    """
      Return the debit part of the destination total
      asset price.
    """

  def getDestinationAssetCredit():
    """
      Return the credit part of the destination total
      asset price.
    """
