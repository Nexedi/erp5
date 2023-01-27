from __future__ import absolute_import
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

from Acquisition import aq_base
from ZPublisher.HTTPRequest import FileUpload
from .Base import func_code, type_definition, list_types, ATTRIBUTE_PREFIX, Getter as BaseGetter, Setter as BaseSetter, Tester as BaseTester
from Products.ERP5Type.PsycoWrapper import psyco
from zLOG import LOG

class Getter(BaseGetter):
    """
      Gets the default reference of a relation
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    __code__ = func_code = func_code()
    __code__.co_varnames = ('self', 'args', 'kw')
    __code__.co_argcount = 1
    __defaults__ = func_defaults = None

    def __init__(self,  id, key, property_type, portal_type, acquired_property,
                        acquisition_base_category,
                        acquisition_portal_type,
                        acquisition_accessor_id,
                        acquisition_copy_value,
                        acquisition_mask_value,
                        storage_id=None,
                        alt_accessor_id = None,
                        acquisition_object_id=None,
                        is_list_type = 0,
                        is_tales_type = 0
                  ):
      if type(portal_type) == type('a'): portal_type = (portal_type, )
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      self._portal_type = portal_type
      self._null = type_definition[property_type]['null']

      # These values are hashed by _get*AcquiredProperty: to be
      # hashable, they need to be converted to tuples
      if isinstance(acquisition_base_category, list):
        acquisition_base_category = tuple(acquisition_base_category)
      if isinstance(acquisition_portal_type, list):
        acquisition_portal_type = tuple(acquisition_portal_type)
      if isinstance(acquisition_object_id, list):
        acquisition_object_id = tuple(acquisition_object_id)
      if isinstance(alt_accessor_id, list):
        alt_accessor_id = tuple(alt_accessor_id)

      self._acquisition_base_category = acquisition_base_category
      self._acquisition_portal_type = acquisition_portal_type
      self._acquisition_accessor_id = acquisition_accessor_id
      self._acquisition_copy_value = acquisition_copy_value
      self._acquisition_mask_value = acquisition_mask_value
      self._acquired_property = acquired_property
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      self._storage_id = storage_id
      self._alt_accessor_id = alt_accessor_id
      self._acquisition_object_id = acquisition_object_id
      self._is_list_type = is_list_type
      self._is_tales_type = is_tales_type

    def __call__(self, instance, *args, **kw):
      if len(args) > 0:
        default = args[0]
      else:
        default = None
      value = instance._getDefaultAcquiredProperty(self._key, None, self._null,
            base_category=self._acquisition_base_category,
            portal_type=self._acquisition_portal_type,
            accessor_id=self._acquisition_accessor_id,
            copy_value=self._acquisition_copy_value,
            mask_value=self._acquisition_mask_value,
            storage_id=self._storage_id,
            alt_accessor_id=self._alt_accessor_id,
            acquisition_object_id=self._acquisition_object_id,
            is_list_type=self._is_list_type,
            is_tales_type=self._is_tales_type,
            checked_permission=kw.get('checked_permission', None)
            )
      if value is not None:
        return value.getProperty(self._acquired_property, default, **kw)
      else:
        return default

    psyco.bind(__call__)

DefaultGetter = Getter

class Setter(BaseSetter):
    """
      Sets a value of a property wich can be acquired.
      Since we set here the property, we must not call acquisition.
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    __code__ = func_code = func_code()
    __code__.co_varnames = ('self', 'value', 'args', 'kw')
    __code__.co_argcount = 2
    __defaults__ = func_defaults = None

    def __init__(self,  id, key, property_type, portal_type, acquired_property,
                        acquisition_base_category,
                        acquisition_portal_type,
                        acquisition_accessor_id,
                        acquisition_copy_value,
                        acquisition_mask_value,
                        storage_id=None,
                        alt_accessor_id = None,
                        acquisition_object_id = None,
                        is_list_type = 0,
                        is_tales_type = 0,
                  ):
      if type(portal_type) == type('a'): portal_type = (portal_type, )
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      self._portal_type = portal_type
      self._null = type_definition[property_type]['null']

      # These values are hashed by _get*AcquiredProperty: to be
      # hashable, they need to be converted to tuples
      if isinstance(acquisition_base_category, list):
        acquisition_base_category = tuple(acquisition_base_category)
      if isinstance(acquisition_portal_type, list):
        acquisition_portal_type = tuple(acquisition_portal_type)
      if isinstance(acquisition_object_id, list):
        acquisition_object_id = tuple(acquisition_object_id)
      if isinstance(alt_accessor_id, list):
        alt_accessor_id = tuple(alt_accessor_id)

      self._acquisition_base_category = acquisition_base_category
      self._acquisition_portal_type = acquisition_portal_type
      self._acquisition_accessor_id = acquisition_accessor_id
      self._acquisition_copy_value = acquisition_copy_value
      self._acquisition_mask_value = acquisition_mask_value
      self._acquired_property = acquired_property
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      self._storage_id = storage_id
      self._alt_accessor_id = alt_accessor_id
      self._acquisition_object_id = acquisition_object_id
      self._is_list_type = is_list_type
      self._is_tales_type = is_tales_type

    def __call__(self, instance, value, *args, **kw):
      from Products.ERP5Type.Utils import assertAttributePortalType
      assertAttributePortalType(instance, self._storage_id, self._portal_type)
      o = instance._getOb(self._storage_id, None)
      if o is None:
        if self._acquired_property == 'file':
          if isinstance(value, FileUpload) or \
                getattr(aq_base(value), 'tell', None) is not None:
            # When editing through the web interface, we are always provided a
            # FileUpload, and when no file has been specified, the file is empty.
            # In the case of empty file, we should not create the sub document.
            value.seek(0, 2)
            is_empty_file = not value.tell()
            value.seek(0)
            if is_empty_file:
              return ()

        o = instance.newContent(id=self._storage_id,
            portal_type=self._portal_type[0])
      o._setProperty(self._acquired_property, value, *args, **kw)
      return (o, )

