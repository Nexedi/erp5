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

# TODO: remove the special OPERATOR case: it does not work when there are both a valid and an invalid operator

class AdvancedSearchTextDetector(lexer):

  def t_OPERATOR(self, t):
    r'(>=?|<=?|!?=)[ ]*'
    return t

  def t_LEFT_PARENTHESE(self, t):
    self.found = True
    t.type = 'WORD'
    return t

  def t_STRING(self, t):
    self.found = True
    t.type = 'WORD'
    return t

  def t_COLUMN(self, t):
    self.found = t.value[:-1] in self.column_id_set
    t.type = 'WORD'
    return t

  def t_OR(self, t):
    self.found = True
    t.type = 'WORD'
    return t

  def t_AND(self, t):
    self.found = True
    t.type = 'WORD'
    return t

  def t_NOT(self, t):
    self.found = True
    t.type = 'WORD'
    return t

  def p_search_text(self, p):
    '''search_text : value
                   | value search_text'''
    if len(p) == 2:
      p[0] = p[1]
    else:
      p[0] = p[1] or p[2]

  def p_value(self, p):
    '''value : WORD
             | OPERATOR WORD'''
    p[0] = len(p) == 3 and ' ' not in p[1]

  tokens = (
    'WORD',
    'OPERATOR')

  def real_token(self):
    return lexer.token(self)

  def token(self):
    return self.token_list.pop(0)

  def __call__(self, input, column_id_set):
    self.column_id_set = column_id_set
    self.found = False
    check_grammar = False
    self.token_list = token_list = []
    append = token_list.append
    self.input(input)
    while not self.found:
      token = self.real_token()
      append(token)
      if token is None:
        break
      if token.type == 'OPERATOR':
        check_grammar = True
    if not self.found and check_grammar:
      self.found = self.parse()
    return self.found

update_docstrings(AdvancedSearchTextDetector)

