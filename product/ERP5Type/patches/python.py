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


if 1:
    # Speed up email parsing (see also http://bugs.python.org/issue1243730)
    from email import Parser as parser, FeedParser as feedparser # BBB

    NLCRE_crack_split = feedparser.NLCRE_crack.split
    def push(self, data):
        """Push some new data into this object."""
        # <patch>
        if self._partial[-1:] == '\r':
            parts = NLCRE_crack_split('\r' + data)
            parts[0] = self._partial[:-1]
        else:
            parts = NLCRE_crack_split(data)
            parts[0] = self._partial + parts[0]
        # </patch>
        # The *ahem* interesting behaviour of re.split when supplied grouping
        # parentheses is that the last element of the resulting list is the
        # data after the final RE.  In the case of a NL/CR terminated string,
        # this is the empty string.
        self._partial = parts.pop()
        #GAN 29Mar09  bugs 1555570, 1721862  Confusion at 8K boundary ending with \r:
        # is there a \n to follow later?
        if not self._partial and parts and parts[-1].endswith('\r'):
            self._partial = parts.pop(-2)+parts.pop()
        # parts is a list of strings, alternating between the line contents
        # and the eol character(s).  Gather up a list of lines after
        # re-attaching the newlines.
        lines = []
        for i in range(len(parts) // 2):
            lines.append(parts[i*2] + parts[i*2+1])
        self.pushlines(lines)
    feedparser.BufferedSubFile.push = push

    FeedParser = feedparser.FeedParser
    def parse(self, fp, headersonly=False):
        """Create a message structure from the data in a file.

        Reads all the data from the file and returns the root of the message
        structure.  Optional headersonly is a flag specifying whether to stop
        parsing after reading the headers or not.  The default is False,
        meaning it parses the entire contents of the file.
        """
        feedparser = FeedParser(self._class)
        if headersonly:
            feedparser._set_headersonly()
        while True:
            # <patch>
            data = fp.read(65536)
            # </patch>
            if not data:
                break
            feedparser.feed(data)
        return feedparser.close()
    parser.Parser.parse = parse


# Workaround bad use of getcwd() in docutils.
# Required by PortalTransforms.transforms.rest
from docutils import utils
utils.relative_path = lambda source, target: os.path.abspath(target)
