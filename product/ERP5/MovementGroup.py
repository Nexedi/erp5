##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Yoshinori Okuji <yo@nexedi.com>
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

"""
Define in this class all classes intended to group every kind of movement
"""

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from zLOG import LOG
from Products.PythonScripts.Utility import allow_class

class RootMovementGroup:

  def __init__(self, class_list, movement=None, last_line_class_name=None,
               separate_method_name_list=[]):
    self._nested_class = None
    self.setNestedClass(class_list=class_list)
    self._movement_list = []
    self._group_list = []

    self._class_list = class_list
    self._last_line_class_name = last_line_class_name
    self._separate_method_name_list = separate_method_name_list

    if movement is not None :
      self.append(movement)

  def getNestedClass(self, class_list):
    if len(class_list)>0:
      return class_list[0]
    return None

  def setNestedClass(self,class_list):
    """
      This sets an appropriate nested class.
    """
    self._nested_class = self.getNestedClass(class_list)

  def _appendGroup(self, movement):
    nested_instance = self._nested_class(
                    movement=movement,
                    class_list=self._class_list[1:],
                    last_line_class_name=self._last_line_class_name,
                    separate_method_name_list=self._separate_method_name_list)
    self._group_list.append(nested_instance)

  def append(self, movement):
    is_movement_in_group = 0
    for group in self.getGroupList():
      if group.test(movement) :
        group.append(movement)
        is_movement_in_group = 1
        break
    if is_movement_in_group == 0 :
      if self._nested_class is not None:
        self._appendGroup(movement)
      else:
        # We are on a node group
        movement_list = self.getMovementList()
        if len(movement_list) > 0:
          # We have a conflict here, because it is forbidden to have 
          # 2 movements on the same node group
          tmp_result = self._separate(movement)
          self._movement_list, split_movement_list = tmp_result
          # XXX Do something with split_movement_list !
        else:
          # No movement on this node, we can add it
          self._movement_list.append(movement)

  def getGroupList(self):
    return self._group_list

  def setGroupEdit(self, **kw):
    """
      Store properties for the futur created object 
    """
    self._property_dict = kw

  def getGroupEditDict(self):
    """
      Get property dict for the futur created object 
    """
    if hasattr(self, '_property_dict'):
      return self._property_dict
    else:
      return {}

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

  def _separate(self, movement):
    """
      Separate 2 movements on a node group
    """
    movement_list = self.getMovementList()
    if len(movement_list) != 1:
      raise "ProgrammingError", "Can separate only 2 movements"
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
        added_movement = None

      return [new_stored_movement], [rejected_movement]

  ########################################################
  # Separate methods
  ########################################################
  def _genericCalculation(self, movement, added_movement=None):
    """
      Generic creation of FakeMovement
    """
    if added_movement is not None:
      # Create a fake movement
      new_movement = FakeMovement([movement, added_movement])
    else:
      new_movement = movement
    return new_movement

  def calculateAveragePrice(self, movement, added_movement=None):
    """
      Create a new movement with a average price
    """
    new_movement = self._genericCalculation(movement, 
                                            added_movement=added_movement)
    new_movement.setPriceMethod("getAveragePrice")
    return new_movement, None

  def calculateAddQuantity(self, movement, added_movement=None):
    """
      Create a new movement with the sum of quantity
    """
    new_movement = self._genericCalculation(movement, 
                                            added_movement=added_movement)
    new_movement.setQuantityMethod("getAddQuantity")
    return new_movement, None

allow_class(RootMovementGroup)

