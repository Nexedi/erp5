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

from Products.ERP5.ERP5Globals import default_section_category, current_inventory_state_list, reserved_inventory_state_list
from Products.ZSQLCatalog.zsqlbrain import ZSQLBrain
from DateTime import DateTime
from ZTUtils import make_query

from zLOG import LOG

class InventoryBrain(ZSQLBrain):
  """
    Global analysis (all variations and categories)
  """

  # Stock management
  def getInventory(self, at_date = None, ignore_variation=0, simulation_state=None, **kw):
    if type(simulation_state) is type('a'):
      simulation_state = [simulation_state]
    result = self.Resource_zGetInventory( resource_uid = [self.resource_uid],
                                          to_date=at_date, omit_simulation = 0,
                                          section_category = default_section_category,
                                          simulation_state=simulation_state)
    inventory = None
    if len(result) > 0:
      inventory = result[0].inventory
    if inventory is None:
      return 0.0
    else:
      return inventory

  #getCurrentInventory = 10.0
  def getCurrentInventory(self):
    """
      Returns current inventory
    """
    return self.getInventory(simulation_state=current_inventory_state_list, ignore_variation=1)
    #return self.getInventory(at_date=DateTime(), ignore_variation=1)

  def getFutureInventory(self):
    """
      Returns current inventory
    """
    return self.getInventory(ignore_variation=1)

  def getAvailableInventory(self):
    """
      Returns current inventory
    """
    at_date=DateTime()
    current = self.getCurrentInventory()
    result = self.Resource_zGetInventory( resource_uid = [self.resource_uid], ignore_variation=1,
                                          from_date=at_date, omit_simulation = 1, omit_input = 1,
                                          section_category = default_section_category,
                                          simulation_state = None)
    reserved_inventory = None
    if len(result) > 0:
      reserved_inventory = result[0].inventory
    if reserved_inventory is None:
      reserved_inventory = 0.0
    result = self.Resource_zGetInventory( resource_uid = [self.resource_uid], ignore_variation=1,
                                          to_date=at_date, omit_simulation = 1, omit_input = 1,
                                          section_category = default_section_category,
                                          simulation_state = ('confirmed', 'getting_ready', 'ready'))
    past_reserved_inventory = None
    if len(result) > 0:
      past_reserved_inventory = result[0].inventory
    if past_reserved_inventory is None:
      past_reserved_inventory = 0.0
    return current + reserved_inventory + past_reserved_inventory

  def getQuantityUnit(self, **kw):
    try:
      resource = self.portal_categories.unrestrictedTraverse(self.resource_relative_url)
      return resource.getQuantityUnit()
    except:
      return ''


