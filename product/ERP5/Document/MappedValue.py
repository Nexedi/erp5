# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

import zope.interface
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.Core.Predicate import Predicate

TRANSFORMATION_FIX = True
_MARKER = []

class MappedValue(Predicate):
  """
    A MappedValue allows to associate a value to a predicate

  XXX Why do we redefine xxxProperty methods ?
      When a property is defined by a property sheet with a specific storage_id,
      they break accessors of this property when a value is mapped to it.
  """
  meta_type = 'ERP5 Mapped Value'
  portal_type = 'Mapped Value'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (   PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.Predicate
                      , PropertySheet.MappedValue
                    )
  # Declarative interfaces
  zope.interface.implements(interfaces.IMappedValue,
                           )
  security.declareProtected(Permissions.AccessContentsInformation, 'getMappedValueBaseCategoryList')
  def getMappedValueBaseCategoryList(self, d=_MARKER):
    if TRANSFORMATION_FIX:
      # Fix Mapped Value Objects which forgot to define their Mapped Base Categories
      if not self._baseGetMappedValueBaseCategoryList():
        if self.getParentValue().getParentValue().getPortalType() == 'Transformation':
          base_category_dict = {}
          for category in self.getCategoryList():
            # XXX-JPS additional test required to prevent taking too much ?
            base_category_dict[category.split('/')[0]] = None
          self._setMappedValueBaseCategoryList(base_category_dict.keys())
    if d is _MARKER:
      return self._baseGetMappedValueBaseCategoryList(d=d)
    return self._baseGetMappedValueBaseCategoryList()

  security.declareProtected( Permissions.AccessContentsInformation, 'getProperty' )
  def getProperty(self, key, d=_MARKER, **kw):
    """
    Use local property instead of calling (acquired) accessor
    whenever key is provided by the mapped value.

    TODO:
    - handle list properties (key ends with _list)
    - add unit tests
    """
    if key in self.getMappedValuePropertyList():
      result = getattr(aq_base(self), key, _MARKER)
      if result is not _MARKER:
        return result
    if d is _MARKER:
      return Predicate.getProperty(self, key, **kw) # XXX-JPS I would prefer to use always getProperty
                                                    # Is there any reason to overload ?
    return Predicate.getProperty(self, key, d=d, **kw)

  def getPropertyList(self, key, d=None):
    """
    Use local property instead of calling (acquired) accessor
    whenever key is provided by the mapped value.

    TODO:
    - add unit tests
    """
    if key in self.getMappedValuePropertyList():
      result = getattr(aq_base(self), key, _MARKER)
      if result is not _MARKER:
        return result
    if d is None:
      return Predicate.getPropertyList(self, key)
    return Predicate.getPropertyList(self, key, d=d)

  def _setProperty(self, key, value, type=None, **kw):
    """
    Use local property instead of calling (acquired) accessor
    whenever key is provided by the mapped value.

    TODO:
    - handle type
    - add unit tests
    """
    if key in self.getMappedValuePropertyList():
      return setattr(self, key, value)
    return Predicate._setProperty(self, key, value, type=type, **kw)

  # Check is this method should also be overriden
  #def _setPropValue(self, key, value, **kw):

  def hasProperty(self, key):
    """
    Use local property instead of calling (acquired) accessor
    whenever key is provided by the mapped value.
    """
    if key in self.getMappedValuePropertyList():
      return getattr(self, key, _MARKER) is not _MARKER
    return Predicate.hasProperty(self, key)

  def _edit(self, **kw):
    # We must first prepare the mapped value before we do the edit
    edit_order = ['mapped_value_property_list',
                  'default_mapped_value_property',
                  'mapped_value_property',
                  'mapped_value_property_set']
    i = len(edit_order)
    edit_order += [x for x in kw.pop('edit_order', ()) if x not in edit_order]
    # Base._edit updates unordered properties first
    edit_order[i:i] = [x for x in kw if x not in edit_order]
    return Predicate._edit(self, edit_order=edit_order, **kw)
