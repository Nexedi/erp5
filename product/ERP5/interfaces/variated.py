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

class IVariated(Interface):
  """IVariated interface specification

  IVariated defines methods to access and modify
  discrete variations (categories) and variation
  properties. It also provides variation range methods
  which are often invoked from variated objects.

  IVariated is normally used to specify discrete variations
  of a movement.

  IVariated is also used on all objects which define
  a variation range, such as Resources, Delivery Lines
  which contain Delivery Cells. In this case, categories
  specify a subset of the total variation range, rather
  than a specific discrete variation.
  """

  # The following methods are intended to access to the
  # variation value of a variated object. Discrete variations
  # are based on categories. General variations are encapsulated
  # into Individual Variation instances.

  # Property Variation Accessors
  def getVariationPropertyList():
    """
    return the list of variation property IDs which are provided
    by the variated instance.

    Used in: Resource, Delivery Line, Delivery Cell
    """

  # Discrete Variation Accessors
  def getVariationBaseCategoryList(omit_optional_variation=0,
                                   omit_individual_variation=0):
    """
    returns a list of base category ids which are used
    to define discrete variation dimensions for this instance

    Used in: Resource, Delivery Line, Delivery Cell

    omit_optional_variation --

    omit_individual_variation --
    """

  def getVariationBaseCategoryItemList(display_id='title_or_id',
        omit_optional_variation=0, omit_individual_variation=0):
    """
    returns a list of (base_category.id, base_category.display_id())
    which can be displayed in an ERP5 Form and define
    to define discrete variation dimensions for this instance

    Used in: Resource, Delivery Line, Delivery Cell

    display_id --

    omit_optional_variation --

    omit_individual_variation --
    """

  def getVariationCategoryList(base_category_list=(),
        omit_optional_variation=0, omit_individual_variation=0):
    """
    returns a list or relative URLs which defines
    a discrete variation (ie. a list of category
    memberships)

    Used in: Resource, Delivery Line, Delivery Cell

    base_category_list --

    omit_optional_variation --

    omit_individual_variation --
    """

  def setVariationCategoryList(node_list, base_category_list=()):
    """
    modifies the discrete variation of a variated instance by
    providing a list of relative URLs

    Used in: Resource, Delivery Line, Delivery Cell

    base_category_list --
    """

  def getVariationCategoryItemList(base_category_list=(), base=1,
        display_id='logical_path', display_base_category=1,
        current_category=None, omit_optional_variation=0,
        omit_individual_variation=0, **kw):
    """
    returns a list of (category.getRelativeUrl(), category.display_id())
    which define the discrete variations  of a variated instance
    in a way which be displayed in an ERP5 Form.

    Used in: Resource, Delivery Line, Delivery Cell

    base_category_list --

    base --

    display_id --

    display_base_category --

    base_category_list --

    current_category --

    omit_optional_variation --

    omit_individual_variation --

    **kw --
    """

  # Discrete Variation Range Accessors
  def getVariationRangeBaseCategoryList():
    """
    returns a list of base categories which are acceptable
    as discrete variation dimensions

    Used in: Resource, Delivery Line, Delivery Cell
    """

  def getVariationRangeBaseCategoryItemList(base=1,
                                            display_id='getTitle'):
    """
    returns a list of (base_category.id, base_category.display_id())
    which are acceptable as discrete variation dimensions of
    the variated instance and are easy to display in an ERP5Form

    Used in: Resource, Delivery Line, Delivery Cell

    display_id --
    """

  def getVariationRangeCategoryList(base_category_list=(), base=1,
        root=1, current_category=None, omit_individual_variation=0):
    """
    returns a list of categories which are acceptable
    as discrete variation values of the current variated instance

    Used in: Resource, Delivery Line, Delivery Cell

    base_category_list --

    base --

    root --

    current_category --

    omit_individual_variation --
    """

  def getVariationRangeCategoryItemList(base_category_list=(), base=1,
        root=1, display_method_id='getCategoryChildLogicalPathItemList',
        display_base_category=1, current_category=None, **kw):
    """
    returns a list of (category.id, category.display_id()) which are acceptable
    as discrete variation values. This is mostly useful in ERP5Form
    instances to generate selection menus.

    Used in: Resource, Delivery Line, Delivery Cell

    base_category_list --

    base --

    root --

    display_method_id --

    display_base_category --

    current_category --

    **kw --
    """

  # Variated Value API
  def setVariated(variated):
    """
    Sets all variation categories and properties of the current
    variated instance to the categories and properties of
    variated instance provided as parameter.

    Used in: Resource, Delivery Line, Delivery Cell

    variated --
    """

  def compareVariated(variated):
    """
    Compares current variated instance with another
    variated instance provided as parameter.

    Used in: Resource, Delivery Line, Delivery Cell

    variated --
    """

  # Serialization API
  def getVariationText():
    """
    returns a human readable, computer parsable,
    non ambiguous string representation of the variation
    categories and properties of the current instance.

    Used in: Delivery Line (terminal), Delivery Cell
    """

  def setVariationText(variation_text):
    """
    parses variation_text to set variation properties
    and categories of the current instance

    Used in: Delivery Line (terminal), Delivery Cell
    Could be used in: Resource, Delivery Line (non terminal)
    """

  def getVariationUid():
    """
    returns a unique UID integer representation of the variation
    categories and properties of the current instance based
    on a UID mapping of variation_text

    Used in: Delivery Line (terminal), Delivery Cell
    Could be used in: Resource, Delivery Line (non terminal)
    """

  def setVariationUid(variation_uid):
    """
    sets variation properties and categories of the current instance
    by looking up variation to UID mapping

    Used in: Delivery Line (terminal), Delivery Cell
    Could be used in: Resource, Delivery Line (non terminal)
    """
