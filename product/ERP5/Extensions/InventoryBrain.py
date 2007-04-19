##############################################################################
#
# Copyright (c) 2002 Nexedi SARL. All Rights Reserved.
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
from Products.ZSQLCatalog.zsqlbrain import ZSQLBrain
from DateTime import DateTime
from ZTUtils import make_query
from Products.CMFCore.utils import getToolByName
from zLOG import LOG, PROBLEM

class InventoryBrain(ZSQLBrain):
  """
    Global analysis (all variations and categories)
  """
  # Stock management
  def getInventory(self, at_date=None, ignore_variation=0,
                   simulation_state=None, **kw):
    if isinstance(simulation_state, str):
      simulation_state = [simulation_state]
    result = self.Resource_zGetInventory(
                      resource_uid=[self.resource_uid],
                      to_date=at_date, omit_simulation=0,
                      section_category=self.getPortalDefaultSectionCategory(),
                      simulation_state=simulation_state)
    inventory = None
    if len(result) > 0:
      inventory = result[0].inventory
    if inventory is None:
      return 0.0
    else:
      return inventory

  def getCurrentInventory(self):
    """
      Returns current inventory
    """
    return self.getInventory(
        simulation_state=self.getPortalCurrentInventoryStateList(),
        ignore_variation=1)

  def getFutureInventory(self):
    """
      Returns current inventory
    """
    return self.getInventory(
                   ignore_variation=1,
                   simulation_state= \
                       list(self.getPortalFutureInventoryStateList())+ \
                       list(self.getPortalReservedInventoryStateList())+ \
                       list(self.getPortalCurrentInventoryStateList()))

  def getAvailableInventory(self):
    """
      Returns current inventory
    """
    at_date=DateTime()
    current = self.getCurrentInventory()
    result = self.Resource_zGetInventory( 
                    resource_uid=[self.resource_uid], ignore_variation=1,
                    omit_simulation=1, omit_input=1,
                    section_category=self.getPortalDefaultSectionCategory(),
                    simulation_state= \
                        self.getPortalReservedInventoryStateList())
    reserved_inventory = None
    if len(result) > 0:
      reserved_inventory = result[0].inventory
    if reserved_inventory is None:
      reserved_inventory = 0.0
    return current + reserved_inventory

  def getQuantityUnit(self, **kw):
    try:
      resource = self.portal_categories.unrestrictedTraverse(
                                      self.resource_relative_url)
      return resource.getQuantityUnit()
    except AttributeError:
      return ''

