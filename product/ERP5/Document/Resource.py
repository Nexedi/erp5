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
from Products.ERP5Type.XMLObject import XMLObject

from Products.ERP5.Variated import Variated
from Products.ERP5.Core.Resource import Resource as CoreResource
from Products.ERP5.ERP5Globals import resource_type_list, variation_type_list, default_section_category, current_inventory_state_list

from zLOG import LOG

class Resource(XMLObject, CoreResource, Variated):
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
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
An Organisation object holds the information about
an organisation (ex. a division in a company, a company,
a service in a public administration)."""
         , 'icon'           : 'organisation_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addResource'
         , 'immediate_view' : 'resource_edit'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'resource_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'resource_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_edit'
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

    # Is it OK now ?
    # The same method is at about 3 different places
    # Some genericity is needed
    security.declareProtected(Permissions.AccessContentsInformation,
                                           'getVariationRangeCategoryItemList')
    def getVariationRangeCategoryItemList(self, base_category_list = (), base=1, root=1,
                                                method_id='getTitle', current_category=None):
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
          other_variations = self.searchFolder(portal_type = variation_type_list)
        except:
          other_variations = []
        if len(other_variations) > 0:
          for o_brain in other_variations:
            o = o_brain.getObject()
            for v in o.getVariationBaseCategoryList():
              if base_category_list is () or v in base_category_list:
                if base:
                  result += [('%s/%s' % (v, o.getRelativeUrl()), '%s/%s' % (v, o.getRelativeUrl()))]
                else:
                  result += [(o.getRelativeUrl(),o.getRelativeUrl())]
        return result

    security.declareProtected(Permissions.AccessContentsInformation,
                                           'getVariationCategoryItemList')
    def getVariationCategoryItemList(self, base_category_list = (),  base=1,
                                        method_id='getTitle',current_category=None):
        """
          Returns possible variations
        """
        result = Variated.getVariationCategoryItemList(self, base_category_list = base_category_list,
                                          method_id=method_id, base = base, current_category=None)
        try:
          other_variations = self.searchFolder(portal_type = variation_type_list)
        except:
          other_variations = []
        if len(other_variations) > 0:
          for o_brain in other_variations:
            o = o_brain.getObject()
            if o is not None:
              for v in o.getVariationBaseCategoryList():
                if base_category_list is () or v in base_category_list:
                  if base:
                    result += [('%s/%s' % (v, o.getRelativeUrl()), '%s/%s' % (v, o.getRelativeUrl()))]
                  else:
                    result += [(o.getRelativeUrl(),o.getRelativeUrl())]
        return result

    # Unit conversion
    security.declareProtected(Permissions.AccessContentsInformation, 'convertQuantity')
    def convertQuantity(self, quantity, from_unit, to_unit):
      return quantity

    # Pricing
    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
    def getTotalPrice(self, quantity, unit=None, variation=None, REQUEST=None):
      return self.convertQuantity(quantity, unit, self.getDefaultQuantityUnit()) *\
                                                                  getBasePrice()

    security.declareProtected(Permissions.AccessContentsInformation, 'getUnitPrice')
    def getUnitPrice(self, unit=None, variation=None, REQUEST=None):
      return self.getTotalPrice(1.0, unit, variation, REQUEST)


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
    def getInventory(self, at_date = None, section = None, node = None,
            node_category=None, section_category=default_section_category, simulation_state=None, variation_text=None,
            ignore_variation=0, **kw):
      if type(simulation_state) is type('a'):
        simulation_state = [simulation_state]
      result = self.Resource_zGetInventory(resource_uid = [self.getUid()],
                                             resource=None,
                                             to_date=at_date,
                                             section=section, node=node,
                                             node_category=node_category,
                                             section_category=section_category,
                                             simulation_state=simulation_state,
                                             variation_text=variation_text
                                             )
      if len(result) > 0:
        return result[0].inventory
      return 0.0

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventory')
    def getFutureInventory(self, section = None, node = None,
             node_category=None, section_category=default_section_category, simulation_state=None,
             ignore_variation=0, **kw):
      """
        Returns inventory at infinite
      """
      return self.getInventory(at_date=None, section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventory')
    def getCurrentInventory(self, section = None, node = None,
             node_category=None, section_category=default_section_category, ignore_variation=0, variation_text=None, **kw):
      """
        Returns current inventory
      """

      # Consider only delivered - forget date at this point
      return self.getInventory(simulation_state = current_inventory_state_list, section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)

      #return self.getInventory(at_date=DateTime(), section=section, node=node,
      #                       node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getAvailableInventory')
    def getAvailableInventory(self, section = None, node = None,
               node_category=None, section_category=default_section_category,
               ignore_variation=0, **kw):
      """
        Returns available inventory, ie. current inventory - deliverable
      """
      return self.getInventory(at_date=DateTime(), section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryList')
    def getInventoryList(self, at_date = None, section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              ignore_variation=0, **kw):
      """
        Returns list of inventory grouped by section or site
      """
      if type(simulation_state) is type('a'):
        simulation_state = [simulation_state]
      result = self.Resource_zGetInventoryList(resource_uid = [self.getUid()],
                                             resource=None,
                                             to_date=at_date,
                                             section=section, node=node,
                                             node_category=node_category,
                                             section_category=section_category,
                                             simulation_state=simulation_state,
                                              **kw)
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryList')
    def getFutureInventoryList(self, section = None, node = None,
             node_category=None, section_category=default_section_category, simulation_state=None,
             ignore_variation=0, **kw):
      """
        Returns list of future inventory grouped by section or site
      """
      return self.getInventoryList(at_date=None, section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryList')
    def getCurrentInventoryList(self, section = None, node = None,
                            node_category=None, section_category=default_section_category,
                            ignore_variation=0, **kw):
      """
        Returns list of current inventory grouped by section or site
      """
      return self.getInventoryList(simulation_state=current_inventory_state_list, section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)
      #return self.getInventoryList(at_date=DateTime(), section=section, node=node,
      #                       node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryStat')
    def getInventoryStat(self, at_date = None, section = None, node = None,
              node_category=None, section_category=default_section_category,
              simulation_state=None, ignore_variation=0, **kw):
      """
        Returns statistics of inventory list grouped by section or site
      """
      if type(simulation_state) is type('a'):
        simulation_state = [simulation_state]
      result = self.Resource_zGetInventory(resource_uid = [self.getUid()],
                                             resource=None,
                                             to_date=at_date,
                                             section=section, node=node,
                                             node_category=node_category,
                                             section_category=section_category,
                                             simulation_state=simulation_state,
                                             **kw)
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryStat')
    def getFutureInventoryStat(self, section = None, node = None,
             node_category=None, section_category=default_section_category, simulation_state=None,
             ignore_variation=0, **kw):
      """
        Returns statistics of future inventory list grouped by section or site
      """
      return self.getInventoryStat(at_date=None, section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryStat')
    def getCurrentInventoryStat(self, section = None, node = None,
                            node_category=None, section_category=default_section_category,
                            ignore_variation=0, **kw):
      """
        Returns statistics of current inventory list grouped by section or site
      """
      return self.getInventoryStat(simulation_state=current_inventory_state_list, section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryChart')
    def getInventoryChart(self, at_date = None, section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              ignore_variation=0, **kw):
      """
        Returns list of inventory grouped by section or site
      """
      if type(simulation_state) is type('a'):
        simulation_state = [simulation_state]
      result = self.Resource_zGetInventoryList(resource_uid = [self.getUid()],
                                             resource=None,
                                             to_date=at_date,
                                             section=section, node=node,
                                             node_category=node_category,
                                             section_category=section_category,
                                             simulation_state=simulation_state,
                                             **kw)
      return map(lambda r: (r.node_title, r.inventory), result)

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryChart')
    def getFutureInventoryChart(self, section = None, node = None,
             node_category=None, section_category=default_section_category, simulation_state=None,
             ignore_variation=0, **kw):
      """
        Returns list of future inventory grouped by section or site
      """
      return self.getInventoryChart(at_date=None, section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryChart')
    def getCurrentInventoryChart(self, section = None, node = None,
                            node_category=None, section_category=default_section_category,
                            ignore_variation=0, **kw):
      """
        Returns list of current inventory grouped by section or site
      """
      return self.getInventoryChart(simulation_state=current_inventory_state_list, section=section, node=node,
                  node_category=node_category, section_category=section_category, **kw)
      #return self.getInventoryChart(at_date=DateTime(), section=section, node=node,
      #            node_category=node_category, section_category=section_category, **kw)


    security.declareProtected(Permissions.AccessContentsInformation, 'getMovementHistoryList')
    def getMovementHistoryList(self, from_date = None, to_date=None, section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              ignore_variation=0, **kw):
      """
        Returns list of inventory grouped by section or site
      """
      result = self.Resource_zGetMovementHistoryList(resource_uid = [self.getUid()],
                                             resource=None,
                                             from_date=from_date,
                                             to_date=to_date,
                                             section=section,
                                             node=node,
                                             node_category=node_category,
                                             section_category=section_category,
                                             simulation_state=simulation_state,
                                             **kw)
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getMovementHistoryStat')
    def getMovementHistoryStat(self, from_date = None, to_date=None, section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              ignore_variation=0, **kw):
      """
        Returns list of inventory grouped by section or site
      """
      result = self.Resource_zGetInventory(resource_uid = [self.getUid()],
                                             resource=None,
                                             from_date=from_date,
                                             to_date=to_date,
                                             section=section,
                                             node=node,
                                             node_category=node_category,
                                             simulation_state=simulation_state,
                                             section_category=section_category, **kw)
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryHistoryList')
    def getInventoryHistoryList(self, from_date = None, to_date=None, section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              ignore_variation=0, **kw):
      """
        Returns list of inventory grouped by section or site
      """
      # Get Movement List
      result = self.Resource_getInventoryHistoryList(  resource_uid = [self.getUid()],
                                             resource=None,
                                             from_date=from_date,
                                             to_date=to_date,
                                             section=section,
                                             node=node,
                                             node_category=node_category,
                                             section_category=section_category,
                                             simulation_state = simulation_state,
                                              **kw)
      return result


    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryHistoryChart')
    def getInventoryHistoryChart(self, from_date = None, to_date=None, section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              ignore_variation=0, **kw):
      """
        Returns list of inventory grouped by section or site
      """
      # Get Movement List
      result = self.Resource_getInventoryHistoryChart(  resource_uid = [self.getUid()],
                                             resource=None,
                                             from_date=from_date,
                                             to_date=to_date,
                                             section=section,
                                             node=node,
                                             node_category=node_category,
                                             section_category=section_category,
                                             simulation_state = simulation_state,
                                              **kw)
      return result


    security.declareProtected(Permissions.AccessContentsInformation, 'getNextNegativeInventoryDate')
    def getNextNegativeInventoryDate(self, from_date = DateTime(), section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              variation_text = None,
              ignore_variation=0, **kw):
      """
        Returns list of inventory grouped by section or site
      """
      # Get Movement List
      result = self.Resource_getInventoryHistoryList(  resource_uid = [self.getUid()],
                                             resource=None,
                                             from_date=from_date,
                                             variation_text = variation_text,
                                             section=section,
                                             node=node,
                                             node_category=node_category,
                                             section_category=section_category,
                                             simulation_state = simulation_state,
                                              **kw)
      for inventory in result:
        if inventory['inventory'] < 0:
          return inventory['stop_date']

      return None


    # Industrial price API
    security.declareProtected(Permissions.AccessContentsInformation, 'getIndustrialPrice')
    def getIndustrialPrice(self, context=None, REQUEST=None, **kw):
      """
        Returns industrial price
      """
      context = self.asContext(context=context, REQUEST=REQUEST, **kw)
      result = self._getIndustrialPrice(context)
      if result is None:
        self._updateIndustrialPrice()
        result = self._getIndustrialPrice(context)
      return result 

    def _getIndustrialPrice(self, context):
      # Default value is None
      return None

    def _updateIndustrialPrice(self, context):
      # Do nothing by default
      pass
