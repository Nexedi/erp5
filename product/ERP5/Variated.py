##############################################################################
#
# Copyright (c) 2002, 2006 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Context, interfaces, Permissions
from Products.ERP5Type.Base import Base
from Products.CMFCategory.Renderer import Renderer

from warnings import warn
from zope.interface import implements

class Variated(Base):
  """
    Variated is a mix-in class for all classes which implement
    the Variated Interface.

    A Variable object is an object which can variate
    according to multiple dimensions. Variable objects include:

    - a Resource instance

    - an Amount instance (a Movement, a DeliveryLine, etc.)

    - an Item

    - a TransformedResource instance
  """

  # Declarative security
  security = ClassSecurityInfo()

  # Declarative interfaces
  implements(interfaces.IVariated)

  security.declareProtected(Permissions.AccessContentsInformation, 
                            'getVariationBaseCategoryList')
  def getVariationBaseCategoryList(self, omit_optional_variation=0,
      omit_option_base_category=None, omit_individual_variation=0):
    """
      Return the list of variation base category.
      If omit_optional_variation==1, do not include base category
      considered as option (ex: industrial_phase).
    """
    #XXX backwards compatibility
    if omit_option_base_category is not None:
      warn("Please use omit_optional_variation instead of"\
          " omit_option_base_category.", DeprecationWarning)
      omit_optional_variation = omit_option_base_category

    vbcl = self._baseGetVariationBaseCategoryList()
    if omit_optional_variation == 1:
      # XXX First implementation
      # option base category list is a portal method, until the creation
      # of a good API.
      option_base_category_list = self.getPortalOptionBaseCategoryList()
      vbcl = [x for x in vbcl if x not in option_base_category_list]
    else:
      vbcl.extend(self.getOptionalVariationBaseCategoryList())
      
    if omit_individual_variation == 0:
      vbcl.extend(self.getIndividualVariationBaseCategoryList())
      
    return vbcl

  security.declareProtected(Permissions.AccessContentsInformation, 
                            '_getVariationCategoryList')
  def _getVariationCategoryList(self, base_category_list = ()):
    if base_category_list is ():
      base_category_list = self.getVariationBaseCategoryList()
#       base_category_list = self.getVariationRangeBaseCategoryList()
    return self.getAcquiredCategoryMembershipList(base_category_list, base=1)

  security.declareProtected(Permissions.AccessContentsInformation, 
                            'getVariationCategoryList')
  def getVariationCategoryList(self, base_category_list=(),
      omit_optional_variation=0, omit_option_base_category=None):
    """
      Returns the list of possible variations
    """
    #XXX backwards compatibility
    if omit_option_base_category is not None:
      warn("Please use omit_optional_variation instead of"\
          " omit_option_base_category.", DeprecationWarning)
      omit_optional_variation = omit_option_base_category

    return self._getVariationCategoryList(
                                  base_category_list=base_category_list)

  security.declareProtected(Permissions.AccessContentsInformation, 
                            'getVariationCategoryItemList')
  def getVariationCategoryItemList(self, base_category_list=(), base=1,
      display_id='logical_path', display_base_category=1,
      current_category=None, omit_optional_variation=0,
      omit_option_base_category=None, **kw):
    """
      Returns the list of possible variations
    """
    #XXX backwards compatibility
    if omit_option_base_category is not None:
      warn("Please use omit_optional_variation instead of"\
          " omit_option_base_category.", DeprecationWarning)
      omit_optional_variation = omit_option_base_category

    variation_category_item_list = []
    if current_category is not None:
      variation_category_item_list.append((current_category,current_category))

    if base_category_list is ():
      base_category_list = self.getVariationBaseCategoryList()
      if omit_optional_variation == 1:
        base_category_list = [x for x in base_category_list if x not in
                              self.getPortalOptionBaseCategoryList()]
    # Prepare 2 rendering
    portal_categories = self.portal_categories
    for base_category in base_category_list:
      variation_category_list = self._getVariationCategoryList(
                                       base_category_list=[base_category])
      
      category_list = []
      object_list = []
      for variation_category_path in variation_category_list:
        try:
          variation_category = portal_categories.resolveCategory(
                                    variation_category_path)
          var_cat_portal_type = variation_category.getPortalType()
        except AttributeError:
          variation_category_item_list.append((variation_category_path,
                                               variation_category_path))
        else:
          if var_cat_portal_type != 'Category':
            object_list.append(variation_category)
          else:
            category_list.append(variation_category)
      # Render categories
      variation_category_item_list.extend(Renderer(
                             display_base_category=display_base_category,
                             display_none_category=0, base=base,
                             current_category=current_category,
                             display_id=display_id, **kw).\
                                               render(category_list))
      # Render the others
      variation_category_item_list.extend(Renderer(
                             base_category=base_category,
                             display_base_category=display_base_category,
                             display_none_category=0, base=base,
                             current_category=current_category,
                             display_id='title', **kw).\
                                               render(object_list))
    return variation_category_item_list
  
  # XXX Is it used ?
