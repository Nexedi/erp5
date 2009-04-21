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

import warnings

from Base import func_code, type_definition, list_types, ATTRIBUTE_PREFIX, Setter as BaseSetter, Getter as BaseGetter
from zLOG import LOG
from Products.ERP5Type.PsycoWrapper import psyco

class SetSetter(BaseSetter):
    """
      Sets a category value through a provided value (List mode)
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
        LOG("ERP5Type Deprecated Setter Id:",0, self._id)
      instance._setValue(self._key, args[0],
                                                spec=kw.get('spec',()),
                                                filter=kw.get('filter', None),
                                                portal_type=kw.get('portal_type',()),
                                                keep_default=1,
                                                checked_permission=kw.get('checked_permission', None))
      if self._reindex:
        warnings.warn("The reindexing accessors are deprecated.\n"
                      "Please use Alias.Reindex instead.",
                      DeprecationWarning)
        instance.reindexObject()
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
      if self._reindex:
        warnings.warn("The reindexing accessors are deprecated.\n"
                      "Please use Alias.Reindex instead.",
                      DeprecationWarning)
        instance.reindexObject()
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
      if self._reindex:
        warnings.warn("The reindexing accessors are deprecated.\n"
                      "Please use Alias.Reindex instead.",
                      DeprecationWarning)
        instance.reindexObject()
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
      return instance._getDefaultAcquiredValue(self._key, **kw)

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
      #LOG("__call__:",0, str((args,kw)))
      return instance._getAcquiredValueList(self._key, **kw)

    psyco.bind(__call__)


class SetGetter(ListGetter):
    """
    Gets a category value set
    """
    def __call__(self, instance, *args, **kw):
      result_list = ListGetter.__call__(self, instance, *args, **kw)
      result_set = dict([(x, 0) for x in result_list]).keys()
      return result_set


class DefaultTitleGetter(BaseGetter):
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
      o = instance._getDefaultAcquiredValue(self._key, **kw)
      if o is None:
        return None
      return o.getTitle()

    psyco.bind(__call__)

class TitleListGetter(BaseGetter):
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
      return [x.getTitle() for x in instance._getAcquiredValueList(self._key, **kw)]

    psyco.bind(__call__)

class TitleSetGetter(TitleListGetter):
    """
    Gets a category value set
    """
    def __call__(self, instance, *args, **kw):
      result_list = TitleListGetter.__call__(self, instance, *args, **kw)
      result_set = dict([(x, 0) for x in result_list]).keys()
      return result_set


class DefaultTranslatedTitleGetter(BaseGetter):
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
                                                 portal_type=kw.get('portal_type',()),
                                                 checked_permission=kw.get('checked_permission', None))
      if o is None:
        return None
      return o.getTranslatedTitle()

    psyco.bind(__call__)

class TranslatedTitleListGetter(BaseGetter):
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
      return [x.getTranslatedTitle() for x in instance._getAcquiredValueList(self._key,
                                                    spec=kw.get('spec',()),
                                                    filter=kw.get('filter', None),
                                                    portal_type=kw.get('portal_type',()),
                                                    checked_permission=kw.get('checked_permission', None))
                                                  ]

    psyco.bind(__call__)

class TranslatedTitleSetGetter(TranslatedTitleListGetter):
    """
    Gets a category value set
    """
    def __call__(self, instance, *args, **kw):
      result_list = TranslatedTitleListGetter.__call__(
           self, instance, *args, **kw)
      result_set = dict([(x, 0) for x in result_list]).keys()
      return result_set


class DefaultReferenceGetter(BaseGetter):
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
                                                 portal_type=kw.get('portal_type',()),
                                                 checked_permission=kw.get('checked_permission', None))
      if o is None:
        return None
      return o.getReference()

    psyco.bind(__call__)

class ReferenceListGetter(BaseGetter):
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
      return [x.getReference() for x in instance._getAcquiredValueList(self._key,
                                                    spec=kw.get('spec',()),
                                                    filter=kw.get('filter', None),
                                                    portal_type=kw.get('portal_type',()),
                                                    checked_permission=kw.get('checked_permission', None))
                                                  ]

    psyco.bind(__call__)

class ReferenceSetGetter(ReferenceListGetter):
    """
    Gets a category value set
    """
    def __call__(self, instance, *args, **kw):
      result_list = ReferenceListGetter.__call__(
           self, instance, *args, **kw)
      result_set = dict([(x, 0) for x in result_list]).keys()
      return result_set


class DefaultUidGetter(BaseGetter):
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
                                                 portal_type=kw.get('portal_type',()),
                                                 checked_permission=kw.get('checked_permission', None))
      if value is not None:
        return value.getUid()
      else:
        return None

    psyco.bind(__call__)

UidGetter = DefaultUidGetter

class UidListGetter(BaseGetter):
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
      return [x.getUid() for x in instance._getAcquiredValueList(self._key,
                                                    spec=kw.get('spec',()),
                                                    filter=kw.get('filter', None),
                                                    portal_type=kw.get('portal_type',()),
                                                    checked_permission=kw.get('checked_permission', None))
                                                  ]

    psyco.bind(__call__)

class UidSetGetter(UidListGetter):
    """
    Gets a category value set
    """
    def __call__(self, instance, *args, **kw):
      result_list = UidListGetter.__call__(
           self, instance, *args, **kw)
      result_set = dict([(x, 0) for x in result_list]).keys()
      return result_set


class UidSetSetter(BaseSetter):
    """
      Sets a category from the uid of the object
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
      instance._setValueUidList(self._key, args[0],
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()),
                                                 keep_default=1,
                                                 checked_permission=kw.get('checked_permission', None))
      if self._reindex:
        warnings.warn("The reindexing accessors are deprecated.\n"
                      "Please use Alias.Reindex instead.",
                      DeprecationWarning)
        instance.reindexObject()

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
      if self._reindex:
        warnings.warn("The reindexing accessors are deprecated.\n"
                      "Please use Alias.Reindex instead.",
                      DeprecationWarning)
        instance.reindexObject()
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
      if self._reindex:
        warnings.warn("The reindexing accessors are deprecated.\n"
                      "Please use Alias.Reindex instead.",
                      DeprecationWarning)
        instance.reindexObject()
      return (instance, )

