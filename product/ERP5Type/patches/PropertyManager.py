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
from Globals import DTMLFile
from Products.ERP5Type.Utils import createExpressionContext
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.CMFCore.Expression import Expression
from Products.ERP5Type import _dtmldir

class ERP5PropertyManager(PropertyManager):
  """
    This class is only for backward compatibility.
  """
  pass

PropertyManager_manage_propertiesForm=DTMLFile('properties',
                                               _dtmldir,
                                               property_extensible_schema__=1)


def PropertyManager_updateProperty(self, id, value):
    # Update the value of an existing property. If value
    # is a string, an attempt will be made to convert
    # the value to the type of the existing property.
    self._wrapperCheck(value)
    if not hasattr(self, 'isRADContent'):
      if not self.hasProperty(id):
          raise 'Bad Request', 'The property %s does not exist' % escape(id)
    if type(value)==type(''):
        proptype=self.getPropertyType(id) or 'string'
        if type_converters.has_key(proptype):
            value=type_converters[proptype](value)
    #LOG('_updateProperty', 0, 'self = %r, id = %r, value = %r' % (self, id, value))
    self._setPropValue(id, value)

def PropertyManager_hasProperty(self, id):
    """Return true if object has a property 'id'"""
    for p in self.propertyIds():
        if id==p:
            return 1
    return 0

def PropertyManager_getProperty(self, id, d=None, evaluate=1):
    """Get the property 'id', returning the optional second
        argument or None if no such property is found."""
    type = self.getPropertyType(id)
    if evaluate and type == 'tales':
        value = getattr(self, id)
        expression = Expression(value)
        econtext = createExpressionContext(self)
        return expression(econtext)
    elif type:
      return getattr(self, id)
    return d

def PropertyManager_getPropertyType(self, id):
    """Get the type of property 'id', returning None if no
      such property exists"""
    for md in self._propertyMap():
        if md['id']==id:
            return md.get('type', 'string')
    return None

def PropertyManager_setProperty(self, id, value, type=None):
    # for selection and multiple selection properties
    # the value argument indicates the select variable
    # of the property

    if type is None:
      # Generate a default type
      value_type = type(value)
      if value_type in (type([]), type(())):
        type = 'lines'
      elif value_type is type(1):
        type = 'int'
      elif value_type is type(1L):
        type = 'long'
      elif value_type is type(1.0):
        type = 'float'
      elif value_type is type('a'):
        if len(value_type.split('\n')) > 1:
          type = 'text'
        else:
          type = 'string'
      else:
        type = 'string'

    self._wrapperCheck(value)
    if not self.valid_property_id(id):
        raise 'Bad Request', 'Invalid or duplicate property id'

    if type in ('selection', 'multiple selection'):
        if not hasattr(self, value):
            raise 'Bad Request', 'No select variable %s' % value
        self._local_properties=getattr(self, '_local_properties', ()) + (
            {'id':id, 'type':type, 'select_variable':value},)
        if type=='selection':
            self._setPropValue(id, '')
        else:
            self._setPropValue(id, [])
    else:
        self._local_properties=getattr(self, '_local_properties', ())+({'id':id,'type':type},)
        self._setPropValue(id, value)

def PropertyManager_delProperty(self, id):
    if not self.hasProperty(id):
        raise ValueError, 'The property %s does not exist' % escape(id)
    self._delPropValue(id)
    self._local_properties=tuple(filter(lambda i, n=id: i['id'] != n,
                                  getattr(self, '_local_properties', ())))

def PropertyManager_propertyIds(self):
    """Return a list of property ids """
    return map(lambda i: i['id'], self._propertyMap())

def PropertyManager_propertyValues(self):
    """Return a list of actual property objects """
    return map(lambda i,s=self: getattr(s,i['id']), self._propertyMap())

def PropertyManager_propertyItems(self):
    """Return a list of (id,property) tuples """
    return map(lambda i,s=self: (i['id'],getattr(s,i['id'])), self._propertyMap())

def PropertyManager_propertyMap(self):
    """Return a tuple of mappings, giving meta-data for properties """
    return tuple(list(self._properties) + list(getattr(self, '_local_properties', ())))

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
ERP5TypeInformation.manage_propertiesForm = PropertyManager_manage_propertiesForm

from ZPublisher.Converters import type_converters, field2string

type_converters['tales'] = field2string
