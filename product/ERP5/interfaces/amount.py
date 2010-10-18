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
Products.ERP5.interfaces.amount
"""

from zope.interface import Interface

class IAmountCore(Interface):
  """Amount Core private interface specification

  IAmountCore defines the minimal set of getters required
  to implement an amount.
  """
  def getQuantity():
    """
    Returns the quantity of the resource
    in the unit specified by the Amount

    NOTE: declaration is redundant with IAmountGetter
    """

  def getResource():
    """
    Returns the resource category relative URL
    of the Amount

    NOTE: declaration is redundant with IAmountGetter
    """

  def getQuantityUnit():
    """
    Returns the quantity unit category relative URL
    of the Amount

    NOTE: declaration is redundant with IAmountGetter
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

    NOTE: declaration is redundant with IAmountGetter
    """

  def getEfficiency():
    """
    Returns the ratio of loss for the given amount. This
    is only used in Path such as Transformation. In other
    words, efficiency of movements is always 100%.

    NOTE: declaration is redundant with IAmountGetter
    """

  def getBaseContributionList():
    """
    The list of bases this amount contributes to. 

    XXX: explain better
    """

  def getBaseApplicationList():
    """
    The list of bases this amount has been applied on. Only set if the
    amount comes from a transformation.

    XXX: explain better
    """

class IAmountConversion(Interface):
  """Amount Conversion private interface specification

  IAmountConversion defines methods which can be used
  to convert an amount from one quantity unit and to another,
  taking into account efficiency.
  """

  def getNetQuantity():
    """
    Take into account efficiency in quantity. This is
    only useful in Path which define a loss ratio, such
    as Transformation. 

    Formula:
      net_quantity = quantity / efficiency
    """

  def getConvertedQuantity(quantity_unit=None, measure=None):
    """
    Returns the quantity of the resource converted in the
    default management unit of the resource.

    quantity_unit -- optional quantity unit to use
                     for conversion.

    measure -- optional quantity unit to use
               for conversion.
    """

  def getNetConvertedQuantity(quantity_unit=None, measure=None):
    """
    Returns the net quantity of the resource converted in the
    default management unit of the resource.

    quantity_unit -- optional quantity unit to use
                     for conversion.

    measure -- optional quantity unit to use
               for conversion.
    """

class IAmountPrice(Interface):
  """Amount Price private interface specification

  IAmountPrice defines methods to compute total price
  and unit price of a resource, taking into account 
  contributions and roundings.
  """
  def getPrice():
    """
    Returns the input unit price of the resource

    NOTE: redundant with IPriceGetter
    """

  def getUnitPrice(base_contribution=None, rounding=False):
    """
    Returns the unit price of the resource, taking into 
    account rounding and contributions (ex. taxes).

    base_contribution -- optional base_contribution.
                If defined, a complex process is launched
                to add or remove to the price various amounts
                calculated from applicable trade models if 
                any.
                
    rounding -- optional rounding parameter. If set to True,
                find and applies appropriate rounding model.
    """

  def getTotalPrice(base_contribution=None, rounding=False):
    """
    Returns total price ie. the unit price of the resource
    multiplied by the quantity, taking into 
    account rounding and contributions (ex. taxes).

    base_contribution -- optional base_contribution.
                If defined, a complex process is launched
                to add or remove to the price various amounts
                calculated from applicable trade models if 
                any.
                
    rounding -- optional rounding parameter. If set to True,
                find and applies appropriate rounding model.
    """

class IAmountArithmetic(Interface):
  """Amount Arithmetic private interface specification

  IAmountArithmetic defines methods to add, substract,
  multiply or device amounts of resources. No rounding
  should happen. All amounts should be converted to 
  the default management unit using getNetConvertedQuantity.
  """
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

class IAmount(IAmountCore, IAmountConversion, IAmountPrice, IAmountArithmetic):
  """Amount interface specification

    An amount represents a quantity of a given resource
    in a given quantity unit. Optional efficiency can be
    specified in order to represent a loss ratio to take
    into account in calculations. Loss ratio is normally
    used only in Path.

    The Amount interface is useful each time
    one needs to add or substract amounts of resources
    independently of a movement. This is the case for example
    for all Transformation related classes.

    TODO-XXX:
      1. Try to merge IAmountPrice and IPriceable
         interface (used for deliveried)
      2. remove profit_quantity and target_quantity everywhere
      3. consider how to make Interface compatible
         with accessor generation (ex. getResource,
         getQuantity, etc.)
  """
