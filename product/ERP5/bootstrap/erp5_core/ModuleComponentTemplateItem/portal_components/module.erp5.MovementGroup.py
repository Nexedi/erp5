##############################################################################
#
# Copyright (c) 2002-2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Yoshinori Okuji <yo@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

from collections import OrderedDict
from warnings import warn
from Products.PythonScripts.Utility import allow_class


class MovementGroupNode:
  # XXX last_line_movement_group is a wrong name. Actually, it is
  # the last delivery movement group. This parameter is used to
  # pick up a branching point of making separate lines when
  # a separate method requests separating movements.
  def __init__(self, movement_group_list=None, movement_list=None,
               last_line_movement_group=None,
               separate_method_name_list=(), movement_group=None,
               merge_delivery=None):
    self._movement_list = []
    self._group_list = []
    self._movement_group = movement_group
    self._movement_group_list = movement_group_list
    self._last_line_movement_group = last_line_movement_group
    self._separate_method_name_list = separate_method_name_list
    self._merge_delivery = merge_delivery
    if movement_list is not None :
      self.append(movement_list)

  def _appendGroup(self, movement_list, property_dict):
    nested_instance = MovementGroupNode(
      movement_group=self._movement_group_list[0],
      movement_group_list=self._movement_group_list[1:],
      last_line_movement_group=self._last_line_movement_group,
      separate_method_name_list=self._separate_method_name_list,
      merge_delivery=self._merge_delivery)
    nested_instance.setGroupEdit(property_dict)
    split_movement_list = nested_instance.append(movement_list)
    self._group_list.append(nested_instance)
    return split_movement_list

  def append(self, movement_list, **kw):
    all_split_movement_list = []
    if len(self._movement_group_list):
      for separate_movement_list, property_dict in \
          self._movement_group_list[0].separate(movement_list,
                                                merge_delivery=self._merge_delivery):
        split_movement_list = self._appendGroup(separate_movement_list,
                                                property_dict)
        if len(split_movement_list):
          if self._movement_group == self._last_line_movement_group:
            self.append(split_movement_list, **kw)
          else:
            all_split_movement_list.extend(split_movement_list)
    else:
      self._movement_list.append(movement_list[0])
      for movement in movement_list[1:]:
        # We have a conflict here, because it is forbidden to have
        # 2 movements on the same node group
        self._movement_list, split_movement = self._separate(movement)
        if split_movement is not None:
          # We rejected a movement, we need to put it on another line
          # Or to create a new one
          all_split_movement_list.append(split_movement)
    return all_split_movement_list

  def getGroupList(self):
    return self._group_list

  def setGroupEdit(self, kw):
    """
      Store properties for the future created object
    """
    self._property_dict = kw

  def getGroupEditDict(self):
    """
      Get property dict for the future created object
    """
    return OrderedDict([
      (k, v)
      for (k, v) in getattr(self, '_property_dict', {}).items()
      if not k.startswith('_')])

  def getCurrentMovementGroup(self):
    return self._movement_group

  def getMovementList(self):
    """
      Return movement list in the current group
    """
    movement_list = []
    group_list = self.getGroupList()
    if len(group_list) == 0:
      return self._movement_list
    else:
      for group in group_list:
        movement_list.extend(group.getMovementList())
      return movement_list

  def getMovement(self):
    """
      Return first movement of the movement list in the current group
    """
    movement = self.getMovementList()[0]
    if movement.__class__.__name__ == 'FakeMovement':
      return movement.getMovementList()[0]
    else:
      return movement

  def test(self, movement, divergence_list):
    # Try to check if movement is updatable or not.
    #
    # 1. if Divergence has no scope: update anyway.
    # 2. if Divergence has a scope: update in related Movement Group only.
    #
    # return value is:
    #   [updatable? (True/False), property dict for update]
    if self._movement_group is not None:
      property_list = []
      if len(divergence_list):
        divergence_scope = self._movement_group.getDivergenceScope()
        if divergence_scope is not None:
          for divergence in divergence_list:
            if (divergence_scope == getattr(divergence, 'divergence_scope',
                                            # assume match if missing
                                            # (e.g. for new simulation)
                                            divergence_scope) and
                self.hasSimulationMovement(divergence.simulation_movement)):
              property_list.append(divergence.tested_property)
          if not property_list:
            return True, {}
        # else update anyway (eg. CausalityAssignmentMovementGroup etc.)
      result, property_dict = self._movement_group.test(
        movement, self._property_dict, property_list=property_list)
      # The following check is partial because it does not check mutable values
      # recursively.
      different_property_dict = self._property_dict != property_dict
      if property_dict is different_property_dict:
        raise ValueError(
          "Movement Group must not modify the passed 'property_dict':"
          " copy it, deeply if necessary, before editing properties")
      return result, property_dict
    else:
      return True, {}

  def getDivergenceScope(self):
    if self._movement_group is not None:
      return self._movement_group.getDivergenceScope()
    else:
      return None

  def hasSimulationMovement(self, simulation_movement):
    for movement in self.getMovementList():
      if movement.__class__.__name__ == "FakeMovement":
        if simulation_movement in movement.getMovementList():
          return True
      elif simulation_movement == movement:
        return True
    return False

  def _separate(self, movement):
    """
      Separate 2 movements on a node group
    """
    movement_list = self.getMovementList()
    if len(movement_list) != 1:
      raise ValueError("Can separate only 2 movements")
    else:
      old_movement = self.getMovementList()[0]

      new_stored_movement = old_movement
      added_movement = movement
      rejected_movement = None

      for separate_method_name in self._separate_method_name_list:
        method = getattr(self, separate_method_name)

        new_stored_movement,\
        rejected_movement= method(new_stored_movement,
                                  added_movement=added_movement)
        if rejected_movement is None:
          added_movement = None
        else:
          break

      return [new_stored_movement], rejected_movement

  ########################################################
  # Separate methods
  ########################################################
  def _genericCalculation(self, movement, added_movement=None):
    """ Generic creation of FakeMovement
    """
    if added_movement is not None:
      # Create a fake movement
      new_movement = FakeMovement([movement, added_movement])
    else:
      new_movement = movement
    return new_movement

  def calculateAveragePrice(self, movement, added_movement=None):
    """ Create a new movement with a average price
    """
    new_movement = self._genericCalculation(movement,
                                            added_movement=added_movement)
    new_movement.setPriceMethod("getAveragePrice")
    return new_movement, None

  def calculateSeparatePrice(self, movement, added_movement=None):
    """ Separate movements which have different price
    """
    if added_movement is not None:
      # XXX To prevent float rounding issue, we round the price with an
      # arbirary precision before comparision.
      movement_price = movement.getPrice()
      if movement_price is not None:
        movement_price = round(movement_price, 5)
      added_movement_price = added_movement.getPrice()
      if added_movement_price is not None:
        added_movement_price = round(added_movement_price, 5)

      if movement_price == added_movement_price:
        new_movement = self._genericCalculation(movement,
                                                added_movement=added_movement)
        new_movement.setPriceMethod('getFirstPrice')
        new_movement.setQuantityMethod("getAddQuantity")
        return new_movement, None
    return movement, added_movement

  def calculateAddQuantity(self, movement, added_movement=None):
    """ Create a new movement with the sum of quantity
    """
    new_movement = self._genericCalculation(movement,
                                            added_movement=added_movement)
    new_movement.setQuantityMethod("getAddQuantity")
    return new_movement, None

  def __repr__(self):
    repr_str = '<%s object at 0x%x\n' % (self.__class__.__name__, id(self))
    repr_str += ' _movement_group = %r,\n' % self._movement_group
    if getattr(self, '_property_dict', None) is not None:
      repr_str += ' _property_dict = %r,\n' % self._property_dict
    if self._movement_list:
      repr_str += ' _movement_list = %r,\n' % self._movement_list
    if self._group_list:
      repr_str += ' _group_list = [\n%s]>' % (
        '\n'.join(['   %s' % x for x in (',\n'.join([repr(i) for i in self._group_list])).split('\n')]))
    else:
      repr_str += ' _last_line_movement_group = %r,\n' % self._last_line_movement_group
      repr_str += ' _separate_method_name_list = %r>' % self._separate_method_name_list
    return repr_str

