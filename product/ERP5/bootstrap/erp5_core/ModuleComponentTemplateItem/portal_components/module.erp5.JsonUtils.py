# -*- coding: utf-8 -*-
#############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

from AccessControl import ModuleSecurityInfo
import six
import json

security = ModuleSecurityInfo(__name__)
security.declarePublic('loadJson')

# On python2, make sure we use UTF-8 strings for the json schemas, so that we don't
# have ugly u' prefixes in the reprs. This also transforms the collections.OrderedDict
# to simple dicts, because the former also have an ugly representation.
# http://stackoverflow.com/a/13105359
if six.PY2:

  def byteify(string):
    if isinstance(string, dict):
      return {
        byteify(key): byteify(value)
        for key, value in string.iteritems()
      }
    elif isinstance(string, list):
      return [byteify(element) for element in string]
    elif isinstance(string, tuple):
      return tuple(byteify(element) for element in string)
    elif isinstance(string, six.text_type):
      return string.encode('utf-8')
    else:
      return string
else:

  def byteify(x):
    return x


def loadJson(*args, **kw):
  return byteify(json.loads(*args, **kw))
