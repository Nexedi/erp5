##############################################################################
#
# Copyright (c) 2002 Coramy SAS and Contributors. All Rights Reserved.
#                    Thierry_Faucher <Thierry_Faucher@coramy.com>
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
from Products.ERP5.ERP5Globals import resource_type_list, variation_type_list

from Domain import Domain

from zLOG import LOG

class Transformation(XMLObject, Domain, Variated):
    """
      Build of material - contains a list of transformed resources

      Use of default_resource... (to define the variation range,
      to ...)


      About ranges:

      getDomainBaseCategoryList -> base categories which allow to select state...

      getDomainRangeBaseCategoryList -> base categories which allow to select state...

      getDomainCategoryList -> bonne id?.... = DomainValue...
                               base category which defines the state
                               (and other things)

      getDomainRangeCategoryList -> bonne id?.... = DomainValue...

    """

    meta_type = 'ERP5 Transformation'
    portal_type = 'Transformation'
    add_permission = Permissions.AddERP5Content
    isPortalContent = 1
    isRADContent = 1

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
                      , PropertySheet.Transformation
                      )

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
une gamme..."""
         , 'icon'           : 'transformation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addTransformation'
         , 'immediate_view' : 'transformation_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Transformed Resource',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'transformation_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'list'
          , 'name'          : 'Object Contents'
          , 'category'      : 'object_action'
          , 'action'        : 'folder_contents'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'transformation_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }

    security.declareProtected(Permissions.AccessContentsInformation,
                                          'getVariationRangeBaseCategoryList')
    def getVariationRangeBaseCategoryList(self):
        """
          Returns possible variation base_category ids of the
          default resource of this transformation
        """
        resource = self.getDefaultResourceValue()
        if resource is not None:
          result = resource.getVariationBaseCategoryList()
        else:
          result = self.getBaseCategoryIds()
        return result

    security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransformationVariationRangeCategoryList')
    def getTransformationVariationRangeCategoryList(self):
        """
          Possible categories (ie. of the default resource)
        """
        return self.getResourceValue().getVariationCategoryList(base_category_list=
                              self.getTransformationVariationBaseCategoryList())

    security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransformationVariationCategoryList')
    def getTransformationVariationCategoryList(self):
        """
          Possible categories (ie. of the default resource)
        """
        return self.getVariationCategoryList(base_category_list=
                              self.getTransformationVariationBaseCategoryList())

    security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransformationVariationRangeBaseCategoryList')
    def getTransformationVariationRangeBaseCategoryList(self):
        """
          Returns possible variation base_category ids of the
          default resource which can be used a variation axis
          in the transformation (ie. all ids of
          getVariationRangeBaseCategoryList except ids which
          are used as a transformation state as defined in
          domain_base_category)
        """
        result = ['',] + list(self.getVariationRangeBaseCategoryList())
        forbidden_id = self.getDomainBaseCategoryList()
        forbidden_id = asList(forbidden_id) # This will soon be useless
        return rejectIn(result, forbidden_id)

    security.declareProtected(Permissions.AccessContentsInformation,
                                      'getVariationRangeBaseCategoryItemList')
    def getVariationRangeBaseCategoryItemList(self):
        """
          Returns possible variations of the resource
          as a list of tuples (id, title). This is mostly
          useful in ERP5Form instances to generate selection
          menus.
        """
        return self.portal_categories.getItemList(self.getVariationRangeBaseCategoryList())

    security.declareProtected(Permissions.AccessContentsInformation,
                          'getTransformationVariationRangeBaseCategoryItemList')
    def getTransformationVariationRangeBaseCategoryItemList(self):
        """
          Returns possible variations of the transformation
          as a list of tuples (id, title). This is mostly
          useful in ERP5Form instances to generate selection
          menus.
        """
        return self.portal_categories.getItemList(
                    self.getTransformationVariationRangeBaseCategoryList())

    security.declareProtected(Permissions.AccessContentsInformation,
                                        'getVariationRangeCategoryItemList')
    def getVariationRangeCategoryItemList(self, base_category_list = ()):
        """
          Returns possible variation category values for the
          transformation according to the default resource.
          Possible category values is provided as a list of
          tuples (id, title). This is mostly
          useful in ERP5Form instances to generate selection
          menus.
        """
        if base_category_list is ():
          base_category_list = self.getVariationBaseCategoryList()
        try:
          result = self.getDefaultResourceValue(
                    ).getVariationRangeCategoryItemList(base_category_list)
        except:
          result = self.portal_categories.getCategoryChildItemList(base_category_list,
                                               base=1)
        return result

    # Aliases to simplify access to range information for TransformedResources
    security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransformationVariationBaseCategoryList')
    def getTransformationVariationBaseCategoryList(self):
      """
        Returns a list of base_category ids for this tranformation
      """
      return self.getVariationBaseCategoryList()

    security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransformationVariationBaseCategoryItemList')
    def getTransformationVariationBaseCategoryItemList(self):
      """
        Returns a list of base_category tuples for this tranformation
      """
      return self.portal_categories.getItemList(self.getVariationBaseCategoryList())

    # This is the main method to do any BOM related calculation
    security.declareProtected(Permissions.AccessContentsInformation, 'getAggregatedAmountList')
    def getAggregatedAmountList(self, context=None, REQUEST=None, **kw):
      """
        getAggregatedSummary returns a list of dictionaries which can be used
        either to do some calculation (ex. price, BOM) or to display
        a detailed view of a transformation.

        We must update this API to be able to manage context
      """
      # LOG('getAggregatedAmountList',0,str((context, REQUEST, kw)))
      REQUEST = self.asContext(context=context, REQUEST=REQUEST, **kw)
      # First we need to get the list of transformations which this transformation depends on
      # At this moment, we only consider 1 dependency
      transformation_list = [self] + self.getSpecialiseValueList()
      # We consider that the specific parameters to take into account
      # are acquired through the REQUEST parameter
      # The REQUEST can either be a Zope REQUEST or a dictionnary provided by the use
      if REQUEST is None:
        # At this moment XXXXXXXXXXXXXXXXXXXXXXXX
        # we initialize the request to a default value in order
        # to make sure we have something to test MappedValues on
        REQUEST = {'categories': ('taille/enfant/08 ans','coloris/modele/701C402/2')}
      # We define some initial values
      # result holds a list of dictionaries
      # price holds a list of dictionaries
      summary_list = []
      grand_total_variated_source_base_price = 0.0
      grand_total_source_base_price = 0.0
      grand_total_base_price = 0.0
      grand_total_variated_base_price = 0.0
      grand_total_variated_source_base_price = 0.0
      grand_total_duration = 0.0

      # Browse all involved transformations and create one line per line of transformation
      # Currently, we do not consider abstractions, we just add whatever we find in all
      # transformations
      for transformation in transformation_list:
        # Browse each transformed or assorted resource of the current transformation
        for transformed_resource in transformation.objectValues():
          LOG("for transformed_resource in transformation",0,transformed_resource.getId())
          line_item_list, total_base_price, total_source_base_price, \
            total_variated_base_price, total_variated_source_base_price, duration \
            = transformed_resource.getAggregatedAmountList(REQUEST)
          summary_list += line_item_list
          grand_total_base_price += total_base_price
          grand_total_source_base_price += total_source_base_price
          grand_total_variated_base_price += total_variated_base_price
          grand_total_variated_source_base_price += total_variated_source_base_price
          grand_total_duration += duration

      #LOG("Transformation Agg summary",0,
      #        str(map(lambda o: (o.resource_id, o.quantity_defined_by), summary_list)))

      # Return values as a tuple
      return map(lambda x: x.__dict__, summary_list) , grand_total_base_price, \
         grand_total_source_base_price, grand_total_duration, \
         grand_total_variated_base_price, grand_total_variated_source_base_price

    # UPDATED BY JPS

    # XXX This should not be there, but in Document/TransformedResource.py or something like
    # this, but actually this does not work, we should find why.
    security.declareProtected(Permissions.ModifyPortalContent, '_setVariationBaseCategoryList')
    def _setVariationBaseCategoryList(self, new_base_category_list):
      """
        We override the default behaviour generated by Utils.py in order
        to update all TransformedResource contained in this transformation
      """
      # Get the list of previous base_category that have been removed or kept
      removed_base_category = []
      kept_base_category = []
      for cat in self.getVariationBaseCategoryList():
        if cat in new_base_category_list:
          kept_base_category += [cat]
        else:
          removed_base_category += [cat]

      # Update variation_base_category_list
      self.variation_base_category_list = new_base_category_list

      # Make sure there is no reference to categories
      # of removed_base_category
      # in categories
      if len(removed_base_category) > 0:
        self._setCategoryMembership(removed_base_category, [], base=1)

      # Filter all fields which are based on base_category
      if self.getVariationBaseCategoryLine() not in new_base_category_list:
        self._setVariationBaseCategoryLine(None)
      if self.getVariationBaseCategoryColumn() not in new_base_category_list:
        self._setVariationBaseCategoryColumn(None)
      self._setVariationBaseCategoryTabList(keepIn(self.getVariationBaseCategoryTabList(),
                                                      new_base_category_list))

      # Make sure that all sub-objects use a valid range
      # We simply call range functions on each object to force
      # range update in XMLMatrix
      for o in self.objectValues():
        if hasattr(o,'v_variation_base_category_list'):
          o.setVVariationBaseCategoryList(keepIn(o.getVVariationBaseCategoryList(),
                                                              new_base_category_list))
        if hasattr(o,'q_variation_base_category_list'):
          o.setQVariationBaseCategoryList(keepIn(o.getQVariationBaseCategoryList(),
                                                              new_base_category_list))
