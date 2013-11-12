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
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from ZTUtils import make_query
from Products.CMFCore.utils import getToolByName
from zLOG import LOG, PROBLEM
from Products.ERP5Type.Message import translateString
from ComputedAttribute import ComputedAttribute

class ComputedAttributeGetItemCompatibleMixin(ZSQLBrain):
  """A brain that supports accessing computed attributes using __getitem__
  protocol.
  """
  def __init__(self):
    # __getitem__ returns the computed attribute directly, but if we access
    # brain['node_title'] we expect to have the attribute after computation,
    # not the ComputedAttribute attribue instance. Defining a __getitem__
    # method on that class is not enough, because the brain class is not
    # directly this class but a class created on the fly that also inherits
    # from Record which already defines a __getitem__ method.
    # We cannot patch the instance, because Record does not allow this kind of
    # mutation, but as the class is created on the fly, for each query, it's
    # safe to patch the class. See Shared/DC/ZRDB/Results.py for more detail.
    # A Records holds a list of r instances, only the first __init__ needs to
    # do this patching.
    if not hasattr(self.__class__, '__super__getitem__'):
      self.__class__.__super__getitem__ = self.__class__.__getitem__
      self.__class__.__getitem__ =\
        ComputedAttributeGetItemCompatibleMixin.__getitem__

  # ComputedAttribute compatibility for __getitem__
  def __getitem__(self, name):
    item = self.__super__getitem__(name)
    if isinstance(item, ComputedAttribute):
      return item.__of__(self)
    return item

class InventoryListBrain(ComputedAttributeGetItemCompatibleMixin):
  """
    Lists each variation
  """
  # Stock management
  def getInventory(self, **kw):
    simulation_tool = getToolByName(self, 'portal_simulation')
    return simulation_tool.getInventory(
                   node_uid=self.node_uid,
                   variation_text=self.variation_text,
                   resource_uid=self.resource_uid, **kw)

  def getCurrentInventory(self,**kw):
    simulation_tool = getToolByName(self, 'portal_simulation')
    return simulation_tool.getCurrentInventory(
                             node_uid=self.node_uid,
                             variation_text=self.variation_text,
                             resource_uid=self.resource_uid, **kw)

  def getFutureInventory(self,**kw):
    simulation_tool = getToolByName(self,'portal_simulation')
    return simulation_tool.getFutureInventory(
                              node_uid=self.node_uid,
                              variation_text=self.variation_text,
                              resource_uid=self.resource_uid, **kw)

  def getAvailableInventory(self,**kw):
    simulation_tool = getToolByName(self,'portal_simulation')
    return simulation_tool.getAvailableInventory(
                             node_uid=self.node_uid,
                             variation_text=self.variation_text,
                             resource_uid=self.resource_uid, **kw)

  def getQuantityUnit(self, **kw):
    resource = self.getResourceValue()
    if resource is not None:
      return resource.getQuantityUnit()

  def _getObjectByUid(self, uid):
    uid_cache = getTransactionalVariable().setdefault(
                    'InventoryBrain.uid_cache', {None: None})
    try:
      return uid_cache[uid]
    except KeyError:
      result_list = self.portal_catalog(uid=uid, limit=1,
        select_dict=dict(title=None, relative_url=None))
      result = None
      if result_list:
        result = result_list[0]
      uid_cache[uid] = result
      return result

  def getSectionValue(self):
    return self._getObjectByUid(self.section_uid)

  def getSectionTitle(self):
    section = self.getSectionValue()
    if section is not None:
      return section.title
  section_title = ComputedAttribute(getSectionTitle, 1)

  def getSectionRelativeUrl(self):
    section = self.getSectionValue()
    if section is not None:
      return section.relative_url
  section_relative_url = ComputedAttribute(getSectionRelativeUrl, 1)

  def getNodeValue(self):
    return self._getObjectByUid(self.node_uid)

  def getNodeTitle(self):
    node = self.getNodeValue()
    if node is not None:
      return node.title
  node_title = ComputedAttribute(getNodeTitle, 1)

  def getNodeRelativeUrl(self):
    node = self.getNodeValue()
    if node is not None:
      return node.relative_url
  node_relative_url = ComputedAttribute(getNodeRelativeUrl, 1)

  def getResourceValue(self):
    return self._getObjectByUid(self.resource_uid)

  def getResourceTitle(self):
    resource = self.getResourceValue()
    if resource is not None:
      return resource.title
  resource_title = ComputedAttribute(getResourceTitle, 1)

  def getResourceRelativeUrl(self):
    resource = self.getResourceValue()
    if resource is not None:
      return resource.relative_url
  resource_relative_url = ComputedAttribute(getResourceRelativeUrl, 1)

  def getResourceReference(self):
    resource = self.getResourceValue()
    if resource is not None:
      return resource.getReference()
  resource_reference = ComputedAttribute(getResourceReference, 1)

  def getListItemUrl(self, cname_id, selection_index, selection_name):
    """Returns the URL for column `cname_id`. Used by ListBox
    """
    resource = self.getResourceValue()
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
          return explanation.absolute_url()
      return ''
    elif resource is not None:
      # A resource is defined, so try to display the movement list
      form_id = 'Resource_viewMovementHistory'
      query_kw = {
        'variation_text': self.variation_text,
        'selection_name': selection_name,
        'selection_index': selection_index,
        'domain_name': selection_name,
      }
      # Add parameters to query_kw
      query_kw_update = {}

      if cname_id in ('transformed_resource_title', ):
        return resource.absolute_url()
      elif cname_id in ('getCurrentInventory', ):
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
                                    form_id,
                                    make_query(**query_kw) )

    # default case, if it's a movement, return link to the explanation of this
    # movement.
    document = self.getObject()
    if document.isMovement():
      explanation = document.getExplanationValue()
      if explanation is not None:
        return explanation.absolute_url()
    return ''

  def getExplanationText(self):
    # Returns an explanation of the movement
    o = self.getObject()
    if o is not None:
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
          mapping['causality_portal_type'] = causality.getTranslatedPortalType()
          mapping['causality_title'] = causality.getTitleOrId()
          return translateString(
            "${delivery_portal_type} ${delivery_title} "
            "(${causality_portal_type} ${causality_title})",
            mapping=mapping)
        else :
          return translateString("${delivery_portal_type} ${delivery_title}",
                                 mapping=mapping)
    return translateString('Unknown')

