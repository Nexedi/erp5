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
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Acquisition import aq_base
from Products.ERP5Type import Permissions, interfaces
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.Accessor.TypeDefinition import list_types

@zope.interface.implementer(interfaces.IPropertyRecordable,)
class PropertyRecordableMixin:
  """
  This class provides a generic implementation of IPropertyRecordable.

  IPropertyRecordable provides methods to record
  existing properties of a document and later retrieve
  them. It is used by simulation to record forced
  properties on simulation movements, but could be used
  for other purpose.

  TODO:
    - extend interface to support time (getRecordedPropertyList)
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.ModifyPortalContent, 'recordProperty')
  def recordProperty(self, id):
    """
    Records the current value of a property.

    id -- ID of the property
    """
    for property_info in self.getPropertyMap():
      if property_info['id'] == id:
        if property_info['type'] in list_types:
          value = self.getPropertyList(id)
        else:
          value = self.getProperty(id)
        break
    else:
      if id in self.getBaseCategoryList():
        value = self.getPropertyList(id)
      else: # should be local property
        value = self.getProperty(id)
    try:
      self._getRecordedPropertyDict()[id] = value
    except AttributeError:
      self._recorded_property_dict = PersistentMapping({id: value})

  security.declareProtected(Permissions.ModifyPortalContent,
                            'clearRecordedProperty')
  def clearRecordedProperty(self, id):
    """
    Clears a previously recorded property from
    the property record.
    """
    self._getRecordedPropertyDict({}).pop(id, None)
    if not self._getRecordedPropertyDict(True):
      del self._recorded_property_dict

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getRecordedPropertyIdList')
  def getRecordedPropertyIdList(self):
    """
    Returns the list of property IDs which have
    been recorded.
    """
    return list(self._getRecordedPropertyDict({}).keys())

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isPropertyRecorded')
  def isPropertyRecorded(self, id):
    """
    Returns True if property with given ID has been
    previously recorded, False else.

    id -- ID of the property
    """
    return id in self._getRecordedPropertyDict(())

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getRecordedProperty')
  def getRecordedProperty(self, id):
    """
    Returns recorded value of property with given ID

    id -- ID of the property
    """
    return self._getRecordedPropertyDict()[id]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asRecordedContext')
  def asRecordedContext(self):
    """
    Returns current document as a temp document
    which recorded properties in its context.
    """
    context = self.asContext()
    context._edit(**self._getRecordedPropertyDict({}))
    return context

  def _getRecordedPropertyDict(self, *args):
    return getattr(aq_base(self), '_recorded_property_dict', *args)

InitializeClass(PropertyRecordableMixin)
