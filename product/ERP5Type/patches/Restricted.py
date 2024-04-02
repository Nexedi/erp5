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

import six
import copy
import sys
import types

try:
  from RestrictedPython.transformer import FORBIDDEN_FUNC_NAMES
except:
  # BBB
  FORBIDDEN_FUNC_NAMES = frozenset(['printed',])

_MARKER = []
def checkNameLax(self, node, name=_MARKER, allow_magic_methods=False):
  """Check names if they are allowed.

  In ERP5 we are much more lax that than in Zope's original restricted
  python and allow to using names starting with _, because we rely on
  runtime checks to prevent access to forbidden attributes from objects.

  We don't allow defining attributes ending with __roles__ though.

  If ``allow_magic_methods is True`` names in `ALLOWED_FUNC_NAMES`
  are additionally allowed although their names start with `_`.
  """
  if name is None:
    return

  if name is _MARKER:
    # we use same implementation for checkName and checkAttrName which access
    # the name in different ways ( see RestrictionMutator 3.6.0 )
    name = node.attrname

  if name.endswith('__roles__'):
    self.error(node, '"%s" is an invalid variable name because '
               'it ends with "__roles__".' % name)
  elif name in FORBIDDEN_FUNC_NAMES:
    self.error(node, '"{name}" is a reserved name.'.format(name=name))


try:
  from RestrictedPython.transformer import RestrictingNodeTransformer
  RestrictingNodeTransformer.check_name = checkNameLax
except ImportError:
  # BBB Restriced 3.6.0
  from RestrictedPython.RestrictionMutator import RestrictionMutator
  RestrictionMutator.checkName = RestrictionMutator.checkAttrName = checkNameLax


from Acquisition import aq_acquire
from AccessControl import getSecurityManager
from AccessControl import allow_module, allow_class, allow_type
from AccessControl import ModuleSecurityInfo
from AccessControl.ZopeGuards import (safe_builtins, _marker, Unauthorized,
    aq_validate, guard, guarded_getattr, guarded_iter, SafeIter, NullIter,
    ContainerAssertions, GuardedDictType, _dict_white_list)

# TODO: add buffer/bytearray

def add_builtins(**kw):
    assert not set(safe_builtins).intersection(kw), "%r intersect %r\n%r" %(safe_builtins, kw, set(safe_builtins).intersection(kw))
    safe_builtins.update(kw)

del safe_builtins['dict']
del safe_builtins['list']

add_builtins(Ellipsis=Ellipsis, NotImplemented=NotImplemented,
             dict=dict, list=list)
if "set" not in safe_builtins: # BBB
    add_builtins(set=set, frozenset=frozenset, slice=slice)
if "bytes" not in safe_builtins: # BBB Zope2
    assert six.PY2
    add_builtins(bytes=str)

add_builtins(bin=bin, classmethod=classmethod, format=format, object=object,
             property=property, staticmethod=staticmethod,
             super=super, type=type)

# XXX: backport of https://github.com/zopefoundation/AccessControl/pull/131
def guarded_next(iterator, default=_marker):
    if default is _marker:
        ob = next(iterator)
    else:
        ob = next(iterator, default)
    if not isinstance(iterator, SafeIter):
        guard(ob, ob)
    return ob
safe_builtins.update(next=guarded_next)

_safe_class_attribute_dict = {}
import inspect
def allow_class_attribute(klass, access=1):
  """
   Allow class methods, static methods, and class properties in the class

   klass -- the class
   access -- a dict, a callable, or a truth value that represents access control
            (defined in SimpleObjectPolicies)
  """
  assert(inspect.isclass(klass))
  _safe_class_attribute_dict[klass] = access