class TrackingListBrain(InventoryListBrain):
  """
  List of aggregated movements
  """
  def getDate(self):
    if not self.date:
      return
    # convert the date in the movement's original timezone.
    # This is a somehow heavy operation, but fortunatly it's only called when
    # the brain is accessed from the Shared.DC.ZRDB.Results.Results instance
    obj = self.getObject()
    if obj is not None:
      portal = obj.getPortalObject()
      movement = portal.portal_catalog.getObject(self.delivery_uid)
      date = movement.getStartDate() or movement.getStopDate()
      if date is not None:
        timezone = date.timezone()
        return self.date.toZone(timezone)
    return self.date


class MovementHistoryListBrain(InventoryListBrain):
  """Brain for getMovementHistoryList
  """
  def __init__(self):
    InventoryListBrain.__init__(self)
    if not self.date:
      return
    # convert the date in the movement's original timezone.
    # This is a somehow heavy operation, but fortunatly it's only called when
    # the brain is accessed from the Shared.DC.ZRDB.Results.Results instance
    obj = self.getObject()
    if obj is not None:
      timezone = None
      if self.node_uid == obj.getSourceUid():
        start_date = obj.getStartDate()
        if start_date is not None:
          timezone = start_date.timezone()
      else:
        stop_date = obj.getStopDate()
        if stop_date is not None:
          timezone = stop_date.timezone()
      if timezone is not None:
        self.date = self.date.toZone(timezone)

  def getListItemUrl(self, cname_id, selection_index, selection_name):
    """Returns the URL for column `cname_id`. Used by ListBox
    Here we just want a link to the explanation of movement.
    """
    document = self.getObject()
    if document.isMovement():
      explanation = document.getExplanationValue()
      if explanation is not None:
        return explanation.absolute_url()
    return ''


  def _debit(self):
    if self.getObject().isCancellationAmount():
      return min(self.total_quantity, 0)
    return max(self.total_quantity, 0)
  debit = ComputedAttribute(_debit, 1)

  def _credit(self):
    if self.getObject().isCancellationAmount():
      return min(-(self.total_quantity or 0), 0)
    return max(-(self.total_quantity or 0), 0)
  credit = ComputedAttribute(_credit, 1)

  def _debit_price(self):
    if self.getObject().isCancellationAmount():
      return min(self.total_price, 0)
    return max(self.total_price, 0)
  debit_price = ComputedAttribute(_debit_price, 1)

  def _credit_price(self):
    if self.getObject().isCancellationAmount():
      return min(-(self.total_price or 0), 0)
    return max(-(self.total_price or 0), 0)
  credit_price = ComputedAttribute(_credit_price, 1)

