##############################################################################
#
# Copyright (c) 2002 Coramy SAS and Contributors. All Rights Reserved.
#                    Thierry_Faucher <Thierry_Faucher@coramy.com>
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Utils import asList, keepIn, rejectIn

from Products.ERP5.Variated import Variated

from Products.ERP5.Document.Domain import Domain

from Globals import InitializeClass
from Products.PythonScripts.Utility import allow_class

import string
from zLOG import LOG

class Transformation(XMLObject, Domain, Variated):
    """
      Build of material - contains a list of transformed resources

      Use of default_resource... (to define the variation range,
      to ...)

      XXX Transformation works only for a miximum of 3 variation base category...
      Matrixbox must be rewrite for a clean implementation of n base category

    """

    meta_type = 'ERP5 Transformation'
    portal_type = 'Transformation'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.VariationRange
                      , PropertySheet.Domain
                      #, PropertySheet.Resource
                      , PropertySheet.TransformedResource
                      , PropertySheet.Path
                      , PropertySheet.Transformation
                      )

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )


    security.declareProtected(Permissions.AccessContentsInformation, 'updateVariationCategoryList')
    def updateVariationCategoryList(self):
      """
        Check if variation category list of the resource changed and update transformation
        and transformation line
      """
      self.setVariationBaseCategoryList( self.getVariationBaseCategoryList() )
      transformation_line_list = self.contentValues()
      for transformation_line in transformation_line_list:
        transformation_line.updateVariationCategoryList()

    security.declareProtected(Permissions.AccessContentsInformation, 'getVariationRangeBaseCategoryList')
    def getVariationRangeBaseCategoryList(self):
        """
          Returns possible variation base_category ids of the
          default resource which can be used a variation axis
          in the transformation. 
        """
        resource = self.getResourceValue()
        if resource is not None:
          result = resource.getVariationBaseCategoryList()
        else:
          # XXX result = self.getBaseCategoryIds()
          # Why calling this method ?
          # Get a global variable which define a list of variation base category
          result = self.getPortalVariationBaseCategoryList()
        return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getVariationRangeBaseCategoryItemList')
    def getVariationRangeBaseCategoryItemList(self):
        """
          Returns possible variations of the transformation
          as a list of tuples (id, title). This is mostly
          useful in ERP5Form instances to generate selection
          menus.
        """
        return self.portal_categories.getItemList( self.getVariationRangeBaseCategoryList() )


    security.declareProtected(Permissions.AccessContentsInformation,'getVariationRangeCategoryList')
    def getVariationRangeCategoryList(self, base_category_list = ()):
        """
          Returns possible variation category values for the
          transformation according to the default resource.
          Possible category values is provided as a list of
          id.
          User may want to define generic transformation without
          any resource define.
          Result is left display.
        """
        if base_category_list is ():
          base_category_list = self.getVariationBaseCategoryList()

        resource = self.getResourceValue()
        if resource != None:
          result = resource.getVariationRangeCategoryList(base_category_list)
        else:
          # No resource is define on transformation. We want to display content of base categories
          result = self.portal_categories.getCategoryChildList(base_category_list, base=1)
        return result

    security.declareProtected(Permissions.AccessContentsInformation,'getVariationRangeCategoryItemList')
    def getVariationRangeCategoryItemList(self, base_category_list = ()):
        """
          Returns possible variation category values for the
          transformation according to the default resource.
          Possible category values is provided as a list of
          tuples (id, title). This is mostly
          useful in ERP5Form instances to generate selection
          menus.
          User may want to define generic transformation without
          any resource define.
        """
        if base_category_list is ():
          base_category_list = self.getVariationBaseCategoryList()

        resource = self.getResourceValue()
        if resource != None:
          result = resource.getVariationRangeCategoryItemList(base_category_list)
        else:
          # No resource is define on transformation. We want to display content of base categories
          result = self.portal_categories.getCategoryChildTitleItemList(base_category_list, base=1, display_none_category=0)
        return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getVariationBaseCategoryItemList')
    def getVariationBaseCategoryItemList(self):
      """
        Returns a list of base_category tuples for this tranformation
      """
      return self.portal_categories.getItemList(self.getVariationBaseCategoryList())


    security.declareProtected(Permissions.AccessContentsInformation, '_setVariationBaseCategoryList')
    def _setVariationBaseCategoryList(self, value):
      """
        Define the possible base categories
      """