class TypeAccessChecker:
  """Check Access for class instances (whose type() is `type`).
  """
  def __call__(self, name, v):
    """
    Create a callable which checks the access if the context type is <type 'type'>s.
    Since the 'type' can be any types of classes, we support the three ways
    defined in AccessControl/SimpleObjectPolicies.  We implement this
    as "a method which returing a method" because we can not know what is the
    type until it is actually called. So the three ways are simulated the
    function returned by this method.

    We don't return a simple function, but a class instance with a __bool__ method
    to accomodate the two cases where this is called by SecurityManager.validate when
    checking access on the class (then only the bool is used) or by guarded_getattr
    when checking access on the instance (the __call__ is used).
    """
    class _AccessChecker:
      def __call__(self, inst, name):
        """
        Check function used with ContainerAssertions checked by cAccessControl.
        """
        access = _safe_class_attribute_dict.get(inst, 0)
        # The next 'dict' only checks the access configuration type
        if access == 1 or (isinstance(access, dict) and access.get(name, 0) == 1):
          pass
        elif isinstance(access, dict) and callable(access.get(name, 0)):
          guarded_method = access.get(name)
          return guarded_method(inst, name)
        elif callable(access):
          # Only check whether the access configuration raise error or not
          access(inst, name)
        else:
          # fallback to default security
          aq_acquire(inst, name, aq_validate, getSecurityManager().validate)
        return v

      def __bool__(self):
        return False
      __nonzero__ = __bool__ # six.PY2

    return _AccessChecker()

  def __bool__(self):
    # If Containers(type(x)) is true, ZopeGuard checks will short circuit,
    # thinking it's a simple type, but we don't want this for type, because
    # type(x) is type for classes, being trueish would skip security check on
    # classes.
    return False
  __nonzero__ = __bool__ # six.PY2

ContainerAssertions[type] = TypeAccessChecker()


class SafeIterItems(SafeIter):

    def __next__(self):
        try:
            ob = self._next()     # AccessControl 2.13
        except AttributeError:
            ob = next(self._iter) # AccessControl 4.x
        c = self.container
        guard(c, ob[0])
        guard(c, ob[1])
        return ob
    next = __next__ # six.PY2

def get_iteritems(c, name):
    return lambda: SafeIterItems(six.iteritems(c), c)
_dict_white_list['iteritems'] = get_iteritems

import past.builtins # six.PY2
allow_module('past.builtins')
ModuleSecurityInfo('past.builtins').declarePublic('cmp')

if six.PY2:
    def guarded_sorted(seq, cmp=None, key=None, reverse=False):
        if cmp is not None:
            from functools import cmp_to_key
            key = cmp_to_key(cmp)

        if not isinstance(seq, SafeIter):
            for i, x in enumerate(seq):
                guard(seq, x, i)
        return sorted(seq, key=key, reverse=reverse)
    safe_builtins['sorted'] = guarded_sorted

def guarded_enumerate(seq, start=0):
    return NullIter(enumerate(guarded_iter(seq), start=start))
safe_builtins['enumerate'] = guarded_enumerate

def guarded_reversed(seq):
    return SafeIter(reversed(seq))
safe_builtins['reversed'] = guarded_reversed
ContainerAssertions[reversed] = 1
# listreverseiterator is a special type, returned by list.__reversed__
ContainerAssertions[type(reversed([]))] = 1


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

ContainerAssertions[types.GeneratorType] = 1

from collections import OrderedDict
ModuleSecurityInfo('collections').declarePublic('OrderedDict')

from collections import defaultdict
ModuleSecurityInfo('collections').declarePublic('defaultdict')

from collections import Counter
ModuleSecurityInfo('collections').declarePublic('Counter')


def allow_full_write(t):
  """Allow setattr, setitem, delattr and delitem for this type.

  This supports both RestrictedPython-3.6.0, where the safetype is implemented as:

      safetype = {dict: True, list: True}.has_key
      ...
      safetype(t)

  and RestrictedPython-5.1, where the safetype is implemented as:

      safetypes = {dict, list}
      ...
      safetype(t)

  """
  # Modify 'safetype' dict in full_write_guard function of RestrictedPython
  # (closure) directly to allow write access (using __setattr__ and __delattr__)
  from RestrictedPython.Guards import full_write_guard
  safetype = full_write_guard.__closure__[1].cell_contents
  if isinstance(safetype, set): # 5.1
    safetype.add(t)
  else: # 3.6
    safetype.__self__.update({t: True})


