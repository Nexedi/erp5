##############################################################################
#
# Copyright (c) 2002-2003 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Base import func_code, type_definition, list_types, ATTRIBUTE_PREFIX, Method

class DefaultGetter(Method):
    """
      Gets the default reference of a relation
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self,  id, key, property_type, default_value,
                        acquisition_base_category,
                        acquisition_portal_type,
                        acquisition_accessor_id,
                        acquisition_copy_value,
                        acquisition_mask_value,
                        acquisition_sync_value,
                        storage_id=None,
                        alt_accessor_id = None,
                        is_list_type = 0
                  ):
      self._id = id
      self.__name__ = id
      self._key = key
      self._type = property_type
      self._null = type_definition[property_type]['null']
      self._default = default_value
      self._acquisition_base_category = acquisition_base_category
      self._acquisition_portal_type = acquisition_portal_type
      self._acquisition_accessor_id = acquisition_accessor_id
      self._acquisition_copy_value = acquisition_copy_value
      self._acquisition_mask_value = acquisition_mask_value
      self._acquisition_sync_value = acquisition_sync_value
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      self._storage_id = storage_id
      self._alt_accessor_id = alt_accessor_id
      self._is_list_type = is_list_type

    def __call__(self, instance, *args, **kw):
      if len(args) > 0:
        default = args[0]
      else:
        default = self._default
      return instance._getDefaultAcquiredProperty(self._key, default, self._null,
            base_category=self._acquisition_base_category,
            portal_type=self._acquisition_portal_type,
            accessor_id=self._acquisition_accessor_id,
            copy_value=self._acquisition_copy_value,
            mask_value=self._acquisition_mask_value,
            sync_value=self._acquisition_sync_value,
            storage_id=self._storage_id,
            alt_accessor_id=self._alt_accessor_id,
            is_list_type=self._is_list_type
            )

Getter = DefaultGetter

class ListGetter(Method):
    """
      Gets an attribute value
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self,  id, key, property_type, default_value,
                        acquisition_base_category,
                        acquisition_portal_type,
                        acquisition_accessor_id,
                        acquisition_copy_value,
                        acquisition_mask_value,
                        acquisition_sync_value,
                        storage_id=None,
                        alt_accessor_id = None,
                        is_list_type = 0
                  ):
      self._id = id
      self.__name__ = id
      self._key = key
      self._type = property_type
      self._null = type_definition[property_type]['null']
      self._default = default_value
      self._acquisition_base_category = acquisition_base_category
      self._acquisition_portal_type = acquisition_portal_type
      self._acquisition_accessor_id = acquisition_accessor_id
      self._acquisition_copy_value = acquisition_copy_value
      self._acquisition_mask_value = acquisition_mask_value
      self._acquisition_sync_value = acquisition_sync_value
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      self._storage_id = storage_id
      self._alt_accessor_id = alt_accessor_id
      self._is_list_type = is_list_type

    def __call__(self, instance, *args, **kw):
      if len(args) > 0:
        default = args[0]
      else:
        default = self._default
      return instance._getAcquiredPropertyList(self._key, default, self._null,
            base_category=self._acquisition_base_category,
            portal_type=self._acquisition_portal_type,
            accessor_id=self._acquisition_accessor_id,
            copy_value=self._acquisition_copy_value,
            mask_value=self._acquisition_mask_value,
            sync_value=self._acquisition_sync_value,
            storage_id=self._storage_id,
            alt_accessor_id=self._alt_accessor_id,
            is_list_type=self._is_list_type)

SetGetter = ListGetter # ERROR
