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

class IAmount(Interface):
  """
    An amount represents a quantity of a given resource
    in a given quantity unit. Optional efficiency
    or (exclusive) profit/loss quantity can be specified
    in order to represent a profit or loss ratio to take
    into account in calculations.

    The Amount interface is useful each time
    we need to add or substract amounts of resources
    independently of a movement. This is the case for example
    for all Transformation related classes.

    Equations:
      net_quantity = quantity * efficiency

    TODO:
      consider how to make Interface compatible
      with accessor generation (ex. getResource)

    Addition:
      target_quantity is obsolete, it is never defined.
  """

  # Core API
  def getQuantity():
    """
      Returns the quantity of the resource
      in the unit specified by the Amount
    """

  def getResource():
    """
      Returns the resource category relative URL
      of the Amount
    """

  def getQuantityUnit():
    """
      Returns the quantity unit category relative URL
      of the Amount
    """

  def isCancellationAmount():
    """
      A cancellation amount must be interpreted
      reversely write to the sign of qauntity.

      For example, a negative credit for a cancellation
      amount is a negative credit, not a positive
      debit.

      A negative production quantity for a cancellation
      amount is a cancelled production, not
      a consumption
    """

  # Net Quantity API
  def getEfficiency():
    """
      Returns a value which is rate affect to the net quantity
      Only used for transformation for now.
    """

  def getNetQuantity():
    """
      Returns affected quantity by some optional effects.
    """

  # Price API

  def getPrice():
    """
      Returns price
    """
  
  def getTotalPrice():
    """
      Returns total price for the number of items
    """

  # Conversion API
  def getConvertedQuantity():
    """
      Returns the quantity converted by the resource
    """

  def getNetConvertedQuantity():
    """
      Returns the net quantity converted by the resource
    """

  # Make it possible to add amounts
  def __add__(value):
    """
      Add

      If the amount can understands argument as amount for addition,
      returns calculated
    """

  def __sub__(value):
    """
      Substract

      If the amount can understands argument as amount for substraction,
      returns calculated
    """

  def __mul__(value):
    """
      Multiply

      If the amount can understands argument as efficiency for multiplication,
      returns calculated
    """

  def __div__(value):
    """
      Devide

      If the amount can understands argument as efficiency for division,
      returns calculated
    """
