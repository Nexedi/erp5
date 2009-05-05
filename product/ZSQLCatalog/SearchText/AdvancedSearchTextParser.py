##############################################################################
#
# Copyright (c) 2008-2009 Nexedi SA and Contributors. All Rights Reserved.
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

from lexer import lexer, update_docstrings
try:
  from Products.ZSQLCatalog.Interface.IAbstractSyntaxNode import INode, IValueNode, ILogicalNode, IColumnNode
  from Interface.Verify import verifyClass
except ImportError:
  INode = None
  IValueNode = None
  ILogicalNode = None
  IColumnNode = None
  def verifyClass(*args, **kw):
    pass

class Node(object):

  __implements__ = INode

  def isLeaf(self):
    return False

  def isColumn(self):
    return False

  def push(self, logical_operator, node):
    return LogicalNode(logical_operator, self, node)

verifyClass(INode, Node)

class ValueNode(Node):

  __implements__ = IValueNode

  def __init__(self, value, comparison_operator=''):
    self.value = value
    self.comparison_operator = comparison_operator

  def isLeaf(self):
    return True

  def getComparisonOperator(self):
    return self.comparison_operator

  def getValue(self):
    return self.value

  def __repr__(self):
    return '<%s %r %r>' % (self.__class__.__name__, self.comparison_operator, self.value)

verifyClass(INode, ValueNode)
verifyClass(IValueNode, ValueNode)

class NotNode(Node):

  __implements__ = ILogicalNode

  def __init__(self, node):
    self.node = node

  def getLogicalOperator(self):
    return 'not'

  def getNodeList(self):
    return [self.node]

  def __repr__(self):
    return '<%s %r>' % (self.__class__.__name__, self.node)

verifyClass(INode, NotNode)
verifyClass(ILogicalNode, NotNode)

class LogicalNode(Node):

  __implements__ = ILogicalNode

  def __init__(self, logical_operator, node, other):
    self.logical_operator = logical_operator
    self.node_list = []
    self._push(node)
    self._push(other)

  def getLogicalOperator(self):
    return self.logical_operator

  def getNodeList(self):
    return self.node_list

  def _push(self, node):
    if isinstance(node, LogicalNode) and node.logical_operator == self.logical_operator:
      self.node_list.extend(node.node_list)
    else:
      self.node_list.append(node)

  def __repr__(self):
    return '<%s %r %r>' % (self.__class__.__name__, self.logical_operator, self.node_list)

verifyClass(INode, LogicalNode)
verifyClass(ILogicalNode, LogicalNode)

class ColumnNode(Node):

  __implements__ = IColumnNode

  def __init__(self, column_name, node):
    self.column_name = column_name
    self.node = node

  def isColumn(self):
    return True

  def getColumnName(self):
    return self.column_name

  def getSubNode(self):
    return self.node

  def __repr__(self):
    return '<%s %r %r>' % (self.__class__.__name__, self.column_name, self.node)

verifyClass(INode, ColumnNode)
verifyClass(IColumnNode, ColumnNode)

class AdvancedSearchTextParser(lexer):

  # IMPORTANT:
  # In short: Don't remove any token definition below even if they look
  # useless.
  # In detail: The lex methods below are redefined here because of ply nice
  # feature of prioritizing tokens using the *line* *number* at which they
  # are defined. As we inherit those methods from another class from another
  # file (which doesn't match this file's content, of course) we must redefine
  # wrapper methods to enforce token priority. Kudos to ply for so much
  # customisable behaviour. Not.

  def t_LEFT_PARENTHESE(self, t):
    return lexer.t_LEFT_PARENTHESE(self, t)

  def t_RIGHT_PARENTHESE(self, t):
    return lexer.t_RIGHT_PARENTHESE(self, t)

  def t_OPERATOR(self, t):
    return lexer.t_OPERATOR(self, t)

  def t_STRING(self, t):
    return lexer.t_STRING(self, t)

  def t_COLUMN(self, t):
    if self.isColumn(t.value[:-1]):
      t = lexer.t_COLUMN(self, t)
    else:
      # t is a non-existing column, so it should be taken as a string prefix.
      t.type = 'STRING_PREFIX'
    return t

  def t_OR(self, t):
    return lexer.t_OR(self, t)

  def t_AND(self, t):
    return lexer.t_AND(self, t)

  def t_NOT(self, t):
    return lexer.t_NOT(self, t)

  def t_WORD(self, t):
    return lexer.t_WORD(self, t)

  def p_seach_text(self, p):
    '''search_text : and_expression
                   | and_expression OR search_text'''
    if len(p) == 2:
      p[0] = p[1]
    else:
      p[0] = p[1].push('or', p[3])

  def p_and_expression(self, p):
    '''and_expression : boolean_expression
                      | boolean_expression and_expression
                      | boolean_expression AND and_expression'''
    if len(p) == 2:
      p[0] = p[1]
    elif len(p) == 3:
      p[0] = p[1].push('and', p[2])
    else:
      p[0] = p[1].push('and', p[3])

  def p_boolean_expression(self, p):
    '''boolean_expression : NOT expression
                          | expression'''
    if len(p) == 3:
      p[0] = NotNode(p[2])
    else:
      p[0] = p[1]

  def p_expression(self, p):
    '''expression : LEFT_PARENTHESE search_text RIGHT_PARENTHESE
                  | column
                  | value'''
    if len(p) == 2:
      p[0] = p[1]
    else:
      p[0] = p[2]

  def p_column(self, p):
    '''column : COLUMN value_expression'''
    p[0] = ColumnNode(p[1], p[2])

  def p_value_expression(self, p):
    '''value_expression : LEFT_PARENTHESE value_or_expression RIGHT_PARENTHESE
                        | value'''
    if len(p) == 2:
      p[0] = p[1]
    else:
      p[0] = p[2]

  def p_value_or_expression(self, p):
    '''value_or_expression : value_and_expression
                           | value_and_expression value_or_expression
                           | value_and_expression OR value_or_expression'''
    if len(p) == 2:
      p[0] = p[1]
    elif len(p) == 3:
      p[0] = p[1].push('or', p[2])
    else:
      p[0] = p[1].push('or', p[3])

  def p_value_and_expression(self, p):
    '''value_and_expression : value_expression
                            | value_expression AND value_and_expression'''
    if len(p) == 2:
      p[0] = p[1]
    else:
      p[0] = p[1].push('and', p[3])

  def p_value(self, p):
    '''value : OPERATOR string
             | string'''
    if len(p) == 2:
      p[0] = ValueNode(p[1])
    else:
      p[0] = ValueNode(p[2], comparison_operator=p[1])

  def p_string(self, p):
    '''string : WORD
              | STRING
              | STRING_PREFIX string'''
    if len(p) == 3:
      p[0] = p[1] + p[2]
    else:
      p[0] = p[1]

  def __call__(self, input, is_column, *args, **kw):
    self.isColumn = is_column
    try:
      return self.parse(input, *args, **kw)
    finally:
      self.isColumn = None

update_docstrings(AdvancedSearchTextParser)

