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

from DateTime import DateTime

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLMatrix import XMLMatrix

from Products.ERP5.Variated import Variated
from Products.ERP5.Core.Resource import Resource as CoreResource
from Products.ERP5.Document.SupplyLine import SupplyLineMixin
from Products.CMFCore.WorkflowCore import WorkflowMethod

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
    def getVariationRangeCategoryItemList(self, base_category_list = (), base=1, root=1,
                                                display_id='getTitle', current_category=None):
        """
          Returns possible variations
        """
        if base_category_list is ():
          base_category_list = self.getVariationBaseCategoryList()
        elif type(base_category_list) is type('a'):
          base_category_list = (base_category_list,)
        result = []

        for c in base_category_list:
          c_range = self.getCategoryMembershipList(c, base=base)
          if len(c_range) > 0:
            result += list(map(lambda x: (x,x), c_range))
          else:      
            if root:    
              # XXX - no idea why we should keep this ? JPS     
              result += self.portal_categories.unrestrictedTraverse(c).getBaseItemList(base=base) 
        try:
          other_variations = self.searchFolder(portal_type = self.getPortalVariationTypeList())
        except:
          other_variations = []
        if len(other_variations) > 0:
          for o_brain in other_variations:
            o = o_brain.getObject()
            for v in o.getVariationBaseCategoryList():
              if base_category_list is () or v in base_category_list:

                display_value = getattr(o, display_id)
                if callable( display_value ):
                  display_value = display_value()

                if base:
                  # [ ( display, stored value ) ]
                  result += [('%s/%s' % (v,  display_value ), '%s/%s' % (v, o.getRelativeUrl()))]
                else:
                  result += [('%s' %  display_value , '%s' %  o.getRelativeUrl())]

        return result



    security.declareProtected(Permissions.AccessContentsInformation,
                                           'getVariationRangeCategoryList')
    def getVariationRangeCategoryList(self, base_category_list = (), base=1, root=1,
                                                display_id='getTitle', current_category=None):
        """
          Returns the range of acceptable categories
        """
        # display is on left
        return map(lambda x: x[1], self.getVariationRangeCategoryItemList(base_category_list=base_category_list,
                                   base=base, root=root, display_id=display_id, current_category=current_category))


    security.declareProtected(Permissions.AccessContentsInformation,
                                           'getVariationCategoryItemList')
    def getVariationCategoryItemList(self, base_category_list = (),  base=1,
                                        display_id='getTitle',current_category=None):
        """
          Returns possible variations
        """
        result = Variated.getVariationCategoryItemList(self, base_category_list = base_category_list,
                                          display_id=display_id, base = base, current_category=None)
        try:
          other_variations = self.searchFolder(portal_type = self.getPortalVariationTypeList())
        except:
          other_variations = []
        if len(other_variations) > 0:
          for o_brain in other_variations:
            o = o_brain.getObject()
            if o is not None:
              for v in o.getVariationBaseCategoryList():
                if base_category_list is () or v in base_category_list:

                  if display_id is not None:
                    try:
                      label = getattr(o, display_id, None)
                      if callable(label):
                        label = label()
                    except:
                      LOG('WARNING: getVariationCategoryItemList', 0, 'Unable to call %s on %s' % (display_id, o.getRelativeUrl()))
                      label = o.getRelativeUrl()

                  if base:
                    result += [('%s/%s' % (v, o.getRelativeUrl()), label   )]
                  else:
                    result += [(o.getRelativeUrl(), label )]
        return result

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

    security.declareProtected( Permissions.ModifyPortalContent, 'updateSupplyMatrix' )
    def updateSupplyMatrix(self):
      """
          Define the indices provided
          one list per index (kw)

          Any number of list can be provided
      """
      # Update the cell range automatically
      # This is far from easy and requires some specific wizzardry
      base_id = 'path'
      kwd = {'base_id': base_id}
      new_range = self.SupplyLine_asCellRange() # This is a site dependent script
      # range must not content empty list
      new_range = filter(lambda x: x != [], new_range)
      self._setCellRange(*new_range, **kwd )

      # XXX need to update the cells content....
      # i did not do anything, because where is maybe some method for continuous range (Romain)

      # XXX why creating all cells ? it takes too much time and is not very useful (Romain)
      #     and it is not updated when we create a variation
      #     and Base_edit does not create such cell....
      """
      cell_range_key_list = self.getCellRangeKeyList(base_id = base_id)
      if cell_range_key_list <> [[None, None]] :
        None
        for k in cell_range_key_list:
          #LOG('new cell',0,str(k))
          c = self.newCell(*k, **kwd)
          c.edit( domain_base_category_list = self.getVariationBaseCategoryList(),
                  mapped_value_property_list = ( 'price',),
                  predicate_operator = 'SUPERSET_OF',
                  predicate_category_list = filter(lambda k_item: k_item is not None, k),
                  variation_category_list = filter(lambda k_item: k_item is not None, k),
                  force_update = 1
                ) # Make sure we do not take aquisition into account
      else:
        # If only one cell, delete it
        cell_range_id_list = self.getCellRangeIdList(base_id = base_id)
        for k in cell_range_id_list:
          if self.get(k) is not None:
            self[k].flushActivity(invoke=0)
            self[k].immediateReindexObject() # We are forced to do this is url is changed (not uid)
            self._delObject(k)
      """

      # TO BE DONE XXX
      # reindex cells when price, quantity or source/dest changes

    # For generation of matrix lines
    security.declareProtected( Permissions.ModifyPortalContent, '_setQuantityStepList' )
    def _setQuantityStepList(self, value):

      self._baseSetQuantityStepList(value)
      value = self.getQuantityStepList()
      value.sort()

      for pid in self.contentIds(filter={'portal_type': 'Predicate Group'}):
        self.deleteContent(pid)
      if len(value) > 0:
        value = value

        # initialisation
        i = 0
        p = self.newContent(id = 'quantity_range_%s' % str(i), portal_type = 'Predicate Group')
        p.setCriterionPropertyList(('quantity', ))
        p.setCriterion('quantity', min=None, max=value[i])
        p.setTitle(' quantity < %s' % repr(value[i]))

        for i in range(0, len(value) -1  ):
          p = self.newContent(id = 'quantity_range_%s' % str(i+1), portal_type = 'Predicate Group')
          p.setCriterionPropertyList(('quantity', ))
          p.setCriterion('quantity', min=value[i], max=value[i+1])
          p.setTitle('%s <= quantity < %s' % (repr(value[i]),repr(value[i+1])))

        # end
        i = len(value) - 1
        p = self.newContent(id = 'quantity_range_%s' % str(i+1), portal_type = 'Predicate Group')
        p.setCriterionPropertyList(('quantity', ))
        p.setCriterion('quantity', min=value[i], max=None)
        p.setTitle('%s <= quantity' % repr(value[i]))


      self.updateSupplyMatrix()

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
