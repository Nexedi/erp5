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


from Base import func_code, type_definition, list_types,\
                 ATTRIBUTE_PREFIX, Method, evaluateTales
from TypeDefinition import asList, identity
import Base
from Products.ERP5Type.PsycoWrapper import psyco
from Acquisition import aq_base
from types import ListType, TupleType

from zLOG import LOG

class DefaultSetter(Base.Setter):
    """
      Sets the default attribute in a list
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    # More information at http://www.zope.org/Members/htrd/howto/FunctionTemplate
    func_code = func_code()
    func_code.co_varnames = ('self','value')
    func_code.co_argcount = 2
    func_defaults = ()

    def __init__(self, id, key, property_type, storage_id=None):
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      if property_type in list_types: # classic list
        self._cast = type_definition[property_type]['cast']
        self._item_cast = identity
      else: # Multivalued
        self._cast = asList
        self._item_cast = type_definition[property_type]['cast']
      self._null = type_definition[property_type]['null']
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      self._storage_id = storage_id
      self._is_tales_type = (property_type == 'tales')

    def __call__(self, instance, *args, **kw):
      # Turn the value into a list
      value = args[0]
      # Modify the property
      if self._is_tales_type:
        setattr(instance, self._storage_id, str(value))
      elif value in self._null:
        # The value has no default property -> it is empty
        setattr(instance, self._storage_id, ())
      else:
        if self._item_cast is not identity:
          value = self._item_cast(value)
        list_value = set(getattr(instance, self._storage_id, ()))
        list_value.discard(value)
        setattr(instance, self._storage_id, (value,) + tuple(list_value))

class ListSetter(DefaultSetter):

    def __call__(self, instance, *args, **kw):
      value = args[0]
      # Modify the property
      if value in self._null:
        setattr(instance, self._storage_id, ())
      elif self._is_tales_type:
        setattr(instance, self._storage_id, str(value))
      else:
        value = self._cast(args[0])
        if self._item_cast is not identity:
          value = map(self._item_cast, value)
        setattr(instance, self._storage_id, tuple(value))

Setter = ListSetter

class SetSetter(Base.Setter):
    """
      Sets the default attribute in a list
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    # More information at http://www.zope.org/Members/htrd/howto/FunctionTemplate
    func_code = func_code()
    func_code.co_varnames = ('self','value')
    func_code.co_argcount = 2
    func_defaults = ()

    def __init__(self, id, key, property_type, storage_id=None):
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      if property_type in list_types: # classic list
        self._cast = type_definition[property_type]['cast']
        self._item_cast = identity
      else: # Multivalued
        self._cast = asList
        self._item_cast = type_definition[property_type]['cast']
      self._null = type_definition[property_type]['null']
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      self._storage_id = storage_id
      self._is_tales_type = (property_type == 'tales')

    def __call__(self, instance, *args, **kw):
      # Turn the value into a list
      value = args[0]
      # Modify the property
      if self._is_tales_type:
        setattr(instance, self._storage_id, str(value))
      elif value in self._null:
        setattr(instance, self._storage_id, ())
      else:
        value = self._cast(value)
        if self._item_cast is not identity:
          value = map(self._item_cast, value)
        if value:
          value = set(value)
          list_value = getattr(instance, self._storage_id, None)
          if list_value:
            default_value = list_value[0]
            if default_value in value:
              # If we change the set, 
              # the default value must be in the new set
              value.remove(default_value)
              value = (default_value,) + tuple(value)
        setattr(instance, self._storage_id, tuple(value))
      return (instance, )

class DefaultGetter(Base.Getter):
    """
      Gets the first item of a list
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key, property_type, default=None, storage_id=None):
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      self._null = type_definition[property_type]['null']
      self._default = default
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      self._storage_id = storage_id
      self._is_tales_type = (property_type == 'tales')

    def __call__(self, instance, *args, **kw):
      if len(args) > 0:
        default = args[0]
      else:
        default = self._default
      list_value = getattr(aq_base(instance), self._storage_id, default)
      if list_value is not None:
        if self._is_tales_type:
          if kw.get('evaluate', 1):
            list_value = evaluateTales(instance=instance, value=list_value)
          else:
            return list_value
        if type(list_value) in (ListType, TupleType):
          if len(list_value) > 0:
            return list_value[0]
          else:
            return None
        # This should not happen though
        return list_value
      if default and len(default):
        return default[0]
      return None

    psyco.bind(__call__)

Getter = DefaultGetter

class ListGetter(Base.Getter):
    """
      Gets an attribute value. A default value can be
      provided if needed
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key, property_type, default=None, storage_id=None):
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      self._null = type_definition[property_type]['null']
      self._default = default
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      self._storage_id = storage_id
      self._is_tales_type = (property_type == 'tales')

    def __call__(self, instance, *args, **kw):
      if len(args) > 0:
        default = args[0]
      else:
        default = self._default
      list_value = getattr(aq_base(instance), self._storage_id, default)
      # We should not use here self._null but None instead XXX
      if list_value not in self._null:
        if self._is_tales_type:
          if kw.get('evaluate', 1):
            if type(list_value) != type(''):
              LOG('ListGetter', 0, 'instance = %r, self._storage_id = %r, list_value = %r' % (instance, self._storage_id, list_value,)) # If we reach this point, something strange is going on
            list_value = evaluateTales(instance=instance, value=list_value)
          else:
            return list_value
        if type(list_value) is TupleType:
          return list(list_value) # Make sure we return a list rather than a tuple
        return list_value
      if default is None:
        return None # nothing was defined as default so None is the appropriate value
      if type(default) is TupleType:
        return list(default) # Make sure we return a list rather than a tuple
      return default

    psyco.bind(__call__)

class SetGetter(ListGetter):
    """
      Gets an attribute value. A default value can be
      provided if needed
    """

    def __call__(self, instance, *args, **kw):
      result_list = ListGetter.__call__(self, instance, *args, **kw)
      if result_list is not None:
        return list(set(result_list))

Tester = Base.Tester