from AccessControl.ZopeGuards import _dict_white_list

# Attributes cannot be set on defaultdict, thus ignore defaultdict like dict/list
from RestrictedPython.Guards import full_write_guard
ContainerAssertions[defaultdict] = _check_access_wrapper(defaultdict, _dict_white_list)
allow_full_write(defaultdict)

# On Python2 only: In contrary to builtins such as dict/defaultdict, it is
# possible to set attributes on OrderedDict instances, so only allow
# setitem/delitem
ContainerAssertions[OrderedDict] = _check_access_wrapper(OrderedDict, _dict_white_list)
if six.PY2:
  OrderedDict.__guarded_setitem__ = OrderedDict.__setitem__.__func__
  OrderedDict.__guarded_delitem__ = OrderedDict.__delitem__.__func__
else:
  allow_full_write(OrderedDict)

_counter_white_list = copy.copy(_dict_white_list)
_counter_white_list['most_common'] = 1
ContainerAssertions[Counter] = _check_access_wrapper(Counter, _counter_white_list)
Counter.__guarded_setitem__ = dict.__setitem__
Counter.__guarded_delitem__ = dict.__delitem__

ModuleSecurityInfo('collections').declarePublic('namedtuple')

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

allow_module('io')
import io
allow_type(io.BytesIO)
allow_type(io.StringIO)
if six.PY2:
  allow_module('StringIO')
  import StringIO
  StringIO.StringIO.__allow_access_to_unprotected_subobjects__ = 1
  allow_module('cStringIO')
  import cStringIO
  allow_type(cStringIO.InputType)
  allow_type(cStringIO.OutputType)

ModuleSecurityInfo('cgi').declarePublic('escape', 'parse_header')
allow_module('datetime')
import datetime
ContainerAssertions[datetime.datetime] = 1
ContainerAssertions[datetime.time] = 1
ContainerAssertions[datetime.date] = 1
ContainerAssertions[datetime.timedelta] = 1
ContainerAssertions[datetime.tzinfo] = 1
# ContainerAssertions allows instance methods but not class attributes,
# so allowing them by allow_class_attribute(cls).
# Ex: datetime.datetime.now(), datetime.datetime.max are class attributes.
allow_class_attribute(datetime.datetime)
allow_class_attribute(datetime.date)
allow_class_attribute(datetime.time)
allow_class_attribute(datetime.timedelta)
allow_class_attribute(datetime.tzinfo)

# We need special care for datetime.datetime.strptime() in Python 2.7.
# It is because datetime.datetime.strptime() imports _strptime by C function
# PyImport_Import which calls
# __import__(name, globals, locals, fromlist=['__doc__'], level=0).
# The "level=0" is not supported by AccessControl in Zope2. At the same time,
# the dummy from '__doc__'  is neither allowed in it by default.
# Therefore we import _strptime in advance in this file.
# This prevents both importing _strptime with level=0, and accessing __doc__,
# when calling datetime.datetime.strptime().
import _strptime
# on python3 it seems we actually need to call strptime for this.
datetime.datetime.strptime('', '')

# Allow dict.fromkeys, Only this method is a class method in dict module.
allow_class_attribute(dict, {'fromkeys': 1})

allow_module('difflib')
allow_module('hashlib')
import hashlib
# XXX: assumes all hash types share the same base class (this is at least true
# for md5 and sha1/224/256/384/512)
allow_type(type(hashlib.md5()))
allow_module('time')
allow_module('unicodedata')