class OrderMovementGroup(RootMovementGroup):
  def __init__(self,movement, **kw):
    #LOG('OrderMovementGroup.__init__, kw:',0,kw)
    RootMovementGroup.__init__(self, movement=movement, **kw)
    if hasattr(movement, 'getRootAppliedRule'):
      # This is a simulation movement
      order_value = movement.getRootAppliedRule().getCausalityValue(
                              portal_type=movement.getPortalOrderTypeList())
      if order_value is None:
        # In some cases (ex. DeliveryRule), there is no order
        # we may consider a PackingList as the order in the OrderGroup
        order_value = movement.getRootAppliedRule().getCausalityValue(
                        portal_type=movement.getPortalDeliveryTypeList())
    else:
      # This is a temp movement
      order_value = None
    if order_value is None:
      order_relative_url = None
    else:
      # get the id of the enclosing delivery
      # for this cell or line
      order_relative_url = order_value.getRelativeUrl()
    self.order = order_relative_url
    self.setGroupEdit(causality_value=order_value)

  def test(self,movement):
    if hasattr(movement, 'getRootAppliedRule'):
      order_value = movement.getRootAppliedRule().getCausalityValue(
                        portal_type=movement.getPortalOrderTypeList())

      if order_value is None:
        # In some cases (ex. DeliveryRule), there is no order
        # we may consider a PackingList as the order in the OrderGroup
        order_value = movement.getRootAppliedRule().getCausalityValue(
                        portal_type=movement.getPortalDeliveryTypeList())
    else:
      # This is a temp movement
      order_value = None
    if order_value is None:
      order_relative_url = None
    else:
      # get the id of the enclosing delivery
      # for this cell or line
      order_relative_url = order_value.getRelativeUrl()
    if order_relative_url == self.order:
      return 1
    else :
      return 0

allow_class(OrderMovementGroup)

class PathMovementGroup(RootMovementGroup):

  def __init__(self,movement,**kw):
    RootMovementGroup.__init__(self, movement=movement, **kw)
    self.source = movement.getSource()
    #LOG('PathGroup.__init__ source',0,self.source)
    self.destination = movement.getDestination()
    #LOG('PathGroup.__init__ destination',0,self.destination)
    self.source_section = movement.getSourceSection()
    #LOG('PathGroup.__init__ source_section',0,self.source_section)
    self.destination_section = movement.getDestinationSection()
    #LOG('PathGroup.__init__ destination_section',0,self.destination_section)
    self.setGroupEdit(
        source_value=movement.getSourceValue(),
        destination_value=movement.getDestinationValue(),
        source_section_value=movement.getSourceSectionValue(),
        destination_section_value=movement.getDestinationSectionValue(),
    )


  def test(self,movement):
    if movement.getSource() == self.source and \
      movement.getDestination() == self.destination and \
      movement.getSourceSection() == self.source_section and \
      movement.getDestinationSection() == self.destination_section  :

      return 1
    else :
      return 0

allow_class(PathMovementGroup)

class DateMovementGroup(RootMovementGroup):

  def __init__(self,movement,**kw):
    RootMovementGroup.__init__(self, movement=movement, **kw)
    self.start_date = movement.getStartDate()
    self.stop_date = movement.getStopDate()
    self.setGroupEdit(
        start_date=movement.getStartDate(),
        stop_date=movement.getStopDate()
    )

  def test(self,movement):
    if movement.getStartDate() == self.start_date and \
      movement.getStopDate() == self.stop_date :
      return 1
    else :
      return 0

allow_class(DateMovementGroup)

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

class ResourceMovementGroup(RootMovementGroup):

  def __init__(self,movement,**kw):
    RootMovementGroup.__init__(self, movement=movement, **kw)
    self.resource = movement.getResource()
    self.setGroupEdit(
        resource_value=self.resource
    )

  def test(self,movement):
    if movement.getResource() == self.resource :
      return 1
    else :
      return 0

allow_class(ResourceMovementGroup)

class BaseVariantMovementGroup(RootMovementGroup):

  def __init__(self,movement,**kw):
    RootMovementGroup.__init__(self, movement=movement, **kw)
    self.base_category_list = movement.getVariationBaseCategoryList()
    if self.base_category_list is None:
      #LOG('BaseVariantGroup __init__', 0, 'movement = %s, movement.showDict() = %s' % (repr(movement), repr(movement.showDict())))
      self.base_category_list = []

  def test(self,movement):
    # we must have the same number of categories
    categories_identity = 0
    #LOG('BaseVariantGroup', 0, 'self.base_category_list = %s, movement = %s, movement.getVariationBaseCategoryList() = %s' % (repr(self.base_category_list), repr(movement), repr(movement.getVariationBaseCategoryList())))
    movement_base_category_list = movement.getVariationBaseCategoryList()
    if movement_base_category_list is None:
      #LOG('BaseVariantGroup test', 0, 'movement = %s, movement.showDict() = %s' % (repr(movement), repr(movement.showDict())))
      movement_base_category_list = []
    if len(self.base_category_list) == len(movement_base_category_list):
      for category in movement_base_category_list:
        if not category in self.base_category_list :
          break
      else :
        categories_identity = 1
    return categories_identity

