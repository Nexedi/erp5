##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
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

from UserDict import UserDict

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Inventory import Inventory
from Products.ERP5.Document.AccountingTransaction import AccountingTransaction


class InventoryKey(UserDict):
  """Class to use as a key when defining inventory dicts.
  """
  def __init__(self, **kw):
    self.data = {}
    self.data.update(kw)

  def clear(self):
    raise TypeError, 'InventoryKey are immutable'
  
  def pop(self, keys, *args):
    raise TypeError, 'InventoryKey are immutable'
  
  def update(self, dict=None, **kwargs):
    raise TypeError, 'InventoryKey are immutable'
  
  def __delitem__(self, key):
    raise TypeError, 'InventoryKey are immutable'
  
  def __setitem__(self, key, item):
    raise TypeError, 'InventoryKey are immutable'
  
  def setdefault(self, key, failobj=None):
    if key in self.data:
      return self.data[key]
    raise TypeError, 'InventoryKey are immutable'

  def __hash__(self):
    return hash(tuple(self.items()))

  def __cmp__(self, other):
    # this is basically here so that we can see if two inventory keys are
    # equals.
    if tuple(self.keys()) != tuple(other.keys()):
      return -1
    for k, v in self.items():
      if v != other[k]:
        return -1
    return 0



class BalanceTransaction(AccountingTransaction, Inventory):
  """Balance Transaction 
  """

  # CMF Type Definition
  meta_type = 'ERP5 Balance Transaction'
  portal_type = 'Balance Transaction'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isDelivery = 1
    
  #zope.interface.implements( interfaces.Inventory, )

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Delivery
                    , PropertySheet.Amount
                    , PropertySheet.Reference
                    , PropertySheet.PaymentCondition
                    , PropertySheet.AccountingTransaction
                    )
  

  def _getGroupByNodeMovementList(self):
    """Returns movements that implies only grouping by node."""
    movement_list = []
    for movement in self.getMovementList(
              portal_type=self.getPortalAccountingMovementTypeList()):
      if getattr(movement, 'isAccountable', 1):
        if not (movement.getSourceSection() or
                movement.getDestinationPayment()):
          movement_list.append(movement)
    return movement_list

  def _getGroupByPaymentMovementList(self):
    """Returns movements that implies grouping by node and payment"""
    movement_list = []
    for movement in self.getMovementList(
              portal_type=self.getPortalAccountingMovementTypeList()):
      if getattr(movement, 'isAccountable', 1):
        if movement.getDestinationPayment():
          movement_list.append(movement)
    return movement_list

  def _getGroupByMirrorSectionMovementList(self):
    """Returns movements that implies only grouping by node and mirror section"""
    movement_list = []
    for movement in self.getMovementList(
              portal_type=self.getPortalAccountingMovementTypeList()):
      if getattr(movement, 'isAccountable', 1):
        if movement.getSourceSection():
          movement_list.append(movement)
    return movement_list


  def _getCurrentStockDict(self):
    """Looks the current stock by calling getInventoryList, and building a
    dictionnary of InventoryKey
    """
    current_stock = dict()
    getInventoryList = self.getPortalObject()\
                            .portal_simulation.getInventoryList
    section_uid = self.getDestinationSectionUid()
    precision = 2
    if section_uid is not None:
      precision =  self.getDestinationSectionValue()\
                        .getPriceCurrencyValue().getQuantityPrecision()
    default_inventory_params = dict(
                        to_date=self.getStartDate().earliestTime(),
                        section_uid=section_uid,
                        precision=precision,
                        portal_type=self.getPortalAccountingMovementTypeList(),
                        simulation_state=('delivered', ))

    # node
    for movement in self._getGroupByNodeMovementList():
      node_uid = movement.getDestinationUid()
      if not node_uid:
        raise ValueError, "No destination uid for %s" % movement
      resource_uid = movement.getResourceUid()

      stock_list = current_stock.setdefault(
                         InventoryKey(node_uid=node_uid,
                                      section_uid=section_uid), [])
      for inventory in getInventoryList(
                              node_uid=node_uid,
                              resource_uid=resource_uid,
                              group_by_node=1,
                              group_by_resource=1,
                              **default_inventory_params):
        if inventory.total_price and inventory.total_quantity:
          stock_list.append(
              dict(destination_uid=node_uid,
                   destination_section_uid=section_uid,
                   resource_uid=resource_uid,
                   quantity=inventory.total_quantity,
                   total_price=inventory.total_price, ))
    
    # mirror section
    for movement in self._getGroupByMirrorSectionMovementList():
      node_uid = movement.getDestinationUid()
      if not node_uid:
        raise ValueError, "No destination uid for %s" % movement
      mirror_section_uid = movement.getSourceSectionUid()
      resource_uid = movement.getResourceUid()

      stock_list = current_stock.setdefault(
                         InventoryKey(node_uid=node_uid,
                                      mirror_section_uid=mirror_section_uid,
                                      section_uid=section_uid), [])
      for inventory in getInventoryList(
                              node_uid=node_uid,
                              mirror_section_uid=mirror_section_uid,
                              resource_uid=resource_uid,
                              group_by_node=1,
                              group_by_mirror_section=1,
                              group_by_resource=1,
                              **default_inventory_params):
        if inventory.total_price and inventory.total_quantity:
          stock_list.append(
              dict(destination_uid=node_uid,
                   destination_section_uid=section_uid,
                   source_section_uid=mirror_section_uid,
                   resource_uid=resource_uid,
                   quantity=inventory.total_quantity,
                   total_price=inventory.total_price, ))

    # payment
    for movement in self._getGroupByPaymentMovementList():
      node_uid = movement.getDestinationUid()
      if not node_uid:
        raise ValueError, "No destination uid for %s" % movement
      payment_uid = movement.getDestinationPaymentUid()
      resource_uid = movement.getResourceUid()

      stock_list = current_stock.setdefault(
                         InventoryKey(node_uid=node_uid,
                                      section_uid=section_uid,
                                      payment_uid=payment_uid), [])
      for inventory in getInventoryList(
                              node_uid=node_uid,
                              payment_uid=payment_uid,
                              resource_uid=resource_uid,
                              group_by_node=1,
                              group_by_payment=1,
                              group_by_resource=1,
                              **default_inventory_params):
        if inventory.total_price and inventory.total_quantity:
          stock_list.append(
              dict(destination_uid=node_uid,
                   destination_section_uid=section_uid,
                   destination_payment_uid=payment_uid,
                   resource_uid=resource_uid,
                   quantity=inventory.total_quantity,
                   total_price=inventory.total_price, ))

    return current_stock


  def _getNewStockDict(self):
    """Looks the new stock on lines in this inventory, and building a
    dictionnary of InventoryKey
    """
    new_stock = dict()
    # node
    for movement in self._getGroupByNodeMovementList():
      node_uid = movement.getDestinationUid()
      if not node_uid:
        raise ValueError, "No destination uid for %s" % movement
      section_uid = movement.getDestinationSectionUid()

      stock_list = new_stock.setdefault(
                 InventoryKey(node_uid=node_uid,
                              section_uid=section_uid), [])
      stock_list.append(
              dict(destination_uid=node_uid,
                   destination_section_uid=section_uid,
                   resource_uid=movement.getResourceUid(),
                   id=movement.getId(),
                   uid=movement.getUid(),
                   relative_url=movement.getRelativeUrl(),
                   quantity=movement.getQuantity(),
                   total_price=movement\
                    .getDestinationInventoriatedTotalAssetPrice(), ))
    
    # mirror section
    for movement in self._getGroupByMirrorSectionMovementList():
      node_uid = movement.getDestinationUid()
      if not node_uid:
        raise ValueError, "No destination uid for %s" % movement
      section_uid = movement.getDestinationSectionUid()
      mirror_section_uid = movement.getSourceSectionUid()

      stock_list = new_stock.setdefault(
                 InventoryKey(node_uid=node_uid,
                              mirror_section_uid=mirror_section_uid,
                              section_uid=section_uid), [])
      stock_list.append(
              dict(destination_uid=node_uid,
                   destination_section_uid=section_uid,
                   source_section_uid=mirror_section_uid,
                   resource_uid=movement.getResourceUid(),
                   id=movement.getId(),
                   uid=movement.getUid(),
                   relative_url=movement.getRelativeUrl(),
                   quantity=movement.getQuantity(),
                   total_price=movement\
                    .getDestinationInventoriatedTotalAssetPrice(), ))
    
    # payment
    for movement in self._getGroupByPaymentMovementList():
      node_uid = movement.getDestinationUid()
      if not node_uid:
        raise ValueError, "No destination uid for %s" % movement
      section_uid = movement.getDestinationSectionUid()
      payment_uid = movement.getDestinationPaymentUid()

      stock_list = new_stock.setdefault(
                 InventoryKey(node_uid=node_uid,
                              payment_uid=payment_uid,
                              section_uid=section_uid), [])
      stock_list.append(
              dict(destination_uid=node_uid,
                   destination_section_uid=section_uid,
                   destination_payment_uid=payment_uid,
                   resource_uid=movement.getResourceUid(),
                   id=movement.getId(),
                   uid=movement.getUid(),
                   relative_url=movement.getRelativeUrl(),
                   quantity=movement.getQuantity(),
                   total_price=movement\
                    .getDestinationInventoriatedTotalAssetPrice(), ))
    
    return new_stock


  def _computeStockDifferenceList(self, current_stock_dict, new_stock_dict):
    """Compute the difference between the result of _getCurrentStockDict and
    _getNewStockDict. Returns a list of dictionnaries with similar keys that
    the ones on inventory brains (node, section, mirror_section ...)
    """
    precision = self.getResourceValue().getQuantityPrecision()

    def computeStockDifference(current_stock_list, new_stock_list):
      # helper function to compute difference between two stock lists.
      if not current_stock_list:
        return new_stock_list
      
      stock_diff_list = current_stock_list[::] # deep copy ?

      for new_stock in new_stock_list:
        matching_diff = None
        for diff in stock_diff_list:
          for prop in [k for k in diff.keys() if k not in ('quantity',
                          'total_price', 'id', 'uid', 'relative_url')]:
            if diff[prop] != new_stock.get(prop):
              break
          else:
            matching_diff = diff
        
        # matching_diff are negated later
        if matching_diff:
          matching_diff['quantity'] -= round(new_stock['quantity'], precision)
          # Matching_diff and new_stock must be consistent.
          # both with total price or none.
          if matching_diff['total_price'] and new_stock['total_price']:
            matching_diff['total_price'] -= new_stock['total_price']
        else:
          stock_diff_list.append(new_stock)
      
      
      # we were doing with reversed calculation, so negate deltas again.
      # Also we remove stocks that have 0 quantity and price.
      return [negateStock(s) for s in stock_diff_list
              if round(s['quantity'], precision) and
                 round(s['total_price'], precision)]

    def negateStock(stock):
      negated_stock = stock.copy()
      negated_stock['quantity'] = -stock['quantity']
      if stock['total_price']:
        negated_stock['total_price'] = -stock['total_price']
      return negated_stock

    delta_list = []
    for current_stock_key, current_stock_value_list in \
                            current_stock_dict.items():
      if current_stock_key in new_stock_dict:
        delta_list.extend(computeStockDifference(
                              current_stock_value_list,
                              new_stock_dict[current_stock_key]))
      else:
        delta_list.extend(
            [negateStock(s) for s in current_stock_value_list])
    
    # now add every thing in new stock which was not in current stock
    for new_stock_key, new_stock_value_list in \
                                new_stock_dict.items():
      if new_stock_key not in current_stock_dict:
        delta_list.extend(new_stock_value_list)

    return delta_list


  def _getTempObjectFactory(self):
    """Returns the factory method that will create temp object.

    This method must return a function that accepts properties keywords
    arguments and returns a temp object edited with those properties.
    """
    from Products.ERP5Type.Document import newTempBalanceTransactionLine
    
    def factory(*args, **kw):
      doc = newTempBalanceTransactionLine(self, kw.pop('id', self.getId()),
                                         uid=self.getUid())
      relative_url = kw.pop('relative_url', None)
      destination_total_asset_price = kw.pop('total_price', None)
      if destination_total_asset_price is not None:
        kw['destination_total_asset_price'] = destination_total_asset_price
      doc._edit(*args, **kw)

      if relative_url:
        
        def URLGetter(url):
          def getRelativeUrl():
            return url
          return getRelativeUrl
        doc.getRelativeUrl = URLGetter(relative_url)
        
        def PathGetter(path):
          def getPath():
            return path
          return getPath
        doc.getPath = PathGetter(relative_url)

      return doc

    return factory


  security.declarePrivate('alternateReindexObject')
  def alternateReindexObject(self, **kw):
    """This method is called when an inventory object is included in a
    group of catalogged objects.
    """
    return self.immediateReindexObject(**kw)


  def immediateReindexObject(self, **kw):
    """Reindexes the object.
    This is different indexing that the default Inventory indexing, because
    we want to take into account that lines in this balance transaction to
    represent the balance of an account (node) with different parameters,
    based on the account_type of those accounts:
      - on standards accounts: it's simply the balance for node, section
       (and maybe resource, like all of thoses)
      - on payable / receivable accounts: for node, section and mirror
        section
      - on bank accounts: for node, section and payment

    Also this uses total_price (and quantity), and ignores variations and
    subvariations as it does not exist in accounting.
    """
    sql_catalog_id = kw.pop("sql_catalog_id", None)
    disable_archive = kw.pop("disable_archive", 0)

    if self.getSimulationState() in self.getPortalDraftOrderStateList():
      # this prevent from trying to calculate stock
      # with not all properties defined and thus making
      # request with no condition in mysql
      object_list = [self]
      immediate_reindex_archive = sql_catalog_id is not None
      self.portal_catalog.catalogObjectList(
                    object_list,
                    sql_catalog_id = sql_catalog_id,
                    disable_archive=disable_archive,
                    immediate_reindex_archive=immediate_reindex_archive)      
      return

    current_stock_dict = self._getCurrentStockDict()
    new_stock_dict = self._getNewStockDict()
    diff_list = self._computeStockDifferenceList(
                                    current_stock_dict,
                                    new_stock_dict)
    temp_object_factory = self._getTempObjectFactory()
    stock_object_list = []
    add_obj = stock_object_list.append
    for diff in diff_list:
      add_obj(temp_object_factory(**diff))

    # Catalog this transaction as a standard document
    self.portal_catalog.catalogObjectList([self])
    
    # Catalog differences calculated from lines
    self.portal_catalog.catalogObjectList(stock_object_list,
         method_id_list=('z_catalog_stock_list',
                         'z_catalog_object_list',
                         'z_catalog_movement_category_list'),
         disable_cache=1, check_uid=0)
    
