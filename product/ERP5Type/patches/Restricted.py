#############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import sys

from RestrictedPython.RestrictionMutator import RestrictionMutator

# Unsafe attributes on protected objects are already disallowed at execution
# and we don't want to maintain a duplicated list of exceptions.
RestrictionMutator.checkName = RestrictionMutator.checkAttrName = \
    lambda *args, **kw: None


from Acquisition import aq_acquire
from AccessControl import getSecurityManager
from AccessControl.ZopeGuards import (safe_builtins, _marker, Unauthorized,
    aq_validate, guard, guarded_getattr, guarded_iter, SafeIter, NullIter,
    ContainerAssertions, GuardedDictType, _dict_white_list)

# TODO: add buffer/bytearray

def add_builtins(**kw):
    assert not set(safe_builtins).intersection(kw)
    safe_builtins.update(kw)

del safe_builtins['dict']
del safe_builtins['list']
add_builtins(Ellipsis=Ellipsis, NotImplemented=NotImplemented,
             dict=dict, list=list, set=set, frozenset=frozenset)

add_builtins(classmethod=classmethod, object=object, property=property,
             slice=slice, staticmethod=staticmethod, super=super, type=type)

if sys.version_info >= (2, 6):
    add_builtins(bin=bin, format=format)

def guarded_next(iterator, default=_marker):
    """next(iterator[, default])

    Return the next item from the iterator. If default is given
    and the iterator is exhausted, it is returned instead of
    raising StopIteration.
    """
    try:
        iternext = guarded_getattr(iterator, 'next').__call__
        # this way an AttributeError while executing next() isn't hidden
        # (2.6 does this too)
    except AttributeError:
        raise TypeError("%s object is not an iterator"
                        % type(iterator).__name__)
    try:
        return iternext()
    except StopIteration:
        if default is _marker:
            raise
        return default
add_builtins(next=guarded_next)

def _check_type_access(name, v):
  def factory(inst, name):
    if not (name == 'fromkeys' and type(inst) is dict):
      # fallback to default security
      aq_acquire(inst, name, aq_validate, getSecurityManager().validate)
    return v
  return factory

ContainerAssertions[type] = _check_type_access

class SafeIterItems(SafeIter):

    def next(self):
        ob = self._next()
        c = self.container
        guard(c, ob[0])
        guard(c, ob[1])
        return ob

def get_iteritems(c, name):
    return lambda: SafeIterItems(c.iteritems(), c)
_dict_white_list['iteritems'] = get_iteritems

if sys.version_info < (2, 5):
    # these are backported in Products.ERP5Type.patches.python
    def guarded_any(seq):
        return any(guarded_iter(seq))
    safe_builtins['any'] = guarded_any

    def guarded_all(seq):
        return all(guarded_iter(seq))
    safe_builtins['all'] = guarded_all

def guarded_sorted(seq, cmp=None, key=None, reverse=False):
    if not isinstance(seq, SafeIter):
        for i, x in enumerate(seq):
            guard(seq, x, i)
    return sorted(seq, cmp=cmp, key=key, reverse=reverse)
safe_builtins['sorted'] = guarded_sorted

def guarded_reversed(seq):
    return SafeIter(reversed(seq))
safe_builtins['reversed'] = guarded_reversed

def get_set_pop(s, name):
    def guarded_pop():
        v = s.pop()
        try:
            guard(s, v)
        except Unauthorized:
            s.add(v)
            raise
        return v
    return guarded_pop

_set_white_get = {
    'add': 1, 'clear': 1, 'copy': 1, 'difference': 1, 'difference_update': 1,
    'discard': 1, 'intersection': 1, 'intersection_update': 1, 'isdisjoint': 1,
    'issubset': 1, 'issuperset': 1, 'pop': get_set_pop, 'remove': 1,
    'symmetric_difference': 1, 'symmetric_difference_update': 1, 'union': 1,
    'update': 1}.get

def _check_set_access(name, value):
    # Check whether value is a set method
    self = getattr(value, '__self__', None)
    if self is None: # item
        return 1
    # Disallow spoofing
    if type(self) is not set:
        return 0
    if getattr(value, '__name__', None) != name:
        return 0
    return _set_white_get(name, 0)

ContainerAssertions[set] = _check_set_access

ContainerAssertions[frozenset] = 1

from collections import OrderedDict
OrderedDict.__allow_access_to_unprotected_subobjects__ = 1

from AccessControl import allow_module, allow_class, allow_type
from AccessControl import ModuleSecurityInfo

# given as example in Products.PythonScripts.module_access_examples
allow_module('base64')
allow_module('binascii')
allow_module('bisect')
allow_module('colorsys')
allow_module('crypt')
##

allow_module('pprint')
ModuleSecurityInfo('json').declarePublic('dumps', 'loads')

import re
allow_module('fnmatch')
allow_module('re')
allow_type(type(re.compile('')))
allow_type(type(re.match('x','x')))

import cStringIO
f = cStringIO.StringIO()
allow_module('cStringIO')
allow_module('StringIO')
allow_type(type(f))

ModuleSecurityInfo('cgi').declarePublic('escape', 'parse_header')
allow_module('difflib')
allow_module('hashlib')
allow_module('time')
allow_module('urlparse')

ModuleSecurityInfo('os.path').declarePublic(
# Allow functions accessing neither file system nor environment.
  'abspath', 'basename', 'commonprefix', 'dirname', 'isabs', 'join',
  'normpath', 'split', 'splitext',
# Also allow some handy data properties.
  'sep', 'pardir', 'curdir', 'extsep',
)