DefaultSetter = Setter

class Tester(BaseTester):
    """
      Tests if an attribute value exists
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    __code__ = func_code = func_code()
    __code__.co_varnames = ('self',)
    __code__.co_argcount = 1
    __defaults__ = func_defaults = ()

    def __init__(self,  id, key, property_type, portal_type, acquired_property,
                        acquisition_base_category,
                        acquisition_portal_type,
                        acquisition_accessor_id,
                        acquisition_copy_value,
                        acquisition_mask_value,
                        storage_id=None,
                        alt_accessor_id = None,
                        acquisition_object_id=None,
                        is_list_type = 0,
                        is_tales_type = 0
                  ):
      if type(portal_type) == type('a'): portal_type = (portal_type, )
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      self._portal_type = portal_type
      self._null = type_definition[property_type]['null']

      # These values are hashed by _get*AcquiredProperty: to be
      # hashable, they need to be converted to tuples
      if isinstance(acquisition_base_category, list):
        acquisition_base_category = tuple(acquisition_base_category)
      if isinstance(acquisition_portal_type, list):
        acquisition_portal_type = tuple(acquisition_portal_type)
      if isinstance(acquisition_object_id, list):
        acquisition_object_id = tuple(acquisition_object_id)
      if isinstance(alt_accessor_id, list):
        alt_accessor_id = tuple(alt_accessor_id)

      self._acquisition_base_category = acquisition_base_category
      self._acquisition_portal_type = acquisition_portal_type
      self._acquisition_accessor_id = acquisition_accessor_id
      self._acquisition_copy_value = acquisition_copy_value
      self._acquisition_mask_value = acquisition_mask_value
      self._acquired_property = acquired_property
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      self._storage_id = storage_id
      self._alt_accessor_id = alt_accessor_id
      self._acquisition_object_id = acquisition_object_id
      self._is_list_type = is_list_type
      self._is_tales_type = is_tales_type

    def __call__(self, instance, *args, **kw):
      if self._storage_id:
        # If this property is supposed to be stored as a content subobject,
        # then we consider that if the subobject does not exist then the
        # property is not set, even if it is acquired from another document.
        o = instance._getOb(self._storage_id, None)
        if o is None:
          return False
      value = instance._getDefaultAcquiredProperty(self._key, None, self._null,
            base_category=self._acquisition_base_category,
            portal_type=self._acquisition_portal_type,
            accessor_id=self._acquisition_accessor_id,
            copy_value=self._acquisition_copy_value,
            mask_value=self._acquisition_mask_value,
            storage_id=self._storage_id,
            alt_accessor_id=self._alt_accessor_id,
            acquisition_object_id=self._acquisition_object_id,
            is_list_type=self._is_list_type,
            is_tales_type=self._is_tales_type,
            checked_permission=kw.get('checked_permission', None)
            )
      if value is not None:
        return value.hasProperty(self._acquired_property)
      return False

