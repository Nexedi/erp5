##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

from Products.ERP5Type.Base import Base
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from AccessControl import ClassSecurityInfo

class RootMovementGroup(Base):

  meta_type = 'ERP5 Root Movement Group'
  portal_type = 'Root Movement Group'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  def getNestedClass(self, class_list):
    for a in class_list:
      if a[0]:
        return a[1]
    return None

  def setNestedClass(self):
    """
      This sets an appropriate nested class.
    """
    def cmpfunc(a,b):
      return cmp(a[0],b[0])
    
    class_list = [(1, RootMovementGroup),
                  (check_order, OrderGroup),
                  (check_path, PathGroup),
                  (check_date, DateGroup),
                  (check_criterion, CriterionGroup),
                  (check_resource, ResourceGroup),
                  (check_base_variant, BaseVariantGroup),
                  (check_variant, VariantGroup),
                  ]
    class_list.sort(cmpfunc)
    for i in range(len(class_list)):
      if class_list[i][1] == self.__class__:
        break
    else:
      raise RuntimeError, "no appropriate nested class is found for %s" % str(self)

    self.nested_class = self.getNestedClass(class_list[i+1:])

  def __init__(self, movement=None):
    self.nested_class = None
    self.setNestedClass()
    self.movement_list = []
    self.group_list = []
    if movement is not None :
      self.append(movement)

  def appendGroup(self, movement):
    if self.nested_class is not None:
      self.group_list.append(self.nested_class(movement))

  def append(self,movement):
    self.movement_list.append(movement)
    movement_in_group = 0
    for group in self.group_list :
      if group.test(movement) :
        group.append(movement)
        movement_in_group = 1
        break
    if movement_in_group == 0 :
      self.appendGroup(movement)

class OrderMovementGroup(RootMovementGroup):

  meta_type = 'ERP5 Order Movement Group'
  portal_type = 'Order Movement Group'

  def __init__(self,movement):
    RootMovementGroup.__init__(self,movement)
    if hasattr(movement, 'getRootAppliedRule'):
      # This is a simulation movement
      order_value = movement.getRootAppliedRule().getCausalityValue(
                                                portal_type=order_type_list)
      if order_value is None:
        # In some cases (ex. DeliveryRule), there is no order
        # we may consider a PackingList as the order in the OrderGroup
        order_value = movement.getRootAppliedRule().getCausalityValue(
                        portal_type=delivery_type_list)
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

  def test(self,movement):
    if hasattr(movement, 'getRootAppliedRule'):
      order_value = movement.getRootAppliedRule().getCausalityValue(
                                                  portal_type=order_type_list)

      if order_value is None:
        # In some cases (ex. DeliveryRule), there is no order
        # we may consider a PackingList as the order in the OrderGroup
        order_value = movement.getRootAppliedRule().getCausalityValue(
                        portal_type=delivery_type_list)
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

class PathMovementGroup(RootMovementGroup):

  meta_type = 'ERP5 Path Movement Group'
  portal_type = 'Path Movement Group'

  def __init__(self,movement):
    RootMovementGroup.__init__(self,movement)
    self.source = movement.getSource()
    LOG('PathGroup.__init__ source',0,self.source)
    self.destination = movement.getDestination()
    LOG('PathGroup.__init__ destination',0,self.destination)
    self.source_section = movement.getSourceSection()
    LOG('PathGroup.__init__ source_section',0,self.source_section)
    self.destination_section = movement.getDestinationSection()
    LOG('PathGroup.__init__ destination_section',0,self.destination_section)
    self.target_source = movement.getTargetSource()
    LOG('PathGroup.__init__ target_source',0,self.target_source)
    self.target_destination = movement.getTargetDestination()
    LOG('PathGroup.__init__ target_destination',0,self.target_destination)
    self.target_source_section = movement.getTargetSourceSection()
    LOG('PathGroup.__init__ target_source_section',0,self.target_source_section)
    self.target_destination_section = movement.getTargetDestinationSection()
    LOG('PathGroup.__init__ target_destination_section',0,self.target_destination_section)


  def test(self,movement):
    if movement.getSource() == self.source and \
      movement.getDestination() == self.destination and \
      movement.getSourceSection() == self.source_section and \
      movement.getDestinationSection() == self.destination_section and \
      movement.getTargetSource() == self.target_source and \
      movement.getTargetDestination() == self.target_destination and \
      movement.getTargetSourceSection() == self.target_source_section and \
      movement.getTargetDestinationSection() == self.target_destination_section :

      return 1
    else :
      return 0

