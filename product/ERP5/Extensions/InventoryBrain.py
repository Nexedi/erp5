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
from zLOG import LOG

class InventoryBrain(ZSQLBrain):
  """
    Global analysis (all variations and categories)
  """
  # Stock management
  def getInventory(self, at_date = None, ignore_variation=0, 
                   simulation_state=None, **kw):
    if type(simulation_state) is type('a'):
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
    simulation_tool = getToolByName(self,'portal_simulation')
    return simulation_tool.getInventory(
                   node=self.node_relative_url,
                   variation_text=self.variation_text,
                   resource=self.resource_relative_url, **kw)

  def getCurrentInventory(self,**kw):
    """
      Returns current inventory
    """
    simulation_tool = getToolByName(self,'portal_simulation')
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
      'explanation_uid': self.getDeliveryUid(),
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
    # XXX FIXME can catch to many exceptions
    try:
      if cname_id in ('getExplanationText','getExplanation', ):
        o = self.getObject()
        if o is not None:
          explanation = o.getExplanationValue()
          if explanation is not None:
            return '%s/%s' % (self.portal_url.getPortalObject().absolute_url(),
                              explanation.getRelativeUrl())
        else:
          return ''
        # XXX Coramy, to be deleted
#       elif cname_id in ('getAggregateList','getAggregateListText',):
#         kw = {
#            'list_method_id' : 'Resource_zGetAggregateList',
#            'explanation_uid' : self.explanation_uid,
#            'node_uid' : self.node_uid,
#            'section_uid' : self.section_uid,
#            'variation_text' : self.variation_text,
#            'resource_uid' : self.resource_uid,
#            'reset': 1
#         }
#         url_params_string = make_query(kw)
#         # should be search XXX
#         return '%s/piece_tissu?%s ' % (
#             self.portal_url.getPortalObject().absolute_url(),
#             url_params_string
#             )
      elif (self.resource_relative_url is not None):
        # A resource is defined, so try to display the movement list
        resource = self.portal_categories.unrestrictedTraverse(
                                self.resource_relative_url)
        form_name = 'Resource_viewMovementHistory'
        query_kw = {
          'variation_text': self.variation_text, 
          'selection_name': selection_name,
          'selection_index': selection_index,
        }
        # Add parameters to query_kw
        query_kw_update = {}
        if cname_id in ('getCurrentInventory', ):
          query_kw_update = {
            'simulation_state': list(self.getPortalCurrentInventoryStateList())
          }
        elif cname_id in ('getAvailableInventory', ):
          query_kw_update = {
            'omit_simulation': 1, 
            'omit_input': 1,
            'simulation_state': \
              list(self.getPortalReservedInventoryStateList())
          }
        elif cname_id in ('getFutureInventory', 'inventory', ):
          query_kw_update = {
            'simulation_state': \
              list(self.getPortalFutureInventoryStateList()) + \
              list(self.getPortalReservedInventoryStateList())
          }
        elif cname_id in ('getInventoryAtDate', ):
          query_kw_update = {
            'to_date': self.at_date,
            'simulation_state': \
              list(self.getPortalFutureInventoryStateList()) + \
              list(self.getPortalReservedInventoryStateList())
          }
        query_kw.update(query_kw_update)
        # Return result
        return '%s/%s?%s&reset=1' % (
          resource.absolute_url(),
          form_name,
          make_query(**query_kw))
    except (AttributeError, KeyError):
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
    explanation_text = 'Unknow'
    if o is not None:
      # Get the delivery/order
      delivery = o.getExplanationValue()
      if delivery is not None:
        explanation_text = "%s %s" % (delivery.getPortalType(),
                                      delivery.getTitleOrId())
        causality = delivery.getCausalityValue()
        if causality is not None:
          explanation_text = "%s (%s %s)" % (explanation_text,
                                             causality.getPortalType(),
                                             causality.getTitleOrId())
    return explanation_text

class DeliveryListBrain(InventoryListBrain):
  """
    Lists each variation
  """

  # Stock management
  def getInventory(self, at_date=None, ignore_variation=0, 
                   simulation_state=None, **kw):
    if type(simulation_state) is type('a'):
      simulation_state = [simulation_state]
    if hasattr(self, 'where_expression'):
      where_expression = self.where_expression
    else:
      where_expression = None
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
    at_date=DateTime()
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
    LOG("At Date",0,str(at_date))
    return self.getInventory(
            at_date=at_date, ignore_variation=0, 
            simulation_state= \
                      list(self.getPortalFutureInventoryStateList()) + \
                      list(self.getPortalReservedInventoryStateList()) + \
                      list(self.getPortalCurrentInventoryStateList()))
