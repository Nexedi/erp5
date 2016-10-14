##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5.Document.PropertyMovementGroup import PropertyMovementGroup
from Products.ERP5Type.Utils import UpperCase

class ParentDeliveryPropertyMovementGroup(PropertyMovementGroup):
  """
  Parent Delivery Property Movement Group is similar to Property
  Movement Group, but it does grouping only by specified category values
  on its parent simulation movement's delivery value and do not update
  documents.

  This is useful for acquired properties like payment_condition_*.
  """
  meta_type = 'ERP5 Parent Delivery Property Movement Group'
  portal_type = 'Parent Delivery Property Movement Group'

  def _getPropertyDict(self, movement, **kw):
    property_dict = {}
    parent_delivery = self._getParentDelivery(movement)
    if parent_delivery is not None:
      for prop in self.getTestedPropertyList():
        property_dict['_%s' % prop] = self._getPropertyFromDocument(parent_delivery, prop)
    return property_dict

  def test(self, document, property_dict, property_list=None, **kw):
    if property_list not in (None, []):
      target_property_list = [x for x in self.getTestedPropertyList() \
                              if x in property_list]
    else:
      target_property_list = self.getTestedPropertyList()
    if document == document.getDeliveryValue():
      # XXX what is the expected behaviour of this movement group in
      # delivery level?
      pass
    else:
      movement = document.getDeliveryRelatedValue()
      if movement is None:
        return False, {}
      document = self._getParentDelivery(movement)
    for prop in target_property_list:
      if property_dict['_%s' % prop] != self._getPropertyFromDocument(document, prop):
        return False, {}
    return True, {}

  def _getParentDelivery(self, movement):
    # try to find local payment conditions from the upper level delivery
    rule = movement.getParentValue()
    delivery = None
    while delivery is None and not(rule.isRootAppliedRule()):
      rule = movement.getParentValue()
      movement = rule.getParentValue()
      delivery = movement.getDeliveryValue()
    return delivery

  def _getPropertyFromDocument(self, document, property_id):
    if document is None:
      return None
    # XXX here we don't use Base.getProperty() but try to call accessor
    # directly to make acquired property
    # (eg. payment_condition_efficiency) working.
    accessor_name = 'get' + UpperCase(property_id)
    return getattr(document, accessor_name)()
