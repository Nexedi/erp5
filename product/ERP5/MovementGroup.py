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

from warnings import warn
from Products.PythonScripts.Utility import allow_class

class MovementRejected(Exception) : pass
class FakeMovementError(Exception) : pass
class MovementGroupError(Exception) : pass

class MovementGroupNode:
  def __init__(self, movement_group_list=None, movement_list=None,
               last_line_movement_group=None,
               separate_method_name_list=[], movement_group=None):
    self._movement_list = []
    self._group_list = []
    self._movement_group = movement_group
    self._movement_group_list = movement_group_list
    self._last_line_movement_group = last_line_movement_group
    self._separate_method_name_list = separate_method_name_list
    if movement_list is not None :
      self.append(movement_list)

  def _appendGroup(self, movement_list, property_dict):
    nested_instance = MovementGroupNode(
      movement_group=self._movement_group_list[0],
      movement_group_list=self._movement_group_list[1:],
      last_line_movement_group=self._last_line_movement_group,
      separate_method_name_list=self._separate_method_name_list)
    nested_instance.setGroupEdit(**property_dict)
    split_movement_list = nested_instance.append(movement_list)
    self._group_list.append(nested_instance)
    return split_movement_list

  def append(self, movement_list):
    all_split_movement_list = []
    if len(self._movement_group_list):
      for separate_movement_list, property_dict in \
          self._movement_group_list[0].separate(movement_list):
        split_movement_list = self._appendGroup(separate_movement_list,
                                                property_dict)
        if len(split_movement_list):
          if self._movement_group == self._last_line_movement_group:
            self.append(split_movement_list)
          else:
            all_split_movement_list.extend(split_movement_list)
    else:
      self._movement_list.append(movement_list[0])
      for movement in movement_list[1:]:
        # We have a conflict here, because it is forbidden to have
        # 2 movements on the same node group
        tmp_result = self._separate(movement)
        self._movement_list, split_movement = tmp_result
        if split_movement is not None:
          # We rejected a movement, we need to put it on another line
          # Or to create a new one
          all_split_movement_list.append(split_movement)
    return all_split_movement_list

  def getGroupList(self):
    return self._group_list

  def setGroupEdit(self, **kw):
    """
      Store properties for the futur created object
    """
    self._property_dict = kw

  def updateGroupEdit(self, **kw):
    """
      Update properties for the futur created object
    """
    self._property_dict.update(kw)

  def getGroupEditDict(self):
    """
      Get property dict for the futur created object
    """
    property_dict = getattr(self, '_property_dict', {}).copy()
    for key in property_dict.keys():
      if key.startswith('_'):
        del(property_dict[key])
    return property_dict

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
        if divergence_scope is None:
          # Update anyway (eg. CausalityAssignmentMovementGroup etc.)
          pass
        else:
          related_divergence_list = [
            x for x in divergence_list \
            if divergence_scope == x.divergence_scope and \
            self.hasSimulationMovement(x.simulation_movement)]
          if not len(related_divergence_list):
            return True, {}
          property_list = [x.tested_property for x in related_divergence_list]
      return self._movement_group.test(movement, self._property_dict,
                                               property_list=property_list)
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
      raise ValueError, "Can separate only 2 movements"
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
    if added_movement is not None and \
            movement.getPrice() == added_movement.getPrice() :
      new_movement = self._genericCalculation(movement,
                                              added_movement=added_movement)
      new_movement.setPriceMethod('getAveragePrice')
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
      raise ValueError, "FakeMovement used where it should not."
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
        raise ValueError, "FakeMovement not well used."

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

  def setDeliveryValue(self, object):
    """
      Set Delivery value for each movement
    """
    for movement in self.__movement_list:
      movement.edit(delivery_value=object)

  def getDeliveryValue(self):
    """
      Only use to test if all movement are not linked (if user did not
      configure DeliveryBuilder well...).
      Be careful.
    """
    result = None
    for movement in self.__movement_list:
      mvt_delivery = movement.getDeliveryValue()
      if mvt_delivery is not None:
        result = mvt_delivery
        break
    return result

  def getRelativeUrl(self):
    """
      Only use to return a short description of one movement
      (if user did not configure DeliveryBuilder well...).
      Be careful.
    """
    return self.__movement_list[0].getRelativeUrl()

  def setDeliveryRatio(self, delivery_ratio):
    """
      Calculate delivery_ratio
    """
    total_quantity = 0
    for movement in self.__movement_list:
      total_quantity += movement.getQuantity()

    if total_quantity != 0:
      for movement in self.__movement_list:
        quantity = movement.getQuantity()
        movement.edit(delivery_ratio=quantity*delivery_ratio/total_quantity)
    else:
      # Distribute equally ratio to all movement
      mvt_ratio = 1 / len(self.__movement_list)
      for movement in self.__movement_list:
        movement.edit(delivery_ratio=mvt_ratio)

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

  def getAveragePrice(self):
    """
      Return average price
    """
    if self.getAddQuantity()>0:
      return (self.getAddPrice() / self.getAddQuantity())
    return 0.0

  def getAddQuantity(self):
    """
      Return the total quantity
    """
    total_quantity = 0
    for movement in self.getMovementList():
      quantity = movement.getQuantity()
      if quantity != None:
        total_quantity += quantity
    return total_quantity

  def getAddPrice(self):
    """
      Return total price
    """
    total_price = 0
    for movement in self.getMovementList():
      quantity = movement.getQuantity()
      price = movement.getPrice()
      if (quantity is not None) and (price is not None):
        total_price += (quantity * price)
    return total_price

  def recursiveReindexObject(self):
    """
      Reindex all movements
    """
    for movement in self.getMovementList():
      movement.recursiveReindexObject()

  def immediateReindexObject(self):
    """
      Reindex immediately all movements
    """
    for movement in self.getMovementList():
      movement.immediateReindexObject()

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

  def edit(self, activate_kw=None, **kw):
    """
      Written in order to call edit in delivery builder,
      as it is the generic way to modify object.

      activate_kw is here for compatibility reason with Base.edit,
      it will not be used here.
    """
    for key in kw.keys():
      if key == 'delivery_ratio':
        self.setDeliveryRatio(kw[key])
      elif key == 'delivery_value':
        self.setDeliveryValue(kw[key])
      else:
        raise FakeMovementError,\
              "Could not call edit on Fakemovement with parameters: %r" % key

  def __repr__(self):
    repr_str = '<%s object at 0x%x for %r' % (self.__class__.__name__,
                                              id(self),
                                              self.getMovementList())
    return repr_str