allow_class(MovementGroupNode)

class FakeMovement:
  """
    A fake movement which simulates some methods on a movement needed
    by DeliveryBuilder.
    It contains a list of real ERP5 Movements and can modify them.
  """

  def __init__(self, movement_list):
    """
      Create a fake movement and store the list of real movements
    """
    self.__price_method = None
    self.__quantity_method = None
    self.__movement_list = []
    for movement in movement_list:
      self.append(movement)
    # This object must not be use when there is not 2 or more movements
    if len(movement_list) < 2:
      raise ValueError("FakeMovement used where it should not.")
    # All movements must share the same getVariationCategoryList
    # So, verify and raise a error if not
    # But, if DeliveryBuilder is well configured, this can never append ;)
    reference_variation_category_list = movement_list[0].\
                                           getVariationCategoryList()
    reference_variation_category_list.sort()
    for movement in movement_list[1:]:
      variation_category_list = movement.getVariationCategoryList()
      variation_category_list.sort()
      if variation_category_list != reference_variation_category_list:
        raise ValueError("FakeMovement not well used.")

  def append(self, movement):
    """
      Append movement to the movement list
    """
    if movement.__class__.__name__ == "FakeMovement":
      self.__movement_list.extend(movement.getMovementList())
      self.__price_method = movement.__price_method
      self.__quantity_method = movement.__quantity_method
    else:
      self.__movement_list.append(movement)

  def getMovementList(self):
    """
      Return content movement list
    """
    return self.__movement_list

  def isTempDocument(self):
    for movement in self.__movement_list:
      if movement.isTempDocument():
        return True
    return False

  def _setDelivery(self, object): # pylint: disable=redefined-builtin
    """
      Set Delivery value for each movement
    """
    for movement in self.__movement_list:
      movement._setDelivery(object)

  def getDeliveryList(self):
    """
      Only used to know if _setDeliveryValue needs to be called.
      Be careful: behaviour differs from CMFCategory in that returned
      list may include None, when there is at least 1 unlinked SM.
    """
    return list({x.getDelivery() for x in self.__movement_list})

  def getDeliveryValue(self):
    """
      Only use to test if all movement are not linked (if user did not
      configure DeliveryBuilder well...).
      Be careful.
    """
    for movement in self.__movement_list:
      mvt_delivery = movement.getDeliveryValue()
      if mvt_delivery is not None:
        return mvt_delivery

  def getRelativeUrl(self):
    """
      Only use to return a short description of one movement
      (if user did not configure DeliveryBuilder well...).
      Be careful.
    """
    return self.__movement_list[0].getRelativeUrl()

  def _setDeliveryRatio(self, delivery_ratio):
    """
      Calculate delivery_ratio
    """
    total_quantity = 0
    for movement in self.__movement_list:
      total_quantity += movement.getProperty('quantity')

    if total_quantity:
      for movement in self.__movement_list:
        quantity = movement.getProperty('quantity')
        movement._setDeliveryRatio(quantity*float(delivery_ratio)/total_quantity)
    else:
      # Distribute equally ratio to all movements
      mvt_ratio = float(delivery_ratio) / len(self.__movement_list)
      for movement in self.__movement_list:
        movement._setDeliveryRatio(mvt_ratio)

  def getPrice(self):
    """
      Return calculated price
    """
    if self.__price_method is not None:
      return getattr(self, self.__price_method)()
    else:
      return None

  def setPriceMethod(self, method):
    """
      Set the price method
    """
    self.__price_method = method

  def getQuantity(self):
    """
      Return calculated quantity
    """
    return getattr(self, self.__quantity_method)()

  def setQuantityMethod(self, method):
    """
      Set the quantity method
    """
    self.__quantity_method = method

  def getFirstPrice(self):
    """
    Get price defined on the first movement
    """
    return self.getMovementList()[0].getPrice(0)

  def getAveragePrice(self):
    """
      Return average price
    """
    price_dict = self._getPriceDict()
    if len(price_dict) == 1:
      return list(price_dict.keys())[0]
    total_quantity = sum(price_dict.values())
    return (total_quantity and
      sum(price * quantity for price, quantity in price_dict.items())
      / float(total_quantity))

  def getAddQuantity(self):
    """
      Return the total quantity
    """
    total_quantity = 0
    for movement in self.getMovementList():
      quantity = movement.getQuantity()
      if quantity:
        total_quantity += quantity
    return total_quantity

  def _getPriceDict(self):
    price_dict = {}
    for movement in self.getMovementList():
      quantity = movement.getQuantity()
      if quantity:
        price = movement.getPrice() or 0
        quantity += price_dict.setdefault(price, 0)
        price_dict[price] = quantity
    return price_dict

  def getAddPrice(self):
    """
      Return total price
    """
    price_dict = self._getPriceDict()
    return sum(price * quantity for price, quantity in price_dict.items())

  def recursiveReindexObject(self, *args, **kw):
    """
      Reindex all movements
    """
    for movement in self.getMovementList():
      movement.recursiveReindexObject(*args, **kw)

  def getPath(self):
    """
      Return the movements path list
    """
    path_list = []
    for movement in self.getMovementList():
      path_list.append(movement.getPath())
    return path_list

  def getVariationBaseCategoryList(self, omit_optional_variation=0,
      omit_option_base_category=None, **kw):
    """
      Return variation base category list
      Which must be shared by all movement
    """
    #XXX backwards compatibility
    if omit_option_base_category is not None:
      warn("Please use omit_optional_variation instead of"\
          " omit_option_base_category.", DeprecationWarning)
      omit_optional_variation = omit_option_base_category

    return self.__movement_list[0].getVariationBaseCategoryList(
        omit_optional_variation=omit_optional_variation, **kw)

  def getVariationCategoryList(self, omit_optional_variation=0,
      omit_option_base_category=None, **kw):
    """
      Return variation base category list
      Which must be shared by all movement
    """
    #XXX backwards compatibility
    if omit_option_base_category is not None:
      warn("Please use omit_optional_variation instead of"\
          " omit_option_base_category.", DeprecationWarning)
      omit_optional_variation = omit_option_base_category

    return self.__movement_list[0].getVariationCategoryList(
        omit_optional_variation=omit_optional_variation, **kw)

  def __repr__(self):
    repr_str = '<%s object at 0x%x for %r' % (self.__class__.__name__,
                                              id(self),
                                              self.getMovementList())
    return repr_str