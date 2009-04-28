##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

class Variated(Interface):
  """
    Common Interface for all objects which can be
    variated.
  """

  # The following methods are intended to access to the
  # variation value of a variated object. Discrete variations
  # are based on categories. General variations are encapsulated
  # into VariationValue instances.

  # Discrete Variation accessors
  def getVariationCategoryList():
    """
      returns a list or relative URLs which defines
      a discrete variation (ie. a list of category
      memberships)
    """
    pass

  def _setVariationCategoryList(node_list):
    """
      modifies the discrete variation of an
      variated instance by providing a list
      of relative URLs
    """
    pass

  def setVariationCategoryList(node_list):
    """
      modifies the discrete variation of an
      variated instance by providing a list
      of relative URLs

      reindexes the object
    """
    pass

  def getVariationBaseCategoryList(node_list):
    """
      returns a list of base category ids
      which are used to define discrete variations
      for this instance
    """
    pass

  def _setVariationBaseCategoryList(node_list):
    """
      modifies the list of base category ids
      which are used to define discrete variations
      for this instance
    """
    pass

  def setVariationBaseCategoryList(node_list):
    """
      modifies the list of base category ids
      which are used to define discrete variations
      for this instance
    """
    pass

  # General Variation accessors
  def getVariationValue():
    """
      Returns a VariationValue object. 
    """
    pass

  def _setVariationValue(value):
    """
      Private setter for VariationValue.
    """
    pass

  def setVariationValue(value):
    """
      Sets the VariationValue.
    """
    pass


  # The following methods are intended to access the
  # variation range of a variated object. A Variation range can
  # be defined in a Resource instance or in any object
  # which has a relation with a Resource (Amount, Transformation)

  # Discrete Variation Range accessors

  def getVariationRangeCategoryList(base_category_list=(), base=1):
    """
      returns a list of categories which are acceptable
      as discrete variation values
    """
    pass

  def getVariationRangeCategoryItemList(base_category_list=(),
                          display_id='getTitle', base=1, current_category=None):
    """
      returns a list of (category.id, category.display_id()) which are acceptable
      as discrete variation values
    """
    pass

  def getVariationRangeBaseCategoryList(base_category_list=(), base=1):
    """
      returns a list of base categories which are acceptable
      as discrete variation values
    """
    pass

  def getVariationRangeBaseCategoryItemList(base_category_list=(),
                          display_id='getTitle', base=1, current_category=None):
    """
      returns a list of base category items which are acceptable
      as discrete variation values
    """
    pass
