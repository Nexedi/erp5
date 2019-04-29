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

from collections import OrderedDict
from operator import methodcaller
from Base import func_code, type_definition, list_types, ATTRIBUTE_PREFIX, Setter as BaseSetter, Getter as BaseGetter
from zLOG import LOG
from Products.ERP5Type.PsycoWrapper import psyco
from Products.ERP5Type.Utils import convertToUpperCase

class SetSetter(BaseSetter):
    """
      Sets a category value through a provided value (List mode)
    """
    _need__name__=1

    # This can not be called from the Web

    def __init__(self, id, key, warning=0):
      self._id = id
      self.__name__ = id
      self._key = key
      self._warning = warning

    def __call__(self, instance, value, *args, **kw):
      if self._warning:
        LOG("ERP5Type Deprecated Setter Id:",0, self._id)
      value = tuple(OrderedDict.fromkeys(value))
      instance._setValue(self._key, value,
                                                spec=kw.get('spec',()),
                                                filter=kw.get('filter', None),
                                                portal_type=kw.get('portal_type',()),
                                                keep_default=1,
                                                checked_permission=kw.get('checked_permission', None))
      return (instance, )

    psyco.bind(__call__)

class ListSetter(SetSetter):
    """
      Sets a category value through a provided value (Set mode)
    """
    _need__name__=1

    def __call__(self, instance, *args, **kw):
      if self._warning:
        LOG("ERP5Type Deprecated Setter Id:",0, self._id)
      instance._setValue(self._key, args[0],
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()),
                                                 keep_default=0,
                                                 checked_permission=kw.get('checked_permission', None))
      return (instance, )

    psyco.bind(__call__)

Setter = ListSetter

class DefaultSetter(SetSetter):
    """
      Sets a category value through a provided value (Set mode)
    """
    _need__name__=1

    def __call__(self, instance, *args, **kw):
      if self._warning:
        LOG("ERP5Type Deprecated Setter Id:",0, self._id)
      instance._setDefaultValue(self._key, args[0],
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()),
                                                 checked_permission=kw.get('checked_permission', None))
      return (instance, )

    psyco.bind(__call__)

class DefaultGetter(BaseGetter):
    """
      Gets a default reference object
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self', 'args', 'kw' )
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key, warning=0):
      self._id = id
      self.__name__ = id
      self._key = key
      self._warning = warning

    def __call__(self, instance, *args, **kw):
      if self._warning:
        LOG("ERP5Type Deprecated Getter Id:",0, self._id)
      if args:
        kw['default'] = args[0]
      return instance.getDefaultAcquiredValue(self._key, **kw)

    psyco.bind(__call__)

Getter = DefaultGetter

class ListGetter(BaseGetter):
    """
      Gets a list of reference objects
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    # XXX This does not work yet completely in URL mode
    func_code = func_code()
    func_code.co_varnames = ('self', 'args', 'kw' )
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key, warning=0):
      self._id = id
      self.__name__ = id
      self._key = key
      self._warning = warning

    def __call__(self, instance, *args, **kw):
      if self._warning:
        LOG("ERP5Type Deprecated Getter Id:",0, self._id)
      if args:
        kw['default'] = args[0]
      return instance.getAcquiredValueList(self._key, **kw)

    psyco.bind(__call__)


class SetGetter(ListGetter):
    """
    Gets a category value set
    """
    def __call__(self, instance, *args, **kw):
      r = ListGetter.__call__(self, instance, **kw)
      return list(OrderedDict.fromkeys(r)) if r or not args else args[0]


def defMethodGetter(key, method=None):
  key = convertToUpperCase(key)
  name = 'Default%sGetter' % key
  if method is None:
    method = methodcaller('get' + key)
  def __call__(self, instance, *args, **kw):
    o = DefaultGetter.__call__(self, instance, **kw)
    if o is None:
      return args[0] if args else None
    return method(o)
  psyco.bind(__call__)
  globals()[name] = type(name, (DefaultGetter,), {'__call__': __call__})

  name = '%sListGetter' % key
  def __call__(self, instance, *args, **kw):
    r = ListGetter.__call__(self, instance, **kw)
    return map(method, r) if r or not args else args[0]
  psyco.bind(__call__)
  globals()[name] = type(name, (ListGetter,), {'__call__': __call__})

  name = '%sSetGetter' % key
  def __call__(self, instance, *args, **kw):
    r = ListGetter.__call__(self, instance, **kw)
    return list({method(x) for x in r}) if r or not args else args[0]
  psyco.bind(__call__)
  globals()[name] = type(name, (ListGetter,), {'__call__': __call__})


defMethodGetter('id')
defMethodGetter('logical_path')
defMethodGetter('reference')
defMethodGetter('short_title')
defMethodGetter('title')
defMethodGetter('title_or_id')
defMethodGetter('translated_title')
defMethodGetter('uid')
defMethodGetter('translated_logical_path', methodcaller(
  'getLogicalPath', item_method='getTranslatedTitle'))

IdGetter = DefaultIdGetter
TitleOrIdGetter = DefaultTitleOrIdGetter
LogicalPathGetter = DefaultLogicalPathGetter
TranslatedLogicalPathGetter = DefaultTranslatedLogicalPathGetter


class UidSetSetter(BaseSetter):
    """
      Sets a category from the uid of the object
    """
    _need__name__=1

    # This can not be called from the Web

    def __init__(self, id, key, warning=0):
      self._id = id
      self.__name__ = id
      self._key = key
      self._warning = warning

    def __call__(self, instance, *args, **kw):
      if self._warning:
        LOG("ERP5Type Deprecated Getter Id:",0, self._id)
      instance._setValueUidList(self._key, set(args[0]),
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()),
                                                 keep_default=1,
                                                 checked_permission=kw.get('checked_permission', None))

class UidListSetter(UidSetSetter):
    """
      Sets a category from the uid of the object
    """
    _need__name__=1

    def __call__(self, instance, *args, **kw):
      if self._warning:
        LOG("ERP5Type Deprecated Getter Id:",0, self._id)
      instance._setValueUidList(self._key, args[0],
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()),
                                                 keep_default=0,
                                                 checked_permission=kw.get('checked_permission', None))
      return (instance, )

UidSetter = UidListSetter

class UidDefaultSetter(UidSetSetter):
    """
      Sets a category from the uid of the object
    """
    _need__name__=1

    def __call__(self, instance, *args, **kw):
      if self._warning:
        LOG("ERP5Type Deprecated Getter Id:",0, self._id)
      instance._setDefaultValueUid(self._key, args[0],
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()),
                                                 checked_permission=kw.get('checked_permission', None))
      return (instance, )


class DefaultPropertyGetter(DefaultGetter):
  def __call__(self, instance, key, *args, **kw):
    o = DefaultGetter.__call__(self, instance, **kw)
    if o is None:
      return args[0] if args else None
    return o.getProperty(key)

  psyco.bind(__call__)

PropertyGetter = DefaultPropertyGetter

class PropertyListGetter(ListGetter):
  def __call__(self, instance, key, *args, **kw):
    r = ListGetter.__call__(self, instance, **kw)
    return [x.getProperty(key) for x in r] if r or not args else args[0]
  psyco.bind(__call__)

class PropertySetGetter(PropertyListGetter):
    """
    Gets a category value set
    """
    def __call__(self, instance, *args, **kw):
      r = PropertyListGetter.__call__(self, instance, **kw)
      return list(set(r)) if r or not args else args[0]
