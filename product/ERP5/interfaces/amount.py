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

from zope.interface import Interface

class IAmount(Interface):
  """Amount interface specification

    An amount represents a quantity of a given resource
    in a given quantity unit. Optional efficiency can be
    specified in order to represent a loss ratio to take
    into account in calculations. Loss ratio is normally
    used only in Path.

    The Amount interface is useful each time
    we need to add or substract amounts of resources
    independently of a movement. This is the case for example
    for all Transformation related classes.

    Equations:
      net_quantity = quantity * efficiency

    TODO:
      1. make sure getTotalPrice has or does not
         have extra parameters (ex. rounding)
      2. remove profit_quantity everywhere
      3. remove target_quantity everywhere
      4. consider how to make Interface compatible
         with accessor generation (ex. getResource,
         getQuantity, etc.)
      5. consider creating an IPriceable interface
         which is common to deliveries and amounts
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
      reversely wrt. to the sign of quantity.

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
      Returns the ratio of loss for the given amount. This
      is only used in Path such as Transformation. In other
      words, efficiency of movements is always 100%.
    """

  def getNetQuantity():
    """
      Returns the quantity multiplied by the ratio.
    """

  # Price API
  def getPrice():
    """
      Returns the unit price of the resource
    """
  
  def getTotalPrice():
    """
      Returns total price ie. the unit price of the resource
      multiplied by the quantity.
    """

  # Conversion API
  def getConvertedQuantity():
    """
      Returns the quantity of the resource converted in the
      management unit of the resource
    """

  def getNetConvertedQuantity():
    """
      Returns the net quantity of the resource converted in the
      management unit of the resource
    """

  # Make it possible to add amounts
  def __add__(value):
    """Add an amount to another amount

      'value' is an IAmount document
    """

  def __sub__(value):
    """Substract an amount from another amount

      'value' is an IAmount document
    """

  def __mul__(value):
    """Multiply an Amount by a float

      'value' is a float
    """

  def __div__(value):
    """Divide an Amount by a float

      'value' is a float
    """