class DateMovementGroup(RootMovementGroup):

  meta_type = 'ERP5 Date Movement Group'
  portal_type = 'Date Movement Group'

  def __init__(self,movement):
    RootMovementGroup.__init__(self,movement)
    self.target_start_date = movement.getTargetStartDate()
    self.target_stop_date = movement.getTargetStopDate()
    self.start_date = movement.getStartDate()
    self.stop_date = movement.getStopDate()

  def test(self,movement):
    if movement.getStartDate() == self.start_date and \
      movement.getStopDate() == self.stop_date :
      return 1
    else :
      return 0

class CriterionMovementGroup(RootMovementGroup):

  meta_type = 'ERP5 Criterion Movement Group'
  portal_type = 'Criterion Movement Group'

  def __init__(self,movement):
    RootMovementGroup.__init__(self,movement)
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

class ResourceMovementGroup(RootMovementGroup):

  meta_type = 'ERP5 Resource Movement Group'
  portal_type = 'Resource Movement Group'

  def __init__(self,movement):
    RootMovementGroup.__init__(self,movement)
    self.resource = movement.getResource()

  def test(self,movement):
    if movement.getResource() == self.resource :
      return 1
    else :
      return 0

class BaseVariantMovementGroup(RootMovementGroup):

  meta_type = 'ERP5 Base Variant Movement Group'
  portal_type = 'Base Variant Movement Group'

  def __init__(self,movement):
    RootMovementGroup.__init__(self,movement)
    self.base_category_list = movement.getVariationBaseCategoryList()
    if self.base_category_list is None:
      LOG('BaseVariantGroup __init__', 0, 'movement = %s, movement.showDict() = %s' % (repr(movement), repr(movement.showDict())))
      self.base_category_list = []

  def test(self,movement):
    # we must have the same number of categories
    categories_identity = 0
    #LOG('BaseVariantGroup', 0, 'self.base_category_list = %s, movement = %s, movement.getVariationBaseCategoryList() = %s' % (repr(self.base_category_list), repr(movement), repr(movement.getVariationBaseCategoryList())))
    movement_base_category_list = movement.getVariationBaseCategoryList()
    if movement_base_category_list is None:
      LOG('BaseVariantGroup test', 0, 'movement = %s, movement.showDict() = %s' % (repr(movement), repr(movement.showDict())))
      movement_base_category_list = []
    if len(self.base_category_list) == len(movement_base_category_list):
      for category in movement_base_category_list:
        if not category in self.base_category_list :
          break
      else :
        categories_identity = 1
    return categories_identity

class VariantMovementGroup(RootMovementGroup):

  meta_type = 'ERP5 Variant Movement Group'
  portal_type = 'Variant Movement Group'

  def __init__(self,movement):
    RootMovementGroup.__init__(self,movement)
    self.category_list = movement.getVariationCategoryList()
    if self.category_list is None:
      LOG('VariantGroup __init__', 0, 'movement = %s, movement.showDict() = %s' % (repr(movement), repr(movement.showDict())))
      self.category_list = []

  def test(self,movement):
    # we must have the same number of categories
    categories_identity = 0
    movement_category_list = movement.getVariationCategoryList()
    if movement_category_list is None:
      LOG('VariantGroup test', 0, 'movement = %s, movement.showDict() = %s' % (repr(movement), repr(movement.showDict())))
      movement_category_list = []
    if len(self.category_list) == len(movement_category_list):
      for category in movement_category_list:
        if not category in self.category_list :
          break
      else :
        categories_identity = 1
    return categories_identity