class DefaultIdGetter(BaseGetter):
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
      value = instance._getDefaultAcquiredValue(self._key, spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()),
                                                 checked_permission=kw.get('checked_permission', None))
      if value is not None:
        return value.getId()
      else:
        return None

    psyco.bind(__call__)

IdGetter = DefaultIdGetter

class DefaultTitleOrIdGetter(BaseGetter):
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
      value = instance._getDefaultAcquiredValue(self._key, spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()),
                                                 checked_permission=kw.get('checked_permission', None))
      if value is not None:
        return value.getTitleOrId()
      else:
        return None

    psyco.bind(__call__)

TitleOrIdGetter = DefaultTitleOrIdGetter

class DefaultLogicalPathGetter(BaseGetter):
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
      value = instance._getDefaultAcquiredValue(self._key, spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()),
                                                 checked_permission=kw.get('checked_permission', None))
      if value is not None:
        return value.getLogicalPath()
      else:
        return None

    psyco.bind(__call__)

LogicalPathGetter = DefaultLogicalPathGetter

class IdListGetter(BaseGetter):
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
      return [x.getId() for x in instance._getAcquiredValueList(self._key,
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()),
                                                 checked_permission=kw.get('checked_permission', None))
                                                  ]

    psyco.bind(__call__)

class IdSetGetter(IdListGetter):
    """
    Gets a category value set
    """
    def __call__(self, instance, *args, **kw):
      result_list = IdListGetter.__call__(
           self, instance, *args, **kw)
      result_set = dict([(x, 0) for x in result_list]).keys()
      return result_set


class LogicalPathListGetter(BaseGetter):
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
      return [x.getLogicalPath() for x in instance._getAcquiredValueList(self._key,
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()),
                                                 checked_permission=kw.get('checked_permission', None))
                                                  ]

class LogicalPathSetGetter(LogicalPathListGetter):
    """
    Gets a category value set
    """
    def __call__(self, instance, *args, **kw):
      result_list = LogicalPathListGetter.__call__(
           self, instance, *args, **kw)
      result_set = dict([(x, 0) for x in result_list]).keys()
      return result_set


class DefaultPropertyGetter(BaseGetter):
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
                                                 portal_type=kw.get('portal_type',()),
                                                 checked_permission=kw.get('checked_permission', None))
      if value is not None:
        return value.getProperty(key)
      else:
        return None

    psyco.bind(__call__)

PropertyGetter = DefaultPropertyGetter

class PropertyListGetter(BaseGetter):
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
      return [x.getProperty(key) for x in instance._getAcquiredValueList(self._key,
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()),
                                                 checked_permission=kw.get('checked_permission', None))
                                                  ]

    psyco.bind(__call__)

class PropertySetGetter(PropertyListGetter):
    """
    Gets a category value set
    """
    def __call__(self, instance, *args, **kw):
      result_list = PropertyListGetter.__call__(
           self, instance, *args, **kw)
      result_set = dict([(x, 0) for x in result_list]).keys()
      return result_set