# The following classes are not ported to Document/XxxxMovementGroup.py yet.

class RootMovementGroup(MovementGroupNode):
  pass

class CriterionMovementGroup(RootMovementGroup):
  def __init__(self,movement,**kw):
    RootMovementGroup.__init__(self, movement=movement, **kw)
    if hasattr(movement, 'getGroupCriterion'):
      self.criterion = movement.getGroupCriterion()
    else:
      self.criterion = None

  def test(self,movement):
    # we must have the same criterion
    if hasattr(movement, 'getGroupCriterion'):
      criterion = movement.getGroupCriterion()
    else:
      criterion = None
    return self.criterion == criterion

allow_class(CriterionMovementGroup)

class SplitResourceMovementGroup(RootMovementGroup):

  def __init__(self, movement, **kw):
    RootMovementGroup.__init__(self, movement=movement, **kw)
    self.resource = movement.getResource()

  def test(self, movement):
    return movement.getResource() == self.resource

allow_class(SplitResourceMovementGroup)

class OptionMovementGroup(RootMovementGroup):

  def __init__(self,movement,**kw):
    RootMovementGroup.__init__(self, movement=movement, **kw)
    option_base_category_list = movement.getPortalOptionBaseCategoryList()
    self.option_category_list = movement.getVariationCategoryList(
                                  base_category_list=option_base_category_list)
    if self.option_category_list is None:
      self.option_category_list = []
    self.option_category_list.sort()
    # XXX This is very bad, but no choice today.
    self.setGroupEdit(industrial_phase_list = self.option_category_list)

  def test(self,movement):
    option_base_category_list = movement.getPortalOptionBaseCategoryList()
    movement_option_category_list = movement.getVariationCategoryList(
                              base_category_list=option_base_category_list)
    if movement_option_category_list is None:
      movement_option_category_list = []
    movement_option_category_list.sort()
    return movement_option_category_list == self.option_category_list

allow_class(OptionMovementGroup)

# XXX This should not be here
# I (seb) have commited this because movement groups are not
# yet configurable through the zope web interface
class IntIndexMovementGroup(RootMovementGroup):

  def getIntIndex(self,movement):
    order_value = movement.getOrderValue()
    int_index = 0
    if order_value is not None:
      if "Line" in order_value.getPortalType():
        int_index = order_value.getIntIndex()
      elif "Cell" in order_value.getPortalType():
        int_index = order_value.getParentValue().getIntIndex()
    return int_index

  def __init__(self,movement,**kw):
    RootMovementGroup.__init__(self, movement=movement, **kw)
    int_index = self.getIntIndex(movement)
    self.int_index = int_index
    self.setGroupEdit(
        int_index=int_index
    )

  def test(self,movement):
    return self.getIntIndex(movement) == self.int_index

allow_class(IntIndexMovementGroup)

class TransformationAppliedRuleCausalityMovementGroup(RootMovementGroup):
  """
  Groups movement that comes from simulation movement that shares the
  same Production Applied Rule.
  """
  def __init__(self, movement, **kw):
    RootMovementGroup.__init__(self, movement=movement, **kw)
    explanation_relative_url = self._getExplanationRelativeUrl(movement)
    self.explanation = explanation_relative_url
    explanation_value = movement.getPortalObject().restrictedTraverse(
                                                    explanation_relative_url)
    self.setGroupEdit(causality_value=explanation_value)

  def _getExplanationRelativeUrl(self, movement):
    """ Get the order value for a movement """
    transformation_applied_rule = movement.getParentValue()
    transformation_rule = transformation_applied_rule.getSpecialiseValue()
    if transformation_rule.getPortalType() != 'Transformation Rule':
      raise MovementGroupError, 'movement! %s' % movement.getPath()
    # XXX Dirty hardcoded
    production_movement = transformation_applied_rule.pr
    production_packing_list = production_movement.getExplanationValue()
    return production_packing_list.getRelativeUrl()

  def test(self,movement):
    return self._getExplanationRelativeUrl(movement) == self.explanation

allow_class(TransformationAppliedRuleCausalityMovementGroup)

class ParentExplanationMovementGroup(RootMovementGroup): pass

class ParentExplanationCausalityMovementGroup(ParentExplanationMovementGroup):
  """
  Like ParentExplanationMovementGroup, and set the causality.
  """
  def __init__(self, movement, **kw):
    ParentExplanationMovementGroup.__init__(self, movement=movement, **kw)
    self.updateGroupEdit(
        causality_value = self.explanation_value
    )

allow_class(ParentExplanationCausalityMovementGroup)
