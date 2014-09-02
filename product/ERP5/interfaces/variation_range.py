# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
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
Products.ERP5.interfaces.variated
"""

from zope.interface import Interface

class IVariationRange(Interface):
  """IVariationRange interface specification

  Common Interface for all objects which define a variation
  range.
  """

  # provides VariationRange accessors

  # Discrete Variation Range Accessors
  def setVariationBaseCategoryList(base_category_id_list):
    """
    modifies the list of base category ids which are used to
    define discrete variation dimensions for this instance.
    Normally provided by the VariationRange property sheet.

    Used in: Resource, Delivery Line

    base_category_id_list --
    """

  # Matrix Handling API
  def getLineVariationRangeCategoryItemList():
    """
    returns possible variation dimensions displayed in line.

    Used in: Resource, Delivery Line

    XXX - missing default display ID
    """

  def getColumnVariationRangeCategoryItemList():
    """
    returns possible variation dimensions displayed in column

    Used in: Resource, Delivery Line

    XXX - missing default display ID
    """

  def getTabVariationRangeCategoryItemList():
    """
    returns possible variation dimensions displayed in tab

    Used in: Resource, Delivery Line

    XXX - missing default display ID
    """

  def getMatrixVariationRangeBaseCategoryList():
    """
    return possible variation dimensions for a matrix

    Used in: Resource, Delivery Line

    XXX - missing default display ID
    """
