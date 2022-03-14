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
from Products.ERP5Type.Accessor.TypeDefinition import list_types
from erp5.component.interface.IMovementCollectionDiff import IMovementCollectionDiff

@zope.interface.implementer(IMovementCollectionDiff,)
class MovementCollectionDiff(object):
  """
  Documents which implement IMovementCollectionDiff
  are used to represent the movements which should be
  added, updated or deleted in an IMovementCollection.
  They are usually generated and used by
  IMovementCollectionUpdater.
  """

  def __init__(self):
    self._deletable_movement_list = []
    self._new_movement_list = []
    self._updatable_movement_list = []

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
    Returns movements which need to be updated, with properties to update
    """
    return self._updatable_movement_list

  def addUpdatableMovement(self, movement, property_dict):
    """
    Add an updatable movement to the diff definition

    property_dict -- properties to update
    """
    self._updatable_movement_list.append((movement, property_dict))

def _getPropertyAndCategoryList(document):
  """
  Returns a dict that includes all property values, based on property
  sheet configuration and all category values.
  """
  property_dict = {}
  property_dict.update(_getPropertyList(document))
  property_dict.update(_getCategoryList(document))
  return property_dict

getPropertyAndCategoryList = _getPropertyAndCategoryList

def _getPropertyList(document, acquire=True):
  property_map = document.getPropertyMap()
  bad_property_list = ['id', 'uid', 'categories_list', 'last_id',]
  document_dict = document.__dict__
  property_dict = {}
  getPropertyList = document.getPropertyList
  getProperty = document.getProperty
  for x in property_map:
    property_id = x['id']
    if property_id in bad_property_list:
      continue
    # we care already stored property only
    elif (x.get('storage_id') or property_id) not in document_dict:
      continue
    # we don't want acquired properties without acquisition_mask_value
    elif x.has_key('acquisition_base_category') and not x.get('acquisition_mask_value', 0):
      continue
    elif x['type'] in list_types and not property_id.endswith('_list'):
      property_dict[property_id] = getPropertyList(property_id)
    else:
      property_dict[property_id] = getProperty(property_id)
  return property_dict

def _getCategoryList(document, acquire=True):
  # we care already stored category only
  document_category_set = {x.split('/',1)[0]
                           for x in document.getCategoryList()}
  getPropertyList = document.getPropertyList
  return {x: getPropertyList(x) for x in document_category_set if x != 'solver'}

from AccessControl.SecurityInfo import allow_module
allow_module(__name__)
