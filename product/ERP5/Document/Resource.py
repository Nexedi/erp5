##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from AccessControl import ClassSecurityInfo

from DateTime import DateTime

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLMatrix import XMLMatrix

from Products.ERP5.Variated import Variated
from Products.ERP5.Core.Resource import Resource as CoreResource
from Products.ERP5.Document.SupplyLine import SupplyLineMixin
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.CMFCategory.Renderer import Renderer

from zLOG import LOG

class Resource(XMLMatrix, CoreResource, Variated):
    """
      A Resource
    """

    meta_type = 'ERP5 Resource'
    portal_type = 'Resource'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Price
                      , PropertySheet.Resource
                      , PropertySheet.Reference
                      , PropertySheet.FlowCapacity
                      , PropertySheet.VariationRange
                      )

    # Is it OK now ?
    # The same method is at about 3 different places
    # Some genericity is needed
    security.declareProtected(Permissions.AccessContentsInformation,
                                           'getVariationRangeCategoryItemList')
    def getVariationRangeCategoryItemList(self, base_category_list=(), base=1, 
                                          root=1, display_id='title', 
                                          display_base_category=1,
                                          current_category=None):
        """
          Returns possible variations

          resource.getVariationRangeCategoryItemList
            => [(display, value)]
        """
        result = []
        if base_category_list is ():
          base_category_list = self.getVariationBaseCategoryList()
        elif type(base_category_list) is type('a'):
          base_category_list = (base_category_list,)

        other_base_category_dict = dict([(i,1) for i in base_category_list])
        try:
          other_variations = self.searchFolder( \
                               portal_type=self.getPortalVariationTypeList())
        except:
          other_variations = []

        other_variations = map(lambda x: x.getObject(), other_variations)
        other_variations = filter(lambda x: x is not None, other_variations)

        for object in other_variations:
          for base_category in object.getVariationBaseCategoryList():
            if (base_category_list is ()) or \
               (base_category in base_category_list):
              other_base_category_dict[base_category] = 0
              # XXX now, call Renderer a lot of time.
              # Better implementation needed
              result.extend(Renderer(
                                   base_category=base_category, 
                                   display_base_category=display_base_category,
                                   display_none_category=0, base=base,
                                   current_category=current_category,
                                   display_id=display_id).\
                                                     render([object]))

        other_base_category_item_list = filter(lambda x: x[1]==1, 
            other_base_category_dict.items())
        other_base_category_list = map(lambda x: x[0],
            other_base_category_item_list)
        for c in other_base_category_list:
            result += self.portal_categories.unrestrictedTraverse(c).getBaseItemList(base=base) 

        return result

    security.declareProtected(Permissions.AccessContentsInformation,
                                           'getVariationRangeCategoryList')
    def getVariationRangeCategoryList(self, base_category_list=(), base=1,
                                      root=1, current_category=None):
      """
        Returns the range of acceptable categories
        
      ## Variation API (exemple) ##
        Base categories defined:
          - colour
          - morphology
          - size
        Categories defined:
          - colour/blue
          - colour/red
          - size/Man
          - size/Woman
        Resource 'resource' created with variation_base_category_list:
            (colour, morphology, size)

        resource.getVariationRangeCategoryList
        variation   | individual variation | result
        ____________________________________________________________________________________
                    |                      | (colour/blue, colour/red, size/Man, size/Woman)
        size/Man    |                      | (colour/blue, colour/red, size/Man, size/Woman)
        colour/blue |                      | (colour/blue, colour/red, size/Man, size/Woman)
                    |  colour/1            | (colour/1, size/Man, size/Woman)
                    |  morphology/2        | (colour/blue, colour/red, size/Man, size/Woman, morphology/2)
      """
      vrcil = self.getVariationRangeCategoryItemList(
                                 base_category_list=base_category_list,
                                 base=base, root=root, 
                                 current_category=current_category)
      # display is on left
      return map(lambda x: x[1], vrcil)


    security.declareProtected(Permissions.AccessContentsInformation,
                                           'getVariationCategoryItemList')
    def getVariationCategoryItemList(self, base_category_list=(), 
                                     omit_individual_variation=1, base=1,
                                     current_category=None,
                                     display_base_category=1,
                                     display_id='title', **kw):
      """
        Returns variations of the resource.
        If omit_individual_variation==1, does not return individual 
        variation.
        Else, returns them.
        Display is on left.
            => [(display, value)]

        *old parameters: base=1, current_category=None, 
                         display_id='getTitle' (default value getTitleOrId)
      """
      result = Variated.getVariationCategoryItemList(self, 
                            base_category_list=base_category_list, 
                            display_base_category=display_base_category, **kw)
      if not omit_individual_variation:
        try:
          # XXX Why catching exception here ?
          # Can searchFolder crach ? Or just getPortalVariationTypeList ?
          other_variations = self.searchFolder(
                                portal_type=self.getPortalVariationTypeList())
        except:
          other_variations = []

        other_variations = map(lambda x: x.getObject(), other_variations)
        other_variations = filter(lambda x: x is not None, other_variations)

        for object in other_variations:
          for base_category in object.getVariationBaseCategoryList():
            if (base_category_list is ()) or \
               (base_category in base_category_list):
              # XXX append object, relative_url ?
              # XXX now, call Renderer a lot of time.
              # Better implementation needed
              result.extend(Renderer(
                                   base_category=base_category, 
                                   display_base_category=display_base_category,
                                   display_none_category=0, base=base,
                                   current_category=current_category,
                                   display_id=display_id, **kw).\
                                                     render([object]))
      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getVariationCategoryItemList')
    def getVariationCategoryList(self, base_category_list=(),
                                 omit_individual_variation=1):
      """
        Returns variations of the resource.
        If omit_individual_variation==1, does not return individual 
        variation.
        Else, returns them.

        ## Variation API (exemple) ##
        Base categories defined:
          - colour
          - morphology
          - size
        Categories defined:
          - colour/blue
          - colour/red
          - size/Man
          - size/Woman
        Resource 'resource' created with variation_base_category_list:
            (colour, morphology, size)

        resource.getVariationCategoryList
        variation   | individual variation | result
        _____________________________________________________
                    |                      | ()
        size/Man    |                      | (size/Man, )
        colour/blue |                      | (colour/blue, )
                    |  colour/1            | (colour/1, )
                    |  morphology/2        | (morphology/2, )
      """
      vcil = self.getVariationCategoryItemList(
                          base_category_list=base_category_list,
                          omit_individual_variation=omit_individual_variation)
      return map(lambda x: x[1], vcil)

    # Unit conversion
    security.declareProtected(Permissions.AccessContentsInformation, 'convertQuantity')
    def convertQuantity(self, quantity, from_unit, to_unit):
      return quantity

