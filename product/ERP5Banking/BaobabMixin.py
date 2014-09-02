##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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

import ExtensionClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.ERP5Type import Permissions
from Products.ERP5Type.Accessor.Base import Method, func_code
from Products.ERP5Type.Utils import convertToMixedCase, convertToUpperCase
from Products.ERP5Type.Globals import InitializeClass

class BaobabGetter(Method):
  """Get a category differently
  """
  _need__name__ = 1

  # Generic Definition of Method Object
  # This is required to call the method form the Web
  func_code = func_code()
  func_code.co_varnames = ('self', )
  func_code.co_argcount = 1
  func_defaults = ()

  def __init__(self, id, method_id):
    self._id = id
    self.__name__ = id
    self._method_id = method_id

  def __call__(self, instance, *args, **kw):
    portal_type = instance.getPortalType()
    skin_id = '%s_%s' % (portal_type.replace(' ', ''), self._id)
    skin = getattr(instance, skin_id, None)
    if skin is not None:
      return skin(*args, **kw)
    return getattr(instance, self._method_id)(*args, **kw)

class BaobabValueGetter(Method):
  """Get the value of a baobab category
  """
  _need__name__ = 1

  # Generic Definition of Method Object
  # This is required to call the method form the Web
  func_code = func_code()
  func_code.co_varnames = ('self', )
  func_code.co_argcount = 1
  func_defaults = ()

  def __init__(self, id, method_id):
    self._id = id
    self.__name__ = id
    self._method_id = method_id

  def __call__(self, instance, *args, **kw):
    category = getattr(instance, self._method_id)(*args, **kw)
    if category is not None:
      return instance.portal_categories.resolveCategory(category)

class BaobabPropertyGetter(Method):
  """Get the property of a baobab category
  """
  _need__name__ = 1

  # Generic Definition of Method Object
  # This is required to call the method form the Web
  func_code = func_code()
  func_code.co_varnames = ('self', )
  func_code.co_argcount = 1
  func_defaults = ()

  def __init__(self, id, method_id, property_id):
    self._id = id
    self.__name__ = id
    self._method_id = method_id
    self._property_id = property_id

  def __call__(self, instance, *args, **kw):
    value = getattr(instance, self._method_id)(*args, **kw)
    if value is not None:
      return value.getProperty(self._property_id, *args, **kw)

class BaobabMixin(ExtensionClass.Base):
  """This class provides different ways to access source, destination, etc.
  """
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,
                            "getTitle")
  def getTitle(self, default=''):
    return getattr(aq_base(self), 'title', default)

for category in ('source', 'destination',
                 'source_section', 'destination_section',
                 'source_payment', 'destination_payment',
                 'source_function', 'destination_function',
                 'source_project', 'destination_project',
                 'source_variation_text', 'destination_variation_text',):
  getter_id = 'getBaobab%s' % (convertToUpperCase(category))
  original_getter_id = 'get%s' % (convertToUpperCase(category))
  method = BaobabGetter(getter_id, original_getter_id)
  setattr(BaobabMixin, getter_id, method)
  BaobabMixin.security.declareProtected(Permissions.View, getter_id)

  value_getter_id = getter_id + 'Value'
  method = BaobabValueGetter(value_getter_id, getter_id)
  setattr(BaobabMixin, value_getter_id, method)
  BaobabMixin.security.declareProtected(Permissions.View, value_getter_id)

  for prop in ('uid', 'title', 'id'):
    prop_getter_id = getter_id + convertToUpperCase(prop)
    method = BaobabPropertyGetter(prop_getter_id, value_getter_id, prop)
    setattr(BaobabMixin, prop_getter_id, method)
    BaobabMixin.security.declareProtected(Permissions.View, prop_getter_id)

InitializeClass(BaobabMixin)