allow_class(BaseVariantMovementGroup)

class VariantMovementGroup(RootMovementGroup):

  def __init__(self,movement,**kw):
    RootMovementGroup.__init__(self, movement=movement, **kw)
    self.category_list = movement.getVariationCategoryList()
    if self.category_list is None:
      #LOG('VariantGroup __init__', 0, 'movement = %s, movement.showDict() = %s' % (repr(movement), repr(movement.showDict())))
      self.category_list = []
    self.setGroupEdit(
        variation_category_list=self.category_list
    )

  def test(self,movement):
    # we must have the same number of categories
    categories_identity = 0
    movement_category_list = movement.getVariationCategoryList()
    if movement_category_list is None:
      #LOG('VariantGroup test', 0, 'movement = %s, movement.showDict() = %s' % (repr(movement), repr(movement.showDict())))
      movement_category_list = []
    if len(self.category_list) == len(movement_category_list):
      for category in movement_category_list:
        if not category in self.category_list :
          break
      else :
        categories_identity = 1
    return categories_identity

allow_class(VariantMovementGroup)

from copy import copy

class CategoryMovementGroup(RootMovementGroup):  
  """
    This seems to be a useless class
  """
  def __init__(self,movement,**kw):
    RootMovementGroup.__init__(self, movement=movement, **kw)
    self.category_list = list(movement.getCategoryList())
    if self.category_list is None:
      self.category_list = []
    self.category_list.sort()

  def test(self,movement):
    # we must have the same number of categories
    movement_category_list = list(movement.getCategoryList())
    if movement_category_list is None:
      movement_category_list = []
    movement_category_list.sort()
    if self.category_list == movement_category_list:
      return 1
    return 0

allow_class(CategoryMovementGroup)

class FakeMovement:
  """
    A fake movement which simulate some methods on a movement needed 
    by DeliveryBuilder.
    It contents a list a real ERP5 Movement and can modify them.
  """
  def __init__(self, movement_list):
    """
      Create a fake movement and store the list of real movement
    """
    self.__price_method = None
    self.__quantity_method = None
    self.__movement_list = []
    for movement in movement_list:
      self.append(movement)
    # This object must not be use when there is not 2 or more movements
    if len(movement_list) < 2:
      raise "ProgrammingError", "FakeMovement used where it does not."
    # All movements must share the same getVariationCategoryList
    # So, verify and raise a error if not
    # But, if DeliveryBuilder is well configured, this can never append ;)
    reference_variation_category_list = movement_list[0].\
                                           getVariationCategoryList()
    error_raising_needed = 0
    for movement in movement_list[1:]:
      variation_category_list = movement.getVariationCategoryList()
      if len(variation_category_list) !=\
         len(reference_variation_category_list):
        error_raising_needed = 1
        break

      for variation_category in variation_category_list:
        if variation_category not in reference_variation_category_list:
          error_raising_needed = 1
          break
    
    if error_raising_needed == 1:
      raise "ProgrammingError", "FakeMovement not well used."

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
      And calculate delivery_ratio
    """
    for movement in self.__movement_list:
      # XXX is delivery_ratio well calculated ?
      # movement.getQuantity / 
      #  (sum object.getRelatedSimulationMovement.getQuantity)
      movement.edit(
          delivery_value=object,
          delivery_ratio=(movement.getQuantity() / object.getQuantity()))
      
  def getPrice(self):
    """
      Return calculated price
    """
    return getattr(self, self.__price_method)()
  
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
    return (self.getAddPrice() / self.getAddQuantity())

  def getAddQuantity(self):
    """
      Return the total quantity
    """
    total_quantity = 0
    for movement in self.getMovementList():
      total_quantity += movement.getQuantity()
    return total_quantity

  def getAddPrice(self):
    """
      Return total price 
    """
    total_price = 0
    for movement in self.getMovementList():
      total_price += (movement.getQuantity() * movement.getPrice())
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

  def getVariationBaseCategoryList(self):
    """
      Return variation base category list
      Which must be shared by all movement
    """
    return self.__movement_list[0].getVariationBaseCategoryList()

  def getVariationCategoryList(self):
    """
      Return variation base category list
      Which must be shared by all movement
    """
    return self.__movement_list[0].getVariationCategoryList()
