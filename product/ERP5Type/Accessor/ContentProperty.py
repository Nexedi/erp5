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
from .Base import func_code, type_definition, ATTRIBUTE_PREFIX, Method
from . import Base
from Products.ERP5Type.PsycoWrapper import psyco

Setter = Base.Setter
DefaultSetter = Base.Setter
ValueSetter = Base.Setter
DefaultValueSetter = Base.Setter

from zLOG import LOG

class ValueGetter(Base.Getter):
    """
      Gets an attribute value. A default value can be
      provided if needed
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    __code__ = func_code = func_code()
    __code__.co_varnames = ('self',)
    __code__.co_argcount = 1
    __defaults__ = func_defaults = ()

    def __init__(self, id, key, property_type, acquired_property,
                 portal_type=None, storage_id=None, default=None):
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      self._null = type_definition[property_type]['null']
      self._default = default
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      elif type(storage_id) not in (type([]), type(())):
        storage_id = [storage_id]
      self._storage_id_list = storage_id
      if type(portal_type) is type('a'):
        portal_type = (portal_type,)
      self._portal_type = portal_type
      self._acquired_property = acquired_property

    def __call__(self, instance, *args, **kw):
      # We return the first available object in the list
      for k in self._storage_id_list:
        o = getattr(instance, k, None)
        if o is not None and (o.portal_type is None or
                              o.portal_type in self._portal_type):
          return o
      return args[0] if args else self._default

    psyco.bind(__call__)

class ValueListGetter(Base.Getter):
    """
      Gets an attribute value. A default value can be
      provided if needed
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    __code__ = func_code = func_code()
    __code__.co_varnames = ('self',)
    __code__.co_argcount = 1
    __defaults__ = func_defaults = ()

    def __init__(self, id, key, property_type, acquired_property,
                 portal_type=None, storage_id=None, default=None):
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      self._null = type_definition[property_type]['null']
      self._default = default
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      elif type(storage_id) is not type([]):
        storage_id = [storage_id]
      self._storage_id_list = storage_id
      self._portal_type = portal_type
      self._acquired_property = acquired_property

    def __call__(self, instance, *args, **kw):
      # We return the list of matching objects
      return [o.getObject() for o in self.contentValues(
          {'portal_type': self._portal_type, 'id': self._storage_id_list})]

    psyco.bind(__call__)

DefaultValueGetter = ValueGetter

class Getter(Base.Getter):
    """
      Gets an attribute value. A default value can be
      provided if needed
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    __code__ = func_code = func_code()
    __code__.co_varnames = ('self', 'args', 'kw')
    __code__.co_argcount = 1
    __defaults__ = func_defaults = ()

    def __init__(self, id, key, property_type, acquired_property,
                 portal_type=None, storage_id=None, default=None):
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      self._null = type_definition[property_type]['null']
      self._default = default
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      elif type(storage_id) is not type([]):
        storage_id = [storage_id]
      self._storage_id_list = storage_id
      if type(portal_type) is type('a'):
        portal_type = (portal_type,)
      self._portal_type = portal_type
      self._acquired_property = acquired_property

    def __call__(self, instance, *args, **kw):
      # We return the first available object in the list
      o = None
      for k in self._storage_id_list:
        o = getattr(instance, k, None)
        if o is not None and o.portal_type in self._portal_type:
          return o.getProperty(self._acquired_property, *args, **kw)
      return args[0] if args else self._default

    psyco.bind(__call__)

class Setter(Base.Setter):
    """
      Gets an attribute value. A default value can be
      provided if needed
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    __code__ = func_code = func_code()
    __code__.co_varnames = ('self', 'value', 'args', 'kw')
    __code__.co_argcount = 2
    __defaults__ = func_defaults = ()

    def __init__(self, id, key, property_type, acquired_property,
                 portal_type=None, storage_id=None):
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      self._null = type_definition[property_type]['null']
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      elif type(storage_id) is not type([]):
        storage_id = [storage_id]
      self._storage_id_list = storage_id
      if type(portal_type) is type('a'):
        portal_type = (portal_type,)
      self._portal_type = portal_type
      self._acquired_property = acquired_property

    def __call__(self, instance, value, *args, **kw):
      # We return the first available object in the list
      o = None
      available_id = None
      modified_object_list = ()
      for k in self._storage_id_list:
        o = instance._getOb(k, None)
        if o is None: available_id = k
        if o is not None and o.portal_type in self._portal_type:
          o._setProperty(self._acquired_property, value, *args, **kw)
          modified_object_list = (o, )
      if o is None and available_id is not None:
        from Products.ERP5Type.Utils import assertAttributePortalType
        assertAttributePortalType(instance, available_id, self._portal_type)
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
        o = instance.newContent(id=available_id,
                                portal_type=self._portal_type[0])
        o._setProperty(self._acquired_property, value, *args, **kw)
        modified_object_list = (o, )
      return modified_object_list

class ListGetter(Base.Getter):
    """
      Gets an attribute value. A default value can be
      provided if needed
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    __code__ = func_code = func_code()
    __code__.co_varnames = ('self',)
    __code__.co_argcount = 1
    __defaults__ = func_defaults = ()

    def __init__(self, id, key, property_type, acquired_property,
                 portal_type=None, storage_id=None):
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      self._null = type_definition[property_type]['null']
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      elif type(storage_id) is not type([]):
        storage_id = [storage_id]
      self._storage_id_list = storage_id
      self._portal_type = portal_type
      self._acquired_property = acquired_property

    def __call__(self, instance, *args, **kw):
      # We return the list of matching objects
      return [o.relative_url for o in self.searchFolder(
                                    portal_type=self._portal_type,
                                    id=self._storage_id_list)]

    psyco.bind(__call__)

DefaultGetter = Getter

class Tester(Base.Tester):
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

    def __init__(self, id, key, property_type, acquired_property,
                 portal_type=None, storage_id=None):
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      self._null = type_definition[property_type]['null']
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      elif type(storage_id) is not list:
        storage_id = [storage_id]
      self._storage_id_list = storage_id
      if type(portal_type) is str:
        portal_type = (portal_type,)
      self._portal_type = portal_type
      self._acquired_property = acquired_property

    def __call__(self, instance, *args, **kw):
      o = None
      for k in self._storage_id_list:
        o = getattr(instance, k, None)
        if o is not None and o.portal_type in self._portal_type:
          return o.hasProperty(self._acquired_property)
      return False

