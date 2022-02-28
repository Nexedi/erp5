from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2002-2007 Nexedi SARL and Contributors. All Rights Reserved.
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

from .Base import func_code, type_definition, list_types, \
                 ATTRIBUTE_PREFIX, Getter as BaseGetter, Setter as BaseSetter
from Products.ERP5Type.PsycoWrapper import psyco
from zLOG import LOG
from zLOG import WARNING

class DefaultGetter(BaseGetter):
  """
  Gets a default reference object
  """
  _need__name__=1

  # Generic Definition of Method Object
  # This is required to call the method form the Web
  __code__ = func_code = func_code()
  __code__.co_varnames = ('self', )
  __code__.co_argcount = 1
  __defaults__ = func_defaults = ()

  def __init__(self, id, key, warning=0):
    """
    'warning' argument means that this category is deprecated in the
    property sheet, so the generated method will also be deprecated
    """
    self._id = id
    self.__name__ = id
    self._key = key
    self._warning = warning

  def __call__(self, instance, *args, **kw):
    if self._warning:
      LOG("ERP5Type", WARNING, "Deprecated Getter Id: %s" % self._id)
    assert not 'validation_state' in kw, "validation_state parameter is not supported"
    assert not 'simulation_state' in kw, "simulation_state parameter is not supported"
    return instance._getDefaultRelatedValue(
                            self._key,
                            spec=kw.get('spec',()),
                            filter=kw.get('filter', None),
                            portal_type=kw.get('portal_type', None),
                            strict_membership=kw.get('strict_membership',
                                                     # 'strict' is deprecated
                                                     kw.get('strict', None)),
                            checked_permission=kw.get('checked_permission', None))

  psyco.bind(__call__)

Getter = DefaultGetter

class ListGetter(BaseGetter):
  """
  Gets a list of reference objects
  """
  _need__name__=1

  # Generic Definition of Method Object
  # This is required to call the method form the Web
  __code__ = func_code = func_code()
  __code__.co_varnames = ('self', )
  __code__.co_argcount = 1
  __defaults__ = func_defaults = ()

  def __init__(self, id, key, warning=0):
    """
    'warning' argument means that this category is deprecated in the
    property sheet, so the generated method will also be deprecated
    """
    self._id = id
    self.__name__ = id
    self._key = key
    self._warning = warning

  def __call__(self, instance, *args, **kw):
    assert not 'validation_state' in kw, "validation_state parameter is not supported"
    assert not 'simulation_state' in kw, "simulation_state parameter is not supported"
    if self._warning:
      LOG("ERP5Type", WARNING, "Deprecated Getter Id: %s" % self._id)
    return instance._getRelatedValueList(self._key, *args, **kw)

  psyco.bind(__call__)

class SetGetter(ListGetter):
  """
  Gets a category value set
  """
  def __call__(self, instance, *args, **kw):
    return list(set(ListGetter.__call__(self, instance, *args, **kw)))


class DefaultPropertyGetter(BaseGetter):
  """
  Gets a default reference object
  """
  _need__name__=1

  # Generic Definition of Method Object
  # This is required to call the method form the Web
  __code__ = func_code = func_code()
  __code__.co_varnames = ('self', )
  __code__.co_argcount = 1
  __defaults__ = func_defaults = ()

  def __init__(self, id, key, warning=0):
    self._id = id
    self.__name__ = id
    self._key = key
    self._warning = warning

  def __call__(self, instance, key, *args, **kw):
    if self._warning:
      LOG("ERP5Type", WARNING, "Deprecated Getter Id: %s" % self._id)
    assert not 'validation_state' in kw, "validation_state parameter is not supported"
    assert not 'simulation_state' in kw, "simulation_state parameter is not supported"
    return instance._getDefaultRelatedProperty(
                         self._key, key,
                         spec=kw.get('spec',()),
                         filter=kw.get('filter', None),
                         portal_type=kw.get('portal_type', None),
                         strict_membership=kw.get('strict_membership',
                                                  # 'strict' is deprecated
                                                  kw.get('strict', None)),
                         checked_permission=kw.get('checked_permission', None))
  psyco.bind(__call__)

PropertyGetter = DefaultPropertyGetter

class PropertyListGetter(BaseGetter):
  """
  Gets a list of reference objects
  """
  _need__name__=1

  # Generic Definition of Method Object
  # This is required to call the method form the Web
  __code__ = func_code = func_code()
  __code__.co_varnames = ('self', )
  __code__.co_argcount = 1
  __defaults__ = func_defaults = ()

  def __init__(self, id, key, warning=0):
    self._id = id
    self.__name__ = id
    self._key = key
    self._warning = warning

  def __call__(self, instance, key, *args, **kw):
    if self._warning:
      LOG("ERP5Type", WARNING, "Deprecated Getter Id: %s" % self._id)
    assert not 'validation_state' in kw, "validation_state parameter is not supported"
    assert not 'simulation_state' in kw, "simulation_state parameter is not supported"
    return instance._getRelatedPropertyList(
                           self._key, key,
                           spec=kw.get('spec',()),
                           filter=kw.get('filter', None),
                           portal_type=kw.get('portal_type', None),
                           strict_membership=kw.get('strict_membership',
                                                    # 'strict' is deprecated
                                                    kw.get('strict', None)),
                           checked_permission=kw.get('checked_permission', None))
  psyco.bind(__call__)

class PropertySetGetter(PropertyListGetter):
  """
  Gets a category value set
  """
  def __call__(self, instance, *args, **kw):
    return list(set(PropertyListGetter.__call__(self, instance, *args, **kw)))


class DefaultIdGetter(PropertyGetter):
  def __call__(self, instance, *args, **kw):
    return PropertyGetter.__call__(self, instance, 'id', *args, **kw)
IdGetter = DefaultIdGetter

class IdListGetter(PropertyListGetter):
  def __call__(self, instance, *args, **kw):
    return PropertyListGetter.__call__(self, instance, 'id', *args, **kw)

class IdSetGetter(PropertySetGetter):
  def __call__(self, instance, *args, **kw):
    return PropertySetGetter.__call__(self, instance, 'id', *args, **kw)


class DefaultTitleGetter(PropertyGetter):
  def __call__(self, instance, *args, **kw):
    return PropertyGetter.__call__(self, instance, 'title', *args, **kw)
TitleGetter = DefaultTitleGetter

class TitleListGetter(PropertyListGetter):
  def __call__(self, instance, *args, **kw):
    return PropertyListGetter.__call__(self, instance, 'title', *args, **kw)

class TitleSetGetter(PropertySetGetter):
  def __call__(self, instance, *args, **kw):
    return PropertySetGetter.__call__(self, instance, 'title', *args, **kw)
