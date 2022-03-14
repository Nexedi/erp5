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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Core.Predicate import Predicate
from erp5.component.interface.IMappedValue import IMappedValue

TRANSFORMATION_FIX = True
_MARKER = object()

@zope.interface.implementer(IMappedValue,)
class MappedValue(Predicate):
  """
    A MappedValue allows to associate a value to a predicate
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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMappedValueBaseCategoryList')
  def getMappedValueBaseCategoryList(self, d=_MARKER):
    if TRANSFORMATION_FIX:
      # Fix Mapped Value Objects which forgot to define their Mapped Base Categories
      if not self._baseGetMappedValueBaseCategoryList():
        if self.getParentValue().getParentValue().getPortalType() == 'Transformation':
          base_category_set = set()
          for category in self.getCategoryList():
            # XXX-JPS additional test required to prevent taking too much ?
            base_category_set.add(category.split('/')[0])
          self._setMappedValueBaseCategoryList(list(base_category_set))
    if d is _MARKER:
      return self._baseGetMappedValueBaseCategoryList(d=d)
    return self._baseGetMappedValueBaseCategoryList()
