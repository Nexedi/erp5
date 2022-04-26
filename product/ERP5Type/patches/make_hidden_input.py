##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.

#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""
Close properly the <input /> tag
"""

import ZTUtils.Zope
from ZTUtils.Zope import complex_marshal
import cgi

def make_hidden_input(*args, **kwargs):
  '''Construct a set of hidden input elements, with marshalling markup.

  If there are positional arguments, they must be dictionaries.
  They are combined with the dictionary of keyword arguments to form
  a dictionary of query names and values.

  Query names (the keys) must be strings.  Values may be strings,
  integers, floats, or DateTimes, and they may also be lists or
  namespaces containing these types.  All arguments are marshalled with
  complex_marshal().
  '''

  d = {}
  for arg in args:
      d.update(arg)
  d.update(kwargs)

  hq = lambda x:cgi.escape(x, quote=True)
  qlist = complex_marshal(list(d.items()))
  for i in range(len(qlist)):
      k, m, v = qlist[i]
      qlist[i] = ('<input type="hidden" name="%s%s" value="%s" />'
                  % (hq(k), m, hq(str(v))))

  return '\n'.join(qlist)

ZTUtils.Zope.make_hidden_input = make_hidden_input
ZTUtils.make_hidden_input = make_hidden_input

