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

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.ERP5Type import Context, Interface, Permissions
from Products.ERP5Type.Base import Base

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
  __implements__ = (Interface.Variated, )

  security.declareProtected(Permissions.AccessContentsInformation, '_getVariationCategoryList')
  def _getVariationCategoryList(self, base_category_list = ()):
    if base_category_list is ():
      base_category_list = self.getVariationRangeBaseCategoryList()
    return self.getAcquiredCategoryMembershipList(base_category_list,base=1)

  security.declareProtected(Permissions.AccessContentsInformation, 'getVariationCategoryList')
  def getVariationCategoryList(self, base_category_list = ()):
    """
      Returns the list of possible variations
    """
    return self._getVariationCategoryList(base_category_list = base_category_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getVariationCategoryItemList')
  def getVariationCategoryItemList(self, base_category_list = (), base=1,
                                        method_id='getTitle', current_category=None):
    """
      Returns the list of possible variation items
    """
    variation_category_item_list = []
    if current_category is not None:
      variation_category_item_list.append(current_category)
    variation_category_list = self.getVariationCategoryList(base_category_list=base_category_list)
    for variation_category in variation_category_list:
      resource = self.portal_categories.resolveCategory(variation_category)
      value = getattr(resource, method_id)()
      if base:
        label = variation_category
      else:
        index = variation_category.find('/') + 1
        label = variation_category[index:]
      variation_category_item_list.append((value, label))
    return variation_category_item_list

  security.declareProtected(Permissions.ModifyPortalContent, '_setVariationCategoryList')
  def _setVariationCategoryList(self, node_list, base_category_list = ()):
    if base_category_list is ():
      base_category_list = self.getVariationRangeBaseCategoryList()
    self._setCategoryMembership(base_category_list,node_list,base=1)
    # If this is a Transformation, we have to update
    # ranges for each subobject
    for o in self.objectValues():
      if o.hasVVariationBaseCategoryList():
        o.setVVariationBaseCategoryList(o.getVVariationBaseCategoryList())
      if o.hasQVariationBaseCategoryList():
        o.setQVariationBaseCategoryList(o.getQVariationBaseCategoryList())

  security.declareProtected(Permissions.ModifyPortalContent, 'setVariationCategoryList')
  def setVariationCategoryList(self, node_list, base_category_list = () ):
    self._setVariationCategoryList(node_list, base_category_list = base_category_list)
    self.reindexObject()


  # Range
  security.declareProtected(Permissions.AccessContentsInformation,
                                        'getVariationRangeBaseCategoryList')
  def getVariationRangeBaseCategoryList(self):
      """
        Returns possible variation base_category ids of the
        default resource of this transformation
      """
      try:
        resource = self.getDefaultResourceValue()
      except:
        resource = None
      if resource is not None:
        result = resource.getVariationBaseCategoryList()
      else:
        result = self.portal_categories.getBaseCategoryIds()
      return result

  security.declareProtected(Permissions.AccessContentsInformation,
                                    'getVariationRangeBaseCategoryItemList')
  def getVariationRangeBaseCategoryItemList(self, base=1, method_id='getTitle', current_category=None):
      """
        Returns possible variations of the resource
        as a list of tuples (id, title). This is mostly
        useful in ERP5Form instances to generate selection
        menus.
      """
      return self.portal_categories.getItemList(self.getVariationRangeBaseCategoryList())

  # Methods for matrix UI widgets
  security.declareProtected(Permissions.AccessContentsInformation,
                                               'getLineVariationRangeCategoryItemList')
  def getLineVariationRangeCategoryItemList(self):
    """
      Returns possible variations in line
    """
    try:
      resource = self.getDefaultResourceValue()
    except:
      resource = None
    if resource is not None:
      clist = resource.getVariationRangeCategoryItemList(base_category_list =
                                       self.getVariationBaseCategoryLine(), root=0)
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
    except:
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
    except:
      resource = None
    if resource is not None:
      clist = resource.getVariationRangeCategoryItemList(base_category_list =
                                       self.getVariationBaseCategoryTabList(), root=0)
    else:
      clist = [(None,None)]
    return clist

  # Missing methods
  # getVariationBaseCategoryItemList

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