class InventoryListBrain(ZSQLBrain):
  """
    Lists each variation
  """

  # Stock management
  def getInventory(self, at_date = None, ignore_variation=0, simulation_state=None, **kw):
    if type(simulation_state) is type('a'):
      simulation_state = [simulation_state]
    result = self.Resource_zGetInventory( resource_uid = [self.resource_uid],
                                          to_date=at_date,
                                          section=self.section_relative_url,
                                          node=self.node_relative_url,
                                          variation_text = self.variation_text,
                                          simulation_state=simulation_state)
    inventory = None
    if len(result) > 0:
      inventory = result[0].inventory
    if inventory is None:
      return 0.0
    else:
      return inventory

  #getCurrentInventory = 10.0
  def getCurrentInventory(self):
    """
      Returns current inventory
    """
    return self.getInventory(simulation_state=current_inventory_state_list, ignore_variation=0)
    #return self.getInventory(at_date=DateTime(), ignore_variation=0)

  def getFutureInventory(self):
    """
      Returns current inventory
    """
    return self.getInventory(ignore_variation=0)

  def getAvailableInventory(self):
    """
      Returns current inventory
    """
    at_date=DateTime()
    current = self.getCurrentInventory()
    result = self.Resource_zGetInventory( resource_uid = [self.resource_uid],
                                          from_date=at_date, omit_simulation = 1, omit_input = 1,
                                          section=self.section_relative_url,
                                          node=self.node_relative_url,
                                          variation_text = self.variation_text,
                                          simulation_state = None)
    reserved_inventory = None
    if len(result) > 0:
      reserved_inventory = result[0].inventory
    if reserved_inventory is None:
      reserved_inventory = 0.0
    result = self.Resource_zGetInventory( resource_uid = [self.resource_uid],
                                          to_date=at_date, omit_simulation = 1, omit_input = 1,
                                          section=self.section_relative_url,
                                          node=self.node_relative_url,
                                          variation_text = self.variation_text,
                                          simulation_state = ('confirmed', 'getting_ready', 'ready'))
    past_reserved_inventory = None
    if len(result) > 0:
      past_reserved_inventory = result[0].inventory
    if past_reserved_inventory is None:
      past_reserved_inventory = 0.0
    return current + reserved_inventory + past_reserved_inventory

  def getQuantity(self, **kw):
    result = self.Delivery_zGetTotal( resource_uid = [self.resource_uid],
                                      variation_text = self.variation_text)
    inventory = None
    if len(result) > 0:
      inventory = result[0].inventory
    if inventory is None:
      return 0.0
    else:
      return inventory

  def getQuantityUnit(self, **kw):
    try:
      resource = self.portal_categories.unrestrictedTraverse(self.resource_relative_url)
      return resource.getQuantityUnit()
    except:
      return ''

  def getListItemUrl(self, cname_id, selection_index, selection_name):
    try:
      if cname_id in ('getExplanationText','getExplanation', ):
        o = self.getObject()
        if o is not None:
          explanation = o.getExplanationValue()
          if explanation is not None:
            return '%s/%s' % (self.portal_url.getPortalObject().absolute_url(), explanation.getRelativeUrl())
        else:
          return ''
      elif cname_id in ('getAggregateList','getAggregateListText',):
        kw = {
               'list_method_id' : 'Resource_zGetAggregateList',
               'explanation_uid' : self.explanation_uid,
               'node_uid' : self.node_uid,
               'section_uid' : self.section_uid,
               'variation_text' : self.variation_text,
               'resource_uid' : self.resource_uid,
               'reset': 1
             }
        url_params_string = make_query(kw)
        # should be search XXX
        return '%s/piece_tissu?%s ' % (
                        self.portal_url.getPortalObject().absolute_url(),
                        url_params_string
                        )
      elif cname_id in ('getCurrentInventory',):
        resource = self.portal_categories.unrestrictedTraverse(self.resource_relative_url)
        return '%s/Resource_movementHistoryView?%s' % (resource.absolute_url(),
          make_query(variation_text=self.variation_text, selection_name=selection_name, selection_index=selection_index,
                     simulation_state=list(current_inventory_state_list)))
      else:
        resource = self.portal_categories.unrestrictedTraverse(self.resource_relative_url)
        return '%s/Resource_movementHistoryView?%s' % (resource.absolute_url(),
          make_query(variation_text=self.variation_text, selection_name=selection_name, selection_index=selection_index))
    except:
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
      portal_type = o.getPortalType()
      if portal_type == "Simulation Movement":
        order = o.getExplanationValue()
        if order is not None:
          return "Simulated Order %s" % (order.getId())
      else:
        LOG("Delivery Value",0,str(self.path))
        delivery = o.getExplanationValue()
        LOG("Delivery Value",0,str(delivery))
        if delivery is not None:
          return "%s %s" % (delivery.getPortalType(), delivery.getId())
    return "Unknown"

class DeliveryListBrain(InventoryListBrain):
  """
    Lists each variation
  """

  # Stock management
  def getInventory(self, at_date = None, ignore_variation=0, simulation_state=None, **kw):
    if type(simulation_state) is type('a'):
      simulation_state = [simulation_state]
    if hasattr(self, 'query'):
      query = self.query
    else:
      query = None
    result = self.Resource_zGetInventory( resource_uid = [self.resource_uid],
                                          to_date=at_date,
                                          section_category = default_section_category,
                                          variation_text = self.variation_text,
                                          simulation_state = simulation_state,
                                          query = query)
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
    result = self.Resource_zGetInventory( resource_uid = [self.resource_uid],
                                          from_date=at_date, omit_simulation = 1, omit_input = 1,
                                          section_category = default_section_category,
                                          variation_text = self.variation_text,
                                          simulation_state = None)
    reserved_inventory = None
    if len(result) > 0:
      reserved_inventory = result[0].inventory
    if reserved_inventory is None:
      reserved_inventory = 0.0
    result = self.Resource_zGetInventory( resource_uid = [self.resource_uid],
                                          to_date=at_date, omit_simulation = 1, omit_input = 1,
                                          section_category = default_section_category,
                                          variation_text = self.variation_text,
                                          simulation_state = ('confirmed', 'getting_ready', 'ready'))
    past_reserved_inventory = None 
    if len(result) > 0:
      past_reserved_inventory = result[0].inventory
    if past_reserved_inventory is None:
      past_reserved_inventory = 0.0
    return current + reserved_inventory + past_reserved_inventory

  def getAvailableInventoryAtDate(self):
    """
      Returns available inventory at the date provided by the SQL method
    """
    at_date=self.at_date
    current = self.getCurrentInventory()
    result = self.Resource_zGetInventory( resource_uid = [self.resource_uid],
                                          from_date=at_date, omit_simulation = 1, omit_input = 1,
                                          section_category = default_section_category,
                                          variation_text = self.variation_text,
                                          simulation_state = None)
    reserved_inventory = None
    if len(result) > 0:
      reserved_inventory = result[0].inventory
    if reserved_inventory is None:
      reserved_inventory = 0.0
    return current + reserved_inventory

