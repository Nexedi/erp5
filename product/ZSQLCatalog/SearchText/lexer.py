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

from ply import lex, yacc
import os
import sys
from cStringIO import StringIO

try:
  from zLOG import LOG
except ImportError:
  def LOG(channel, level, message):
    print >>sys.stderr, message

module_path = os.path.dirname(os.path.abspath(__file__))

class ParserOrLexerError(Exception):
  pass

class LexerError(ParserOrLexerError):
  pass

class ParserError(ParserOrLexerError):
  pass

class lexer(object):
  def init(self, **kw):
    debug = kw.pop('debug', False)
    # Catch all logs with a cStringIO
    output = sys.stdout = sys.stderr = StringIO()
    self.lexer = lex.lex(object=self, **kw)
    self.parser = yacc.yacc(module=self, debug=debug,
                            debugfile="%s.out" % (self.__class__.__name__, ),
                            tabmodule="%s_parsetab" % (self.__class__.__name__, ),
                            outputdir=module_path)
    sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
    # Emit all logs with regular Zope logging
    for line in output.getvalue().split('\n'):
      if len(line):
        LOG('lexer', 0, line)

  def t_error(self, t):
    raise LexerError, 'ERROR: Invalid character %r' % (t.value[0], )

  def p_error(self, p):
    raise ParserError, 'Syntax error in input: %r' % (p, )

  def input(self, string):
    self.lexer.input(string)

  def token(self):
    return self.lexer.token()

  tokens = (
    'OR',
    'AND',
    'NOT',
    'COLUMN',
    'STRING',
    'WORD',
    'OPERATOR',
    'LEFT_PARENTHESE',
    'RIGHT_PARENTHESE')

  t_ignore = ' '

  def t_LEFT_PARENTHESE(self, t):
    r'\('
    return t

  def t_RIGHT_PARENTHESE(self, t):
    r'\)'
    return t

  def t_OPERATOR(self, t):
    r'(>=?|<=?|!?=)'
    return t

  def t_STRING(self, t):
    r'"(\\.|[^\\"])*"'
    # Unescape value and strip surrounding quotes
    value_list = []
    append = value_list.append
    escaped = False
    for char in t.value[1:-1]:
      if escaped:
        escaped = False
        if char != '"':
          append('\\')
      else:
        if char == '\\':
          escaped = True
          continue
      append(char)
    assert not escaped
    t.value = ''.join(value_list)
    return t

  def t_COLUMN(self, t):
    r'[^><= :\(\)"][^ :\(\)"]*:'
    t.value = t.value[:-1]
    return t

  def t_OR(self, t):
    r'OR'
    return t

  def t_AND(self, t):
    r'AND'
    return t

  def t_NOT(self, t):
    r'NOT'
    return t

  def t_WORD(self, t):
    r'[^><= :\(\)"][^ :\(\)"]*'
    return t

  def parse(self, *args, **kw):
    kw['lexer'] = self
    return self.parser.parse(*args, **kw)

  __call__ = parse

def update_docstrings(klass):
  for property in dir(klass):
    if property.startswith('t_'):
      source = getattr(lexer, property, None)
      if callable(source):
        destination = getattr(klass, property)
        assert callable(destination)
        if destination.__doc__ is None:
          destination.im_func.__doc__ = source.__doc__