# This patch is temporary and allows to circumvent name conflict in ZSQLCatalog process for Coramy
    security.declareProtected(Permissions.AccessContentsInformation,
                                              'getDefaultDestinationAmountBis')
    def getDefaultDestinationAmountBis(self, unit=None, variation=None, REQUEST=None):
      try:
        return self.getDestinationReference()
      except:
        return None

# This patch is temporary and allows to circumvent name conflict in ZSQLCatalog process for Coramy
    security.declareProtected(Permissions.AccessContentsInformation,
                                              'getDefaultSourceAmountBis')
    def getDefaultSourceAmountBis(self, unit=None, variation=None, REQUEST=None):
      try:
        return self.getSourceReference()
      except:
        return None


    # This patch allows variations to find a resource
    security.declareProtected(Permissions.AccessContentsInformation,
                                              'getDefaultResourceValue')
    def getDefaultResourceValue(self):
      return self


    # Stock Management
    security.declareProtected(Permissions.AccessContentsInformation, 'getInventory')
    def getInventory(self, **kw):
      """
      Returns inventory
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventory')
    def getCurrentInventory(self, **kw):
      """
      Returns current inventory
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getCurrentInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getAvailableInventory')
    def getAvailableInventory(self, **kw):
      """
      Returns available inventory
      (current inventory - deliverable)
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getAvailableInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventory')
    def getFutureInventory(self, **kw):
      """
      Returns inventory at infinite
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getFutureInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryList')
    def getInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryList')
    def getCurrentInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getCurrentInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryList')
    def getFutureInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getFutureInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryStat')
    def getInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryStat')
    def getCurrentInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getCurrentInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryStat')
    def getFutureInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getFutureInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryChart')
    def getInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryChart')
    def getCurrentInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getCurrentInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryChart')
    def getFutureInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getFutureInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryHistoryList')
    def getInventoryHistoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getInventoryHistoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryHistoryChart')
    def getInventoryHistoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getInventoryHistoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getMovementHistoryList')
    def getMovementHistoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getMovementHistoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getMovementHistoryStat')
    def getMovementHistoryStat(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getMovementHistoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getNextNegativeInventoryDate')
    def getNextNegativeInventoryDate(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getNextNegativeInventoryDate(**kw)


    # Asset Price API
    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryAssetPrice')
    def getInventoryAssetPrice(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryAssetPrice')
    def getCurrentInventoryAssetPrice(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getCurrentInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getAvailableInventoryAssetPrice')
    def getAvailableInventoryAssetPrice(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getAvailableInventoryAssetPrice(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryAssetPrice')
    def getFutureInventoryAssetPrice(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self.getRelativeUrl()
      return self.portal_simulation.getFutureInventoryAssetPrice(**kw)


    # Industrial price API
    security.declareProtected(Permissions.AccessContentsInformation, 'getIndustrialPrice')
    def getIndustrialPrice(self, context=None, REQUEST=None, **kw):
      """
        Returns industrial price
      """
      context = self.asContext(context=context, REQUEST=REQUEST, **kw)
      result = self._getIndustrialPrice(context)
      if result is None:
        self._updateIndustrialPrice(context)
        result = self._getIndustrialPrice(context)
      return result

    def _getIndustrialPrice(self, context):
      # Default value is None
      return None

    def _updateIndustrialPrice(self, context):
      # Do nothing by default
      pass

    security.declareProtected( Permissions.ModifyPortalContent, 'validate' )
    def validate(self):
      """
      """
      pass

    validate = WorkflowMethod( validate )

    security.declareProtected( Permissions.ModifyPortalContent, 'invalidate' )
    def invalidate(self):
      """
      """
      pass

    invalidate = WorkflowMethod( invalidate )

    # Predicate handling
    security.declareProtected(Permissions.AccessContentsInformation, 'asPredicate')
    def asPredicate(self):
      """
      Returns a temporary Predicate based on the Resource properties
      """
      from Products.ERP5 import newTempPredicateGroup as newTempPredicate
      p = newTempPredicate(self.getId(), uid = self.getUid())
      p.setMembershipCriterionBaseCategoryList(('resource',))
      p.setMembershipCriterionCategoryList(('resource/%s' % self.getRelativeUrl(),))
      return p

#monkeyPatch(SupplyLineMixin)
from types import FunctionType
for id, m in SupplyLineMixin.__dict__.items():
    if type(m) is FunctionType:
        setattr(Resource, id, m)
