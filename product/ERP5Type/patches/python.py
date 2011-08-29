# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import os, sys, types

if sys.version_info < (2, 5):
  import __builtin__, imp

  def all(iterable):
    """
    Return True if bool(x) is True for all values x in the iterable.
    """
    for x in iterable:
      if not x:
        return False
    return True
  __builtin__.all = all

  def any(iterable):
    """
    Return True if bool(x) is True for any x in the iterable.
    """
    for x in iterable:
      if x:
        return True
    return False
  __builtin__.any = any

  import md5, sha
  sys.modules['hashlib'] = hashlib = imp.new_module('hashlib')
  hashlib.md5 = md5.new
  hashlib.sha1 = sha.new

  import email.Utils
  sys.modules['email.utils'] = email.Utils

  # A business template exported by Python 2.4 may contain:
  # <klass>
  #   <global id="xxx" name="_compile" module="sre"/>
  # </klass>
  #
  # A business template exported by Python 2.6 may contain:
  # <klass>
  #   <global id="xxx" name="_compile" module="re"/>
  # </klass>
  #
  # Python 2.6 provides 'sre._compile', but Python 2.4 does not provide
  # 're._compile', so we provide re._compile here for the backward
  # compatilibility.

  import re, sre
  re._compile = sre._compile

  # Monkey-patch pprint to sort keys of dictionaries
  class _ordered_dict(dict):
    def iteritems(self):
      return sorted(self.items())

  import pprint as _pprint
  orig_safe_repr = _pprint._safe_repr
  def _safe_repr(object, context, maxlevels, level):
    if type(object) is dict:
      object = _ordered_dict(object)
    return orig_safe_repr(object, context, maxlevels, level)
  _pprint._safe_repr = _safe_repr


if sys.version_info < (2, 6):

  try:
    import simplejson as json
  except ImportError, missing_simplejson:
    class dummy(types.ModuleType):
      def __getattr__(self, name):
        raise missing_simplejson
    json = dummy('dummy_json')
  sys.modules['json'] = json


if sys.version_info < (2, 7):

  try:
    from ordereddict import OrderedDict
  except ImportError, missing_ordereddict:
    def OrderedDict(*args, **kw):
      raise missing_ordereddict
  import collections
  collections.OrderedDict = OrderedDict


# Workaround bad use of getcwd() in docutils.
# Required by PortalTransforms.transforms.rest
from docutils import utils
utils.relative_path = lambda source, target: os.path.abspath(target)
