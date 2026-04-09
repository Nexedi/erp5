##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type.Utils import bytes2str

def _mysql_sqlquote_fallback(value):
  """
  MySQL-specific string quoting fallback, used when no database connection
  is available (e.g. in unit tests). Only correct for MySQL-compatible backends.
  """
  if isinstance(value, bytes):
    value = bytes2str(value)
  return "'" + (value
    .replace('\x5c', r'\\')
    .replace('\x00', r'\0')
    .replace('\x08', r'\b')
    .replace('\x09', r'\t')
    .replace('\x0a', r'\n')
    .replace('\x0d', r'\r')
    .replace('\x1a', r'\Z')
    .replace('\x22', r'\"')
    .replace('\x27', r"\'")
  ) + "'"

def sqlquote(value, sql_quote):
  result = sql_quote(value)
  # sql_quote__ from some DA implementations (e.g. ZMySQLDA) returns bytes;
  # others (e.g. SQLite DA or our fallback) return str.
  if isinstance(result, bytes):
    return bytes2str(result)
  return result