#      XXX TransformedResource works only for a maximum of 3 variation base category...
#      Matrixbox must be rewrite for a clean implementation of n base category
      if len(value) <= 3:
        self._baseSetVariationBaseCategoryList(value)
      else:
        raise MoreThan3VariationBaseCategory

      # create relations between resource variation and transformation
      self._setVariationCategoryList( self.getVariationRangeCategoryList() )

    security.declareProtected(Permissions.AccessContentsInformation, 'setVariationBaseCategoryList')
    def setVariationBaseCategoryList(self, value):
      """
        Define the possible base categories and reindex object
      """
      self._setVariationBaseCategoryList(value)
      self.reindexObject()

    security.declareProtected(Permissions.AccessContentsInformation, 'getVariationCategoryItemList')
    def getVariationCategoryItemList(self, base_category_list = (), base=1, display_id='getTitleOrId', current_category=None):
      """
        Returns the list of possible variations
        XXX Copied and modified from Variated
        Result is left display.
      """
      variation_category_item_list = []

# What is this parameter ?
#    if current_category is not None:
#      variation_category_item_list.append((current_category,current_category))

      if base_category_list == ():
        base_category_list = self.getVariationBaseCategoryList()

      variation_category_list = self.getVariationCategoryList(base_category_list=base_category_list)

      for variation_category in variation_category_list:
        resource = self.portal_categories.resolveCategory(variation_category)

        if resource.getPortalType() == 'Category':
          # XXX  Category is unusable if only Title is displayed...
          value = getattr(resource, 'getLogicalPath')()
        else:
          # And displaying LogicalPath for variation is unusable for user...
          value = getattr(resource, display_id)()

        if base:
          index = variation_category.find('/') 
          base_category = variation_category[:index]
          label = base_category+'/'+value
        else:
          label = value

        # Result is left display
        variation_category_item_list.append((label,  variation_category ))  

      return variation_category_item_list


    security.declareProtected(Permissions.AccessContentsInformation, 'getAggregatedAmountList')
    def getAggregatedAmountList(self, context=None, REQUEST=None, **kw):
      """
        getAggregatedAmountList returns a AggregatedAmountList which can be used
        either to do some calculation (ex. price, BOM) or to display
        a detailed view of a transformation.
      """
      context = self.asContext(context=context, REQUEST=REQUEST, **kw)
      # First we need to get the list of transformations which this transformation depends on
      # XXX At this moment, we only consider 1 dependency
      template_transformation_list = self.getSpecialiseValueList()

      result = AggregatedAmountList()

      # Browse all involved transformations and create one line per line of transformation
      # Currently, we do not consider abstractions, we just add whatever we find in all
      # transformations
      for transformation in [self] + template_transformation_list:
        # Browse each transformed or assorted resource of the current transformation
        for transformation_line in transformation.objectValues():

          result.extend( transformation_line.getAggregatedAmountList(context) )

      return result

# XXX subclassing directly list would be better, but does not work yet (error with class and security)
from UserList import UserList
class AggregatedAmountList(UserList):
  """
    Temporary object needed to aggregate Amount value
    And to calculate some report or total value
  """
  meta_type = "AggregatedAmountList"
  security = ClassSecurityInfo()
#  security.declareObjectPublic()

  security.declarePublic('getTotalBasePrice')
  def getTotalBasePrice(self):
    """
      Return total bas price of the transformation
    """
    result = sum( filter(lambda y: y is not None  ,map( lambda x: x.getTotalBasePrice(), self)) )
    return result

  security.declarePublic('getTotalDuration')
  def getTotalDuration(self):
    """
      Return total duration of the transformation
    """
    result = sum( filter(lambda y: y is not None  ,map( lambda x: x.getDuration(), self) ))
    return result
  
InitializeClass(AggregatedAmountList)
allow_class(AggregatedAmountList)
