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
from AccessControl import allow_module, allow_class, allow_type
from AccessControl import ModuleSecurityInfo
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

add_builtins(bin=bin, classmethod=classmethod, format=format, object=object,
             property=property, slice=slice, staticmethod=staticmethod,
             super=super, type=type)

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

def guarded_sorted(seq, cmp=None, key=None, reverse=False):
    if not isinstance(seq, SafeIter):
        for i, x in enumerate(seq):
            guard(seq, x, i)
    return sorted(seq, cmp=cmp, key=key, reverse=reverse)
safe_builtins['sorted'] = guarded_sorted

def guarded_reversed(seq):
    return SafeIter(reversed(seq))
safe_builtins['reversed'] = guarded_reversed

def guarded_enumerate(seq, start=0):
    return NullIter(enumerate(guarded_iter(seq), start=start))
safe_builtins['enumerate'] = guarded_enumerate

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

def _check_access_wrapper(expected_type, white_list_dict):
  def _check_access(name, value):
    # Check whether value is a method of expected type
    self = getattr(value, '__self__', None)
    if self is None: # item
        return 1
    # Disallow spoofing
    if type(self) is not expected_type:
        return 0
    if getattr(value, '__name__', None) != name:
        return 0
    return white_list_dict.get(name, 0)

  return _check_access

_set_white_dict = {
    'add': 1, 'clear': 1, 'copy': 1, 'difference': 1, 'difference_update': 1,
    'discard': 1, 'intersection': 1, 'intersection_update': 1, 'isdisjoint': 1,
    'issubset': 1, 'issuperset': 1, 'pop': get_set_pop, 'remove': 1,
    'symmetric_difference': 1, 'symmetric_difference_update': 1, 'union': 1,
    'update': 1}

ContainerAssertions[set] = _check_access_wrapper(set, _set_white_dict)

ContainerAssertions[frozenset] = 1

from collections import OrderedDict
ModuleSecurityInfo('collections').declarePublic('OrderedDict')

from collections import defaultdict
ModuleSecurityInfo('collections').declarePublic('defaultdict')

from AccessControl.ZopeGuards import _dict_white_list

# Attributes cannot be set on defaultdict, thus modify 'safetype' dict
# (closure) directly to ignore defaultdict like dict/list
from RestrictedPython.Guards import full_write_guard
ContainerAssertions[defaultdict] = _check_access_wrapper(defaultdict, _dict_white_list)
full_write_guard.func_closure[1].cell_contents.__self__[defaultdict] = True

# In contrary to builtins such as dict/defaultdict, it is possible to set
# attributes on OrderedDict instances, so only allow setitem/delitem
ContainerAssertions[OrderedDict] = _check_access_wrapper(OrderedDict, _dict_white_list)
OrderedDict.__guarded_setitem__ = OrderedDict.__setitem__.__func__
OrderedDict.__guarded_delitem__ = OrderedDict.__delitem__.__func__

# given as example in Products.PythonScripts.module_access_examples
allow_module('base64')
allow_module('binascii')
allow_module('bisect')
allow_module('colorsys')
allow_module('crypt')
##

allow_module('pprint')
allow_module('quopri')
ModuleSecurityInfo('json').declarePublic('dumps', 'loads')

import re
allow_module('fnmatch')
allow_module('re')
allow_type(type(re.compile('')))
allow_type(type(re.match('x','x')))
allow_type(type(re.finditer('x','x')))

import cStringIO
f = cStringIO.StringIO()
allow_module('cStringIO')
allow_module('StringIO')
allow_type(type(f))

ModuleSecurityInfo('cgi').declarePublic('escape', 'parse_header')
allow_module('datetime')
import datetime
ContainerAssertions[datetime.datetime] = 1
ContainerAssertions[datetime.time] = 1
ContainerAssertions[datetime.date] = 1
ContainerAssertions[datetime.timedelta] = 1
ContainerAssertions[datetime.tzinfo] = 1
allow_module('difflib')
allow_module('hashlib')
import hashlib
# XXX: assumes all hash types share the same base class (this is at least true
# for md5 and sha1/224/256/384/512)
allow_type(type(hashlib.md5()))
allow_module('time')
allow_module('unicodedata')
allow_module('urlparse')
allow_module('struct')

ModuleSecurityInfo('os.path').declarePublic(
# Allow functions accessing neither file system nor environment.
  'abspath', 'basename', 'commonprefix', 'dirname', 'isabs', 'join',
  'normpath', 'split', 'splitext',
# Also allow some handy data properties.
  'sep', 'pardir', 'curdir', 'extsep',
)
ModuleSecurityInfo('email.mime.application').declarePublic('MIMEApplication')
ModuleSecurityInfo('email.mime.audio').declarePublic('MIMEAudio')
ModuleSecurityInfo('email.mime.base').declarePublic('MIMEBase')
ModuleSecurityInfo('email.mime.image').declarePublic('MIMEImage')
ModuleSecurityInfo('email.mime.message').declarePublic('MIMEMessage')
ModuleSecurityInfo('email.mime.multipart').declarePublic('MIMEMultipart')
ModuleSecurityInfo('email.mime.nonmultipart').declarePublic('MIMENonMultipart')
ModuleSecurityInfo('email.mime.text').declarePublic('MIMEText')

# Alias modules - only applied to restricted python.
MNAME_MAP = {
  'zipfile': 'Products.ERP5Type.ZipFile',
  'calendar': 'Products.ERP5Type.Calendar',
}
for alias, real in MNAME_MAP.items():
  assert '.' not in alias, alias # TODO: support this
  allow_module(real)
del alias, real
orig_guarded_import = safe_builtins['__import__']
def guarded_import(mname, globals=None, locals=None, fromlist=None,
    level=-1):
  for fromname in fromlist or ():
    if fromname[:1] == '_':
      raise Unauthorized(fromname)
  if mname in MNAME_MAP:
    mname = MNAME_MAP[mname]
    if not fromlist:
      # fromlist value is meaningless but required. See __import__ doc.
      fromlist = ['__name__']
  return orig_guarded_import(mname, globals, locals, fromlist, level)
safe_builtins['__import__'] = guarded_import

ModuleSecurityInfo('transaction').declarePublic('doom')

ModuleSecurityInfo('urllib').declarePublic(
  'urlencode',
  'quote', 'unquote',
  'quote_plus', 'unquote_plus',
)

import hmac
allow_module('hmac')
# HMAC does not sub-class object so ContainerAssertions
# does not work
hmac.HMAC.__allow_access_to_unprotected_subobjects__ = 1

import decimal
allow_module('decimal')
ContainerAssertions[decimal.Decimal] = 1
ContainerAssertions[decimal.Context] = 1
for member_id in dir(decimal):
  member = getattr(decimal, member_id)
  if isinstance(member, type) and issubclass(member, decimal.DecimalException):
    ContainerAssertions[member] = 1
del member_id, member