class InventoryListBrain(ZSQLBrain):
  """
    Lists each variation
  """

  # Stock management
  def getInventory(self, **kw):
    """
    Returns the inventory
    """
    simulation_tool = getToolByName(self, 'portal_simulation')
    return simulation_tool.getInventory(
                   node=self.node_relative_url,
                   variation_text=self.variation_text,
                   resource=self.resource_relative_url, **kw)

  def getCurrentInventory(self,**kw):
    """
      Returns current inventory
    """
    simulation_tool = getToolByName(self, 'portal_simulation')
    return simulation_tool.getCurrentInventory(
                             node=self.node_relative_url,
                             variation_text=self.variation_text,
                             resource=self.resource_relative_url, **kw)

  def getFutureInventory(self,**kw):
    """
      Returns current inventory
    """
    simulation_tool = getToolByName(self,'portal_simulation')
    return simulation_tool.getFutureInventory(
                              node=self.node_relative_url,
                              variation_text=self.variation_text,
                              resource=self.resource_relative_url, **kw)

  def getAvailableInventory(self,**kw):
    """
      Returns current inventory
    """
    simulation_tool = getToolByName(self,'portal_simulation')
    return simulation_tool.getAvailableInventory(
                             node=self.node_relative_url,
                             variation_text=self.variation_text,
                             resource=self.resource_relative_url, **kw)

  def getQuantity(self, **kw):
    """
    Return the quantity of the current delivery for a resource
    """
    total_kw = {
      'explanation_uid': self.getExplanationUid(),
      'resource_uid': self.resource_uid,
      'variation_text': self.variation_text,
    }
    total_kw.update(self.portal_catalog.buildSQLQuery(query_table='movement',
                                                      **total_kw))
    result = self.Delivery_zGetTotal(**total_kw)
    inventory = None
    if len(result) > 0:
      inventory = result[0].inventory
    if inventory is None:
      return 0.0
    else:
      return inventory

  def getQuantityUnit(self, **kw):
    try:
      resource = self.portal_categories.unrestrictedTraverse(
                                           self.resource_relative_url)
      return resource.getQuantityUnit()
    except AttributeError:
      return ''

  def getListItemUrl(self, cname_id, selection_index, selection_name):
    """Returns the URL for column `cname_id`. Used by ListBox
    """
    if cname_id in ('getExplanationText', 'getExplanation', ):
      o = self.getObject()
      if o is not None:
        if not getattr(o, 'isDelivery', 0):
          explanation = o.getExplanationValue()
        else:
          # Additional inventory movements are catalogged in stock table
          # with the inventory's uid. Then they are their own explanation.
          explanation = o
        if explanation is not None:
          return '%s/%s/view' % (
                  self.portal_url.getPortalObject().absolute_url(),
                  explanation.getRelativeUrl())
      else:
        return ''
    elif getattr(self, 'resource_relative_url', None) is not None:
      # A resource is defined, so try to display the movement list
      resource = self.portal_categories.unrestrictedTraverse(
                              self.resource_relative_url)
      form_name = 'Resource_viewMovementHistory'
      query_kw = {
        'variation_text': self.variation_text,
        'selection_name': selection_name,
        'selection_index': selection_index,
        'domain_name': selection_name,
      }
      # Add parameters to query_kw
      query_kw_update = {}

      if cname_id in ('getCurrentInventory', ):
        query_kw_update = {
          'simulation_state': 
            list(self.getPortalCurrentInventoryStateList() + \
            self.getPortalTransitInventoryStateList()),
          'omit_transit': 1,
          'transit_simulation_state': list(
                 self.getPortalTransitInventoryStateList())
        }

      elif cname_id in ('getAvailableInventory', ):
        query_kw_update = {
          'simulation_state': list(self.getPortalCurrentInventoryStateList() + \
                            self.getPortalTransitInventoryStateList()),
          'omit_transit': 1,
          'transit_simulation_state': list(self.getPortalTransitInventoryStateList()),
          'reserved_kw': {
            'simulation_state': list(self.getPortalReservedInventoryStateList()),
            'transit_simulation_state': list(self.getPortalTransitInventoryStateList()),
            'omit_input': 1
          }
        }
      elif cname_id in ('getFutureInventory', 'inventory', ):
        query_kw_update = {
          'simulation_state': \
            list(self.getPortalFutureInventoryStateList()) + \
            list(self.getPortalTransitInventoryStateList()) + \
            list(self.getPortalReservedInventoryStateList()) + \
            list(self.getPortalCurrentInventoryStateList())
        }
      elif cname_id in ('getInventoryAtDate', ):
        query_kw_update = {
          'to_date': self.at_date,
          'simulation_state': \
            list(self.getPortalFutureInventoryStateList()) + \
            list(self.getPortalReservedInventoryStateList())
        }
      query_kw.update(query_kw_update)
      return '%s/%s?%s&reset=1' % ( resource.absolute_url(),
                                    form_name,
                                    make_query(**query_kw) )

    # default case, if it's a movement, return link to the explanation of this
    # movement.
    o = self.getObject()
    if getattr(o, 'isMovement', 0):
      explanation = o.getExplanationValue()
      if explanation is not None:
        return '%s/%s/view' % (
                self.portal_url.getPortalObject().absolute_url(),
                explanation.getRelativeUrl())
    return ''

  def getAggregateListText(self):
    aggregate_list = self.Resource_zGetAggregateList(
                                   explanation_uid = self.explanation_uid,
                                   node_uid = self.node_uid,
                                   section_uid = self.section_uid,
                                   variation_text = self.variation_text,
                                   resource_uid = self.resource_uid)
    result = []
    for o in aggregate_list:
      result.append(o.relative_url)
    return '<br>'.join(result)

  def getExplanationText(self):
    # Returns an explanation of the movement
    o = self.getObject()
    if o is not None:
      N_ = lambda msg, **kw: o.Localizer.translate('ui', msg, **kw)
      # Get the delivery/order
      if not getattr(o, 'isDelivery', 0):
        delivery = o.getExplanationValue()
      else:
        # Additional inventory movements are catalogged in stock table
        # with the inventory's uid. Then they are their own explanation.
        delivery = o
      if delivery is not None:
        mapping = {
          'delivery_portal_type' : delivery.getTranslatedPortalType(),
          'delivery_title' : delivery.getTitleOrId()
        }
        causality = delivery.getCausalityValue()
        if causality is not None:
          mapping['causality_portal_type'] = \
                            causality.getTranslatedPortalType()
          mapping['causality_title'] = causality.getTitleOrId()
          return N_("${delivery_portal_type} ${delivery_title} "\
                    "(${causality_portal_type} ${causality_title})",
                    mapping = mapping )
        else :
          return N_("${delivery_portal_type} ${delivery_title}",
                    mapping = mapping )
    return N_('Unknown')

class DeliveryListBrain(InventoryListBrain):
  """
    Lists each variation
  """

  # Stock management
  def getInventory(self, at_date=None, ignore_variation=0, 
                   simulation_state=None, **kw):
    if isinstance(simulation_state, str):
      simulation_state = [simulation_state]
    where_expression = getattr(self, 'where_expression', None)
    result = self.Resource_zGetInventory(
                    resource_uid = [self.resource_uid],
                    to_date=at_date,
                    section_category = self.getPortalDefaultSectionCategory(),
                    variation_text = self.variation_text,
                    simulation_state = simulation_state,
                    where_expression = where_expression)
    inventory = None
    if len(result) > 0:
      inventory = result[0].inventory
    if inventory is None:
      return 0.0
    else:
      return inventory

  def getAvailableInventory(self):
    """
      Returns current inventory at current date
    """
    at_date = DateTime()
    current = self.getCurrentInventory()
    result = self.Resource_zGetInventory(
                resource_uid = [self.resource_uid],
                omit_simulation = 1, omit_input = 1,
                section_category = self.getPortalDefaultSectionCategory(),
                variation_text = self.variation_text,
                simulation_state = self.getPortalReservedInventoryStateList())
    reserved_inventory = None
    if len(result) > 0:
      reserved_inventory = result[0].inventory
    if reserved_inventory is None:
      reserved_inventory = 0.0
    return current + reserved_inventory

  def getInventoryAtDate(self):
    """
      Returns inventory at the date provided by the SQL method
    """
    at_date=self.at_date
    return self.getInventory(
            at_date=at_date, ignore_variation=0, 
            simulation_state= \
                      list(self.getPortalFutureInventoryStateList()) + \
                      list(self.getPortalReservedInventoryStateList()) + \
                      list(self.getPortalCurrentInventoryStateList()))