#   def getVariationCategoryTitleOrIdItemList(self, base_category_list=(), 
#                                             base=1, **kw):
#     """
#     Returns a list of tuples by parsing recursively all categories in a
#     given list of base categories. Uses getTitleOrId as method
#     """
#     return self.getVariationCategoryItemList(
#                    display_id='title_or_id', 
#                    base_category_list=base_category_list, base=base, **kw)

  security.declareProtected(Permissions.ModifyPortalContent, 
                            '_setVariationCategoryList')
  def _setVariationCategoryList(self, node_list, base_category_list=()):
    if base_category_list is ():
      base_category_list = self.getVariationBaseCategoryList()
    self._setCategoryMembership(base_category_list,node_list,base=1)

  security.declareProtected(Permissions.ModifyPortalContent, 
                            'setVariationCategoryList')
  def setVariationCategoryList(self, node_list, base_category_list=()):
    self._setVariationCategoryList(node_list, 
                                   base_category_list=base_category_list)
    self.reindexObject()

  # Range
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationRangeBaseCategoryList')
  def getVariationRangeBaseCategoryList(self):
      """
      Returns possible variation base_category ids.
      """
      # Get a portal method which defines a list of 
      # variation base category
      return self.getPortalVariationBaseCategoryList()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationRangeBaseCategoryItemList')
  def getVariationRangeBaseCategoryItemList(self, base=1, 
                                            display_id='getTitle', 
                                            current_category=None):
      """
        Returns possible variations of the resource
        as a list of tuples (id, title). This is mostly
        useful in ERP5Form instances to generate selection
        menus.
      """
      return self.portal_categories.getItemList(
                            self.getVariationBaseCategoryList())

  security.declareProtected(Permissions.AccessContentsInformation,
                                    'getVariationBaseCategoryItemList')
  def getVariationBaseCategoryItemList(self, display_id='title_or_id',
        omit_optional_variation=0, omit_option_base_category=None,
        omit_individual_variation=0):
      """
        Returns base category of the resource
        as a list of tuples (title, id). This is mostly
        useful in ERP5Form instances to generate selection
        menus.
      """
      #XXX backwards compatibility
      if omit_option_base_category is not None:
        warn("Please use omit_optional_variation instead of"\
            " omit_option_base_category.", DeprecationWarning)
        omit_optional_variation = omit_option_base_category

      variation_base_category_list = self.getVariationBaseCategoryList(
          omit_optional_variation=omit_optional_variation,
          omit_individual_variation=omit_individual_variation)
      result = []
      for base_category in variation_base_category_list:
        bc = self.portal_categories.resolveCategory(base_category)
        result.extend(Renderer(display_base_category=0, 
                               display_none_category=0, base=1,
                               display_id=display_id).render([bc]))
      return result

  # Methods for matrix UI widgets
  # XXX FIXME Those method are depreciated.
  # We now use _asCellRange scripts.
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getLineVariationRangeCategoryItemList')
  def getLineVariationRangeCategoryItemList(self):
    """
      Returns possible variations in line
    """
    try:
      resource = self.getDefaultResourceValue()
    except AttributeError:
      resource = None
    if resource is not None:
      clist = resource.getVariationRangeCategoryItemList(
                       base_category_list=self.getVariationBaseCategoryLine(),
                       root=0)
    else:
      clist = [(None,None)]
    return clist

  security.declareProtected(Permissions.AccessContentsInformation,
                                       'getColumnVariationRangeCategoryItemList')
  def getColumnVariationRangeCategoryItemList(self):
    """
      Returns possible variations in column
    """
    try:
      resource = self.getDefaultResourceValue()
    except AttributeError:
      resource = None
    if resource is not None:
      clist = resource.getVariationRangeCategoryItemList(base_category_list =
                                       self.getVariationBaseCategoryColumn(), root=0)
    else:
      clist = [(None,None)]
    return clist

  security.declareProtected(Permissions.AccessContentsInformation,
                               'getTabVariationRangeCategoryItemList')
  def getTabVariationRangeCategoryItemList(self):
    """
      Returns possible variations in tab
    """
    try:
      resource = self.getDefaultResourceValue()
    except AttributeError:
      resource = None
    if resource is not None:
      clist = resource.getVariationRangeCategoryItemList(base_category_list =
                                       self.getVariationBaseCategoryTabList(), root=0)
    else:
      clist = [(None,None)]
    return clist

  # Help
  security.declareProtected(Permissions.AccessContentsInformation,
                                        'getMatrixVariationRangeBaseCategoryList')
  def getMatrixVariationRangeBaseCategoryList(self):
    """
      Return base categories used in the matrix
    """
    line_bc= self.getVariationBaseCategoryLine()
    column_bc = self.getVariationBaseCategoryColumn()
    # We need to copy values first
    tab_bc = list(self.getVariationBaseCategoryTabList())
    result = tab_bc
    if line_bc is not None and line_bc is not '':
      result += [line_bc]
    if column_bc is not None and column_bc is not '':
      result += [column_bc]
    return result

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationRangeCategoryItemList')
  def getVariationRangeCategoryItemList(self, base_category_list=(), base=1, 
                                        root=1,
                                        display_method_id='getCategoryChildLogicalPathItemList',
                                        display_base_category=1,
                                        current_category=None, **kw):
    """
    Returns possible variations
      => [(display, value)]
    """
    result = []
    if base_category_list is ():
      base_category_list = self.getVariationBaseCategoryList()
    elif type(base_category_list) is type('a'):
      base_category_list = (base_category_list, )

    traverse = getToolByName(self, 'portal_categories').unrestrictedTraverse
    # Render categories
    for base_category in base_category_list:
      result += getattr(traverse(base_category), display_method_id)(
                             base=base,
                             display_base_category=display_base_category,
                             display_none_category=0, **kw)
    # Return result
    return result

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariationRangeCategoryList')
  def getVariationRangeCategoryList(self, base_category_list=(), base=1,
                                    root=1, current_category=None,
                                    omit_individual_variation=0):
    """
      Returns the range of acceptable categories
    """
    vrcil = self.getVariationRangeCategoryItemList(
                          base_category_list=base_category_list,
                          base=base, root=root, 
                          current_category=current_category,
                          omit_individual_variation=omit_individual_variation)
    # display is on left
    return [x[1] for x in vrcil]

  # Context related methods
  security.declarePublic('newVariationValue')
  def newVariationValue(self, context=None, REQUEST=None, **kw):
    # PERFORMANCE ISSUE
    from Products.ERP5.VariationValue import newVariationValue
    if context is None:
      return newVariationValue(REQUEST=REQUEST, **kw)
    else:
      return newVariationValue(context=context, REQUEST=REQUEST, **kw)

  # Provide a string representation of variations
  security.declarePublic('getVariationText')
  def getVariationText(self):
    """
      Provide a string representation of variation
    """
    category_list = list(self.getVariationCategoryList())
    category_list.sort()
    return '\n'.join(category_list)

InitializeClass(Variated)