if six.PY2:
  import urlparse
  allow_module('urlparse')
  allow_type(urlparse.ParseResult)
  allow_type(urlparse.SplitResult)

  ModuleSecurityInfo('urllib').declarePublic(
    'urlencode',
    'quote', 'unquote',
    'quote_plus', 'unquote_plus',
  )
import six.moves.urllib.parse
allow_module('six.moves.urllib.parse')
allow_type(six.moves.urllib.parse.ParseResult)
allow_type(six.moves.urllib.parse.SplitResult)
# BBB this is different type on python3
allow_type(type(six.moves.urllib.parse.urldefrag('')))
ModuleSecurityInfo('six.moves.urllib.parse').declarePublic(
  'urlencode',
  'quote', 'unquote',
  'quote_plus', 'unquote_plus',
)

allow_module('struct')
allow_module('zlib')

ModuleSecurityInfo('bz2').declarePublic(
  'compress', 'decompress', 'BZ2Compressor', 'BZ2Decompressor',
)
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
  'collections': 'Products.ERP5Type.Collections',
  'six': 'Products.ERP5Type.Six',
  'pandas': 'Products.ERP5Type.Pandas',
}
for alias, real in six.iteritems(MNAME_MAP):
  assert '.' not in alias, alias # TODO: support this
  allow_module(real)
del alias, real
orig_guarded_import = safe_builtins['__import__']
try:
  from AccessControl.ZopeGuards import import_default_level # zope4py3
except ImportError:
  import_default_level = -1
def guarded_import(mname, globals=None, locals=None, fromlist=None,
    level=import_default_level):
  for fromname in fromlist or ():
    if fromname[:1] == '_':
      raise Unauthorized(fromname)
  # ZODB Components must be imported beforehand as ModuleSecurityInfo() may be
  # called there and AccessControl secureModule() expects to find the module
  # in _moduleSecurity dict. Also, import loader will fill MNAME_MAP.
  if mname.startswith('erp5.component.'):
      # Call find_load_module() to log errors as this will always raise
      # Unauthorized error without details
      #
      # XXX: pkgutil.get_loader() only works with '__path__'
      import erp5.component
      _, _, package_name, module_name = mname.split('.', 3)
      try:
          component_package = getattr(erp5.component, package_name)
      except AttributeError:
          raise Unauthorized(mname)
      if component_package.find_load_module(module_name) is None:
          raise Unauthorized(mname)
  if mname in MNAME_MAP:
    mname = MNAME_MAP[mname]
    if not fromlist:
      # fromlist value is meaningless but required. See __import__ doc.
      fromlist = ['__name__']
  return orig_guarded_import(mname, globals, locals, fromlist, level)
safe_builtins['__import__'] = guarded_import

ModuleSecurityInfo('transaction').declarePublic('doom')

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

from random import SystemRandom
allow_type(SystemRandom)
from random import Random
allow_type(Random)
ModuleSecurityInfo('os').declarePublic('urandom')

#
# backport from wendelin
#
# we need to allow access to numpy's internal types
import numpy as np
allow_module('numpy')
allow_module('numpy.lib.recfunctions')
for dtype in ('int8', 'int16', 'int32', 'int64', \
              'uint8', 'uint16', 'uint32', 'uint64', \
              'float16', 'float32', 'float64', \
              'complex64', 'complex128'):
  z = np.array([0,], dtype = dtype)
  allow_type(type(z[0]))
  allow_type(type(z))

  sz = np.array([(0,)], dtype = [('f0', dtype)])
  allow_type(type(sz[0]))
  allow_type(type(sz))

  rz = np.rec.array(np.array([(0,)], dtype = [('f0', dtype)]))
  allow_type(type(rz[0]))
  allow_type(type(rz))

# TODO zope4py3
#allow_type(np.dtype)
allow_type(np.timedelta64)
allow_type(type(np.c_))
# TODO zope4py3
#allow_type(type(np.dtype('int16')))
sz = np.array([('2017-07-12T12:30:20',)], dtype=[('date', 'M8[s]')])
allow_type(type(sz[0]['date']))

