# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import zope.interface
from Products.ERP5Type import interfaces
from Products.ERP5Type.Accessor.TypeDefinition import list_types

class MovementCollectionDiff(object):
  """
  Documents which implement IMovementCollectionDiff
  are used to represent the movements which should be
  added, updated or deleted in an IMovementCollection.
  They are usually generated and used by
  IMovementCollectionUpdater.
  """
  # Declarative interfaces
  zope.interface.implements(interfaces.IMovementCollectionDiff,)

  def __init__(self):
    self._deletable_movement_list = []
    self._new_movement_list = []
    self._updatable_movement_list = []
    self._property_dict_dict = {}

  def getDeletableMovementList(self):
    """
    Returns the list of movements which need
    to be deleted.
    """
    return self._deletable_movement_list

  def addDeletableMovement(self, movement):
    """
    Add a deletable movement to the diff definition
    """
    self._deletable_movement_list.append(movement)

  def getNewMovementList(self):
    """
    Returns a list temp movements which represent new
    movements to add to an existing IMovementCollection.
    """
    return self._new_movement_list

  def addNewMovement(self, movement):
    """
    Add a new movement to the diff definition
    """
    self._new_movement_list.append(movement)

  def getUpdatableMovementList(self):
    """
    Returns the list of movements which need
    to be updated.
    """
    return self._updatable_movement_list

  def getMovementPropertyDict(self, movement):
    """
    Returns a dict of all properties and values
    to update an existing movement or to
    create a new movement.
    """
    # for updatable movement, property_dict is already calculated.
    property_dict = self._property_dict_dict.get(movement)
    # for new movement, property_dict should be calculated here.
    if property_dict is None:
      property_dict = _getPropertyList(movement)
      property_dict.update(_getCategoryList(movement, acquire=False))
      return property_dict
    else:
      return property_dict

  def addUpdatableMovement(self, movement, property_dict):
    """
    Add an updatable movement to the diff definition

    property_dict -- properties to update
    """
    self._updatable_movement_list.append(movement)
    self._property_dict_dict[movement] = property_dict

def _getPropertyAndCategoryList(document):
  """
  Returns a dict that includes all property values, based on property
  sheet configuration and all category values.
  """
  property_dict = {}
  property_dict.update(_getPropertyList(document))
  property_dict.update(_getCategoryList(document))
  return property_dict

def _getPropertyList(document, acquire=True):
  property_map = document.getPropertyMap()
  bad_property_list = ['id', 'uid', 'categories_list', 'last_id',]
  # we don't want acquired properties without acquisition_mask_value
  for x in property_map:
    if x.has_key('acquisition_base_category') and not x.get('acquisition_mask_value', 0):
      bad_property_list.append(x['id'])

  default_value_dict = dict([(x['id'], x.get('default', None)) \
                             for x in property_map])
  getPropertyList = document.getPropertyList
  getProperty = document.getProperty
  getter_list_type_dict = {
    True:getPropertyList,
    False:getProperty
    }
  getter_dict = dict([(x['id'],
                       getter_list_type_dict[x['type'] in list_types and not x['id'].endswith('_list')]) \
                      for x in property_map])

  def filter_property_func(x):
    key, value = x
    if key in bad_property_list:
      return False
    default = default_value_dict[key]
    if value == default:
      return False
    if not acquire and not document.hasProperty(key):
      return False
    if isinstance(value, (list, tuple)) and \
         isinstance(default, (list, tuple)) and \
         tuple(value) == tuple(default):
      return False
    return True

  return dict(filter(filter_property_func,
                     [(x, getter_dict[x](x)) for x in \
                      document.getPropertyIdList()]))

def _getCategoryList(document, acquire=True):
  bad_category_list = ['solver', ]
  getPropertyList = document.getPropertyList
  def filter_category_func(x):
    return len(x[1]) != 0 and x[0] not in bad_category_list and \
           (acquire or document.hasProperty(x[0]))

  return dict(filter(filter_category_func,
                     [(x, getPropertyList(x)) for x in \
                      document.getBaseCategoryList()]))
    
