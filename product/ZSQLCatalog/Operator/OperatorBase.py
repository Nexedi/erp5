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

from zLOG import LOG
from Products.ZSQLCatalog.interfaces.operator import IOperator
from Interface.Verify import verifyClass
from Products.ZSQLCatalog.SQLCatalog import profiler_decorator

@profiler_decorator
def escapeString(value):
  # Inspired from ERP5Type/Utils:sqlquote, but this product must not depend on it.
  return "'" + value.replace('\\', '\\\\').replace("'", "''") + "'"

@profiler_decorator
def valueFloatRenderer(value):
  if isinstance(value, basestring):
    value = float(value.replace(' ', ''))
  return repr(value)

@profiler_decorator
def valueDateTimeRenderer(value):
  return '"%s"' % (value.toZone('UTC').ISO(), )

@profiler_decorator
def valueDefaultRenderer(value):
  LOG('OperatorBase', 0, 'Unhandled value class: %s (%r). Converted to string and escaped.' % (value.__class__.__name__, value))
  return escapeString(str(value))

@profiler_decorator
def valueNoneRenderer(value):
  return 'NULL'

value_renderer = {
  'int': str,
  'long': str,
  'float': valueFloatRenderer,
  'DateTime': valueDateTimeRenderer,
  'NoneType': valueNoneRenderer,
}

value_search_text_renderer = {
  'DateTime': str,
}

@profiler_decorator
def valueDefaultSearchTextRenderer(value):
  """
    This is just repr, but always surrounding text strings with doublequotes.
  """
  if isinstance(value, basestring):
    result = '"%s"' % (value.replace('\\', '\\\\').replace('"', '\\"'), )
  else:
    result = repr(value)
  return result

@profiler_decorator
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

@profiler_decorator
def columnDefaultRenderer(column, format=None):
  return column

column_renderer = {
  'float': columnFloatRenderer
}

class OperatorBase(object):

  __implements__ = IOperator

  def __init__(self, operator, operator_search_text=None):
    self.operator = operator
    if operator_search_text is None:
      operator_search_text = operator
    self.operator_search_text = operator_search_text

  def getOperator(self):
    return self.operator

  def getOperatorSearchText(self):
    return self.operator_search_text

  @profiler_decorator
  def _render(self, column, value):
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
      value = value_renderer.get(type, valueDefaultRenderer)(value['query'])
    else:
      value = self._renderValue(value)
    return column, value

  @profiler_decorator
  def _renderValue(self, value):
    """
      Render given value as string.

      value (int, float, long, DateTime, string, None)
        Value to render as a string for use in SQL (quoted, escaped).
    """
    if isinstance(value, basestring):
      value = escapeString(value)
    else:
      value = value_renderer.get(value.__class__.__name__, valueDefaultRenderer)(value)
    return value

  @profiler_decorator
  def asSearchText(self, value):
    return value_search_text_renderer.get(value.__class__.__name__, valueDefaultSearchTextRenderer)(value)

  def asSQLExpression(self, column, value_list, only_group_columns):
    raise NotImplementedError, 'This method must be overloaded by a subclass ' \
      'to be able to get an SQL representation of this operator.'

  def __repr__(self):
    return '<%s(%r) at %s>' % (self.__class__.__name__, self.getOperator(), id(self))

verifyClass(IOperator, OperatorBase)

