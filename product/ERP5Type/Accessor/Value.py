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

from Base import func_code, type_definition, list_types, ATTRIBUTE_PREFIX, Method
from zLOG import LOG

class Setter(Method):
    """
      Sets a reference
    """
    _need__name__=1

    # This can not be called from the Web

    def __init__(self, id, key, reindex=1, warning=0):
      self._id = id
      self.__name__ = id
      self._key = key
      self._reindex = reindex
      self._warning = warning

    def __call__(self, instance, *args, **kw):
      if self._warning:
        LOG("ERP5Type Deprecated Getter Id:",0, self._id)
      instance._setValue(self._key, args[0],
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()))
      if self._reindex: instance.reindexObject()

ListSetter = Setter
SetSetter = Setter # Error XXX
DefaultSetter = Setter # Error XXX

class DefaultGetter(Method):
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
      return instance._getDefaultAcquiredValue(self._key, **kw)

Getter = DefaultGetter

class ListGetter(Method):
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
      LOG("__call__:",0, str((args,kw)))
      return instance._getAcquiredValueList(self._key, **kw)


SetGetter = ListGetter # Error XXX

class DefaultTitleGetter(Method):
    """
      Gets a default reference object
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self', )
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      o = instance._getDefaultAcquiredValue(self._key,
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()))
      if o is None:
        return None
      return o.getTitle()

class TitleListGetter(Method):
    """
      Gets a list of reference objects
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      return map(lambda x:x.getTitle(), instance._getAcquiredValueList(self._key,
                                                    spec=kw.get('spec',()),
                                                    filter=kw.get('filter', None),
                                                    portal_type=kw.get('portal_type',()))
                                                  )

TitleSetGetter = TitleListGetter # Error XXX

class DefaultUidGetter(Method):
    """
      Gets a default reference object
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      value = instance._getDefaultAcquiredValue(self._key,
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()))
      if value is not None:
        return value.getUid()
      else:
        return None

UidGetter = DefaultUidGetter

class UidListGetter(Method):
    """
      Gets a list of reference objects uid
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      return map(lambda x:x.getUid(), instance._getAcquiredValueList(self._key,
                                                    spec=kw.get('spec',()),
                                                    filter=kw.get('filter', None),
                                                    portal_type=kw.get('portal_type',()))
                                                  )
UidSetGetter = UidListGetter # Error XXX

class UidSetter(Method):
    """
      Sets a reference
    """
    _need__name__=1

    # This can not be called from the Web

    def __init__(self, id, key, reindex=1, warning=0):
      self._id = id
      self.__name__ = id
      self._key = key
      self._reindex = reindex
      self._warning = warning

    def __call__(self, instance, *args, **kw):
      if self._warning:
        LOG("ERP5Type Deprecated Getter Id:",0, self._id)
      instance._setValueUids(self._key, args[0],
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()))
      if self._reindex: instance.reindexObject()

UidListSetter = UidSetter
UidSetSetter = UidSetter # Error XXX
UidDefaultSetter = UidSetter # Error XXX

class DefaultIdGetter(Method):
    """
      Gets a default reference object
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      value = instance._getDefaultAcquiredValue(self._key, spec=kw.get('spec',()))
      if value is not None:
        return value.getId()
      else:
        return None

IdGetter = DefaultIdGetter

class DefaultTitleOrIdGetter(Method):
    """
      Gets a default reference object
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      value = instance._getDefaultAcquiredValue(self._key, spec=kw.get('spec',()))
      if value is not None:
        return value.getTitleOrId()
      else:
        return None

TitleOrIdGetter = DefaultTitleOrIdGetter

class DefaultLogicalPathGetter(Method):
    """
      Gets a default logical path object
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      value = instance._getDefaultAcquiredValue(self._key, spec=kw.get('spec',()))
      if value is not None:
        return value.getLogicalPath()
      else:
        return None

LogicalPathGetter = DefaultLogicalPathGetter

class IdListGetter(Method):
    """
      Gets a list of reference objects uid
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      return map(lambda x:x.getId(), instance._getAcquiredValueList(self._key,
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()))
                                                  )

IdSetGetter = IdListGetter # Error XXX

class LogicalPathListGetter(Method):
    """
      Gets a list of logical path
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      return map(lambda x:x.getLogicalPath(), instance._getAcquiredValueList(self._key,
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()))
                                                  )

LogicalPathSetGetter = LogicalPathListGetter # Error XXX

class DefaultPropertyGetter(Method):
    """
      Gets a default reference object
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, key, *args, **kw):
      value = instance._getDefaultAcquiredValue(self._key,
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()))
      if value is not None:
        return value.getProperty(key)
      else:
        return None

PropertyGetter = DefaultPropertyGetter

class PropertyListGetter(Method):
    """
      Gets a list of reference objects uid
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, key, *args, **kw):
      return map(lambda x:x.getProperty(key), instance._getAcquiredValueList(self._key,
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()))
                                                  )
PropertySetGetter = PropertyListGetter # Error XXX
