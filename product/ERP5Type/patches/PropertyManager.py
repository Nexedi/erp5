##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# Properties
from OFS.PropertyManager import PropertyManager, type_converters
from OFS.PropertyManager import escape
from Products.ERP5Type.Globals import DTMLFile
from Products.ERP5Type.Utils import createExpressionContext
from Products.CMFCore.Expression import Expression
from Products.ERP5Type import _dtmldir
from Acquisition import aq_base
from zExceptions import BadRequest
from DateTime import DateTime

class ERP5PropertyManager(PropertyManager):
  """
    This class is only for backward compatibility.
  """
  pass

PropertyManager_manage_propertiesForm=DTMLFile('properties',
                                               _dtmldir,
                                               property_extensible_schema__=1)


def PropertyManager_updateProperty(self, id, value, local_properties=False):
    # Update the value of an existing property. If value
    # is a string, an attempt will be made to convert
    # the value to the type of the existing property.
    self._wrapperCheck(value)
    if not hasattr(self, 'isRADContent'):
      if not self.hasProperty(id):
          raise BadRequest, 'The property %s does not exist' % escape(id)
    if isinstance(value, str):
        proptype=self.getPropertyType(id, local_properties=local_properties) \
           or 'string'
        if type_converters.has_key(proptype):
            value=type_converters[proptype](value)
    self._setPropValue(id, value)

def PropertyManager_hasProperty(self, id, local_properties=False):
    """Return true if object has a property 'id'"""
    for p in self.propertyIds(local_properties=local_properties):
        if id==p:
            return 1
    return 0

def PropertyManager_getProperty(self, id, d=None, evaluate=1,
                                local_properties=False, checked_permission=None):
    """Get the property 'id', returning the optional second
        argument or None if no such property is found."""
    property_type = self.getPropertyType(id,
                      local_properties=local_properties)
    if evaluate and property_type == 'tales':
        value = getattr(self, id)
        expression = Expression(value)
        econtext = createExpressionContext(self)
        return expression(econtext)
    elif property_type:
      return getattr(self, id, d)
    return d

def PropertyManager_getPropertyType(self, id, local_properties=False):
    """Get the type of property 'id', returning None if no
      such property exists"""
    if local_properties:
      property_map = getattr(self, '_local_properties', [])
    else:
      property_map = self._propertyMap()
    for md in property_map:
        if md['id']==id:
            return md.get('type', 'string')
    return None

def PropertyManager_setProperty(self, id, value, type=None):
    # for selection and multiple selection properties
    # the value argument indicates the select variable
    # of the property

    if type is None:
      # Generate a default type
      if isinstance(value, (list, tuple)):
        type = 'lines'
      elif isinstance(value, int):
        type = 'int'
      elif isinstance(value, long):
        type = 'long'
      elif isinstance(value, float):
        type = 'float'
      elif isinstance(value, basestring):
        if len(value.split('\n')) > 1:
          type = 'text'
        else:
          type = 'string'
      elif isinstance(value, DateTime):
        type = 'date'
      else:
        type = 'string'

    self._wrapperCheck(value)
    if not self.valid_property_id(id):
        raise BadRequest, 'Invalid or duplicate property id: %s' % id

    if type in ('selection', 'multiple selection'):
        if not hasattr(self, value):
            raise BadRequest, 'No select variable %s' % value
        self._local_properties=getattr(self, '_local_properties', ()) + (
            {'id':id, 'type':type, 'select_variable':value},)
        if type=='selection':
            self._setPropValue(id, '')
        else:
            self._setPropValue(id, [])
    else:
        self._local_properties = getattr(self,
                '_local_properties', ()) + ({'id':id, 'type':type},)
        self._setPropValue(id, value)

def PropertyManager_valid_property_id(self, id):
    # This is required because in order to disable acquisition
    # we set all properties with a None value on the class Base,
    # so wee need to check if the property is not on Base.__dict__

    from Products.ERP5Type.Base import Base
    if not id or id[:1]=='_' or (id[:3]=='aq_') \
       or (' ' in id) or (hasattr(aq_base(self), id) and \
       not (Base.__dict__.has_key(id) and Base.__dict__[id] is None)) or escape(id) != id:
        return 0
    return 1

def PropertyManager_delProperty(self, id):
    if not self.hasProperty(id):
        raise ValueError, 'The property %s does not exist' % escape(id)
    self._delPropValue(id)
    self._local_properties=tuple(filter(lambda i, n=id: i['id'] != n,
                                  getattr(self, '_local_properties', ())))

def PropertyManager_propertyIds(self, local_properties=False):
    """Return a list of property ids """
    return map(lambda i: i['id'], self._propertyMap(
      local_properties=local_properties))

def PropertyManager_propertyValues(self):
    """Return a list of actual property objects """
    return map(lambda i,s=self: s.getProperty(i['id']), self._propertyMap())

def PropertyManager_propertyItems(self):
    """Return a list of (id,property) tuples """
    return map(lambda i,s=self: (i['id'],s.getProperty(i['id'])), self._propertyMap())

def PropertyManager_propertyMap(self, local_properties=False):
    """Return a tuple of mappings, giving meta-data for properties """
    property_map = list(self._properties)
    property_dict = {}
    for p in property_map:
      property_dict[p['id']] = None
      # base_id is defined for properties which are associated to multiple accessors
      if p.has_key('base_id'): property_dict[p['base_id']] = None
    # Only add those local properties which are not global
    for p in getattr(self, '_local_properties', ()):
      if not property_dict.has_key(p['id']):
        property_map.append(p)
    return tuple(property_map)

def PropertyManager_propdict(self):
    dict={}
    for p in self._propertyMap():
        dict[p['id']]=p
    return dict

def PropertyManager_manage_addProperty(self, id, value, type, REQUEST=None):
    """Add a new property via the web. Sets a new property with
    the given id, type, and value."""
    if type_converters.has_key(type):
        value=type_converters[type](value)
    #LOG('manage_addProperty', 0, 'id = %r, value = %r, type = %r, REQUEST = %r' % (id, value, type, REQUEST))
    self._setProperty(id.strip(), value, type)
    if REQUEST is not None:
        return self.manage_propertiesForm(self, REQUEST)

PropertyManager.manage_addProperty = PropertyManager_manage_addProperty
PropertyManager.manage_propertiesForm = PropertyManager_manage_propertiesForm
PropertyManager._updateProperty = PropertyManager_updateProperty
PropertyManager.valid_property_id = PropertyManager_valid_property_id
PropertyManager.getPropertyType = PropertyManager_getPropertyType
PropertyManager._setProperty = PropertyManager_setProperty
PropertyManager._delProperty = PropertyManager_delProperty
PropertyManager.propertyIds = PropertyManager_propertyIds
PropertyManager.propertyValues = PropertyManager_propertyValues
PropertyManager.propertyItems = PropertyManager_propertyItems
PropertyManager._propertyMap = PropertyManager_propertyMap
PropertyManager.propdict = PropertyManager_propdict
PropertyManager.hasProperty = PropertyManager_hasProperty
PropertyManager.getProperty = PropertyManager_getProperty

from ZPublisher.Converters import type_converters, field2string

type_converters['tales'] = field2string