allow_full_write(np.ndarray)
allow_full_write(np.core.records.recarray)
allow_full_write(np.core.records.record)

def restrictedMethod(s,name):
  def dummyMethod(*args, **kw):
    raise Unauthorized(name)
  return dummyMethod


try:
  import pandas as pd
except ImportError:
  pass
else:
  allow_type(pd.Timestamp)
  allow_type(pd.DatetimeIndex)
  allow_type(pd.MultiIndex)
  allow_type(pd.Index)
  try:                    # for pandas >= 0.20.x
    allow_type(pd.RangeIndex)
  except AttributeError:  # BBB for pandas < 0.20.x
    allow_type(pd.indexes.range.RangeIndex)
  try:                    # for pandas >= 0.20.x
    allow_type(pd.Int64Index)
  except AttributeError:  # BBB for pandas < 0.20.x
    allow_type(pd.indexes.numeric.Int64Index)
  allow_type(pd.core.groupby.DataFrameGroupBy)
  allow_type(pd.core.groupby.SeriesGroupBy)
  try:                    # for pandas >= 0.20.x
    from pandas.core.resample import (
      TimedeltaIndexResampler, DatetimeIndexResampler, PeriodIndexResampler
    )
  except ImportError:  # BBB for pandas < 0.20.x
    from pandas.tseries.resample import (
      TimedeltaIndexResampler, DatetimeIndexResampler, PeriodIndexResampler
    )
  allow_type(TimedeltaIndexResampler)
  allow_type(DatetimeIndexResampler)
  allow_type(PeriodIndexResampler)

  allow_class(pd.DataFrame)

  # Note: These black_list methods are for pandas 0.19.2
  series_black_list = ('to_csv', 'to_json', 'to_pickle', 'to_hdf',
                       'to_sql', 'to_msgpack')
  ContainerAssertions[pd.Series] = _check_access_wrapper(
    pd.Series, dict.fromkeys(series_black_list, restrictedMethod))

  pandas_black_list = ('read_pickle', 'read_hdf',
                       'read_excel', 'read_html', 'read_msgpack',
                       'read_gbq', 'read_sas', 'read_stata')
  ModuleSecurityInfo(MNAME_MAP['pandas']).declarePrivate(*pandas_black_list)

  dataframe_black_list = ('to_csv', 'to_json', 'to_pickle', 'to_hdf',
                          'to_excel', 'to_html', 'to_sql', 'to_msgpack',
                          'to_latex', 'to_gbq', 'to_stata')
  ContainerAssertions[pd.DataFrame] = _check_access_wrapper(
    pd.DataFrame, dict.fromkeys(dataframe_black_list, restrictedMethod))

  allow_full_write(pd.DataFrame)
  allow_full_write(pd.Series)
  try:                    # for pandas >= 0.20.x
    pd_DatetimeIndex = pd.DatetimeIndex
  except AttributeError:  # BBB for pandas < 0.20.x
    pd_DatetimeIndex = pd.tseries.index.DatetimeIndex
  allow_full_write(pd_DatetimeIndex)
  allow_full_write(pd.core.indexing._iLocIndexer)
  allow_full_write(pd.core.indexing._LocIndexer)
  allow_full_write(pd.MultiIndex)
  allow_full_write(pd.Index)

# pytz exceptions are sometimes needed when using pandas
# see https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.tz_localize.html
for e in 'UnknownTimeZoneError InvalidTimeError AmbiguousTimeError NonExistentTimeError'.split():
  ModuleSecurityInfo('pytz').declarePublic(e)

import ipaddress
allow_module('ipaddress')
allow_type(ipaddress.IPv4Address)
allow_type(ipaddress.IPv6Address)
allow_type(ipaddress.IPv4Network)
allow_type(ipaddress.IPv6Network)
allow_type(ipaddress.IPv4Interface)
allow_type(ipaddress.IPv6Interface)
