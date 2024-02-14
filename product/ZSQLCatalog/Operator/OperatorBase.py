##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
# Copyright (c) 2007-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Vincent Pelletier <vincent@nexedi.com>
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
import six
from six import string_types as basestring
from zLOG import LOG
from DateTime import DateTime
from Products.ZSQLCatalog.interfaces.operator import IOperator
from Products.ZSQLCatalog.Utils import sqlquote as escapeString
from AccessControl.ZopeGuards import SafeIter
from zope.interface.verify import verifyClass
from zope.interface import implementer

def valueFloatRenderer(value):
  if isinstance(value, basestring):
    value = float(value.replace(' ', ''))
  return repr(value)

def valueDateTimeRenderer(value):
  return '"%s"' % (value.toZone('UTC').ISO(), )

def valueDefaultRenderer(value):
  LOG('OperatorBase', 0, 'Unhandled value class: %s (%r). Converted to string and escaped.' % (value.__class__.__name__, value))
  return escapeString(str(value))

def valueNoneRenderer(value):
  return 'NULL'

def valueUnsupportedRenderer(value):
  raise TypeError("ZSQCatalog does not support %s (%s)" % (type(value), value))

value_renderer = {
  int: str,
  float: valueFloatRenderer,
  DateTime: valueDateTimeRenderer,
  None.__class__: valueNoneRenderer,
  bool: int,
  str: escapeString,
  SafeIter: valueUnsupportedRenderer,
  type(six.iterkeys({})): valueUnsupportedRenderer,
  type(six.iteritems({})): valueUnsupportedRenderer,
  type(six.itervalues({})): valueUnsupportedRenderer,
}
if six.PY2:
  value_renderer[long] = str
  value_renderer[unicode] = escapeString
else:
  value_renderer[bytes] = escapeString

value_search_text_renderer = {
  DateTime: str,
}

def valueDefaultSearchTextRenderer(value):
  """
    This is just repr, but always surrounding text strings with doublequotes.
  """
  if isinstance(value, basestring):
    result = '"%s"' % (value.replace('\\', '\\\\').replace('"', '\\"'), )
  else:
    result = repr(value)
  return result

def columnFloatRenderer(column, format=None):
  """Format a float column.

  'format' is a string describing the precision, in which '.' is used as
  decimal separator. The number of decimal places in this format string is used
  to search with this precision.

  For example column=0.12345, format='0.00' will match values equals to 0.12
  when truncated to 2 places.
  """
  if format is not None:
    if '.' in format:
      format = format.replace(' ', '')
      column = "TRUNCATE(%s, %s)" % (column, len(format.split('.')[-1]))
  return column

def columnDefaultRenderer(column, format=None):
  return column

column_renderer = {
  'float': columnFloatRenderer
}

@implementer(IOperator)
class OperatorBase(object):

  def __init__(self, operator, operator_search_text=None):
    self.operator = operator
    if operator_search_text is None:
      operator_search_text = operator
    self.operator_search_text = operator_search_text

  def getOperator(self):
    return self.operator

  def getOperatorSearchText(self):
    return self.operator_search_text

  def _render(self, column, value,
              value_renderer_get={k.__name__: v
                for k, v in six.iteritems(value_renderer)}.get):
    """
      Render given column and value for use in SQL.
      Value is rendered to convert it to SQL-friendly value.
      Column is rendered to include possible cast code.

      column (string)
        Column on which the value will be matched
      value (see _renderValue)
        Value to render.
    """
    if isinstance(value, dict):
      type = value['type']
      column = column_renderer.get(type, columnDefaultRenderer)(column, format=value['format'])
      value = value_renderer_get(type, valueDefaultRenderer)(value['query'])
    else:
      value = self._renderValue(value)
    return column, value

  def _renderValue(self, value,
                   value_renderer_get=value_renderer.get,
                   valueDefaultRenderer=valueDefaultRenderer):
    """
      Render given value as string.

      value (int, float, long, DateTime, string, None)
        Value to render as a string for use in SQL (quoted, escaped).
    """
    return value_renderer_get(value.__class__, valueDefaultRenderer)(value)

  def asSearchText(self, value):
    return value_search_text_renderer.get(value.__class__,
                                          valueDefaultSearchTextRenderer)(value)

  def asSQLExpression(self, column, value_list, only_group_columns):
    raise NotImplementedError('This method must be overloaded by a subclass'
      ' to be able to get an SQL representation of this operator.')

  def __repr__(self):
    return '<%s(%r) at %s>' % (self.__class__.__name__, self.getOperator(), id(self))

verifyClass(IOperator, OperatorBase)

