#!/usr/bin/python
# -*- coding: utf8 -*-
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

import threading
from AdvancedSearchTextDetector import AdvancedSearchTextDetector
from AdvancedSearchTextParser import AdvancedSearchTextParser
from lexer import ParserOrLexerError
try:
  from Products.ZSQLCatalog.SQLCatalog import profiler_decorator
except ImportError:
  def profiler_decorator(funct):
    return funct

if __name__ == '__main__':
  DEBUG = 1
else:
  DEBUG = 0

parser_pool = threading.local()

@profiler_decorator
def getAdvancedSearchTextDetector():
  try:
    return parser_pool.advanced_search_text_detector
  except AttributeError:
    advanced_search_text_detector = AdvancedSearchTextDetector()
    advanced_search_text_detector.init(debug=DEBUG)
    parser_pool.advanced_search_text_detector = advanced_search_text_detector
    return advanced_search_text_detector

@profiler_decorator
def getAdvancedSearchTextParser():
  try:
    return parser_pool.parser
  except AttributeError:
    parser = AdvancedSearchTextParser()
    parser.init(debug=DEBUG)
    parser_pool.parser = parser
    return parser

@profiler_decorator
def _parse(input, is_column, *args, **kw):
  if getAdvancedSearchTextDetector()(input, is_column):
    result = getAdvancedSearchTextParser()(input, *args, **kw)
  else:
    result = None
  return result

@profiler_decorator
def parse(*args, **kw):
  try:
    result = _parse(*args, **kw)
  except (KeyboardInterrupt, SystemExit):
    raise
  except:
    result = None
  return result

if __name__ == '__main__':
  class Query:
    def __init__(self, column, value, comparison_operator='='):
      self.column = column
      self.comparison_operator = comparison_operator
      if isinstance(value, (list, tuple)):
        value = ''.join(value)
      self.value = value

    def asTuple(self):
      return (self.column, self.value, self.comparison_operator)

    def __repr__(self):
      value = self.value
      if len(value) == 1:
        value = value[0]
      return 'Query(%r, %r, %r)' % (self.column, value, self.comparison_operator)

    def __eq__(self, other):
      if isinstance(other, Query):
        return self.asTuple() == other.asTuple()
      else:
        return False

    def __ne__(self, other):
      return not (self == other)

  class ComplexQuery:
    def __init__(self, query_list, operator):
      self.operator = operator
      self.query_list = query_list

    def __repr__(self):
      return 'ComplexQuery(%r, operator=%r)' % (self.query_list, self.operator)

    def __eq__(self, other):
      if isinstance(other, ComplexQuery):
        if self.operator != other.operator:
          return False
        other_query_list = other.query_list[:]
        for my_query in self.query_list:
          for other_index in xrange(len(other_query_list)):
            other_query = other_query_list[other_index]
            if my_query == other_query:
              other_query_list.pop(other_index)
              break
          else:
            return False
        return len(other_query_list) == 0
      else:
        return False

    def __ne__(self, other):
      return not (self == other)

  check_list = [
    ('foo', None),
    ('foo bar', None),
    ('foo   bar', None),
    ('foo%', None),
    ('%foo', None),
    ('%foo%', None),
    ('foo%bar', None),
    ('foo% bar', None),
    ('foo %bar', None),
    ('foo and bar', None),
    ('foo or bar', None),
    ('foo - bar', None),
    ('foo- bar', None),
    ('!-1', None),
    ('->1', None),
    ('+=1', None),
    ('jean-paul', None),
    ('JeanAndPaul', None),
    ('totoORtata', None),
    ('NORD', None),
    ('OR ARGENT', None),
    ('CUIVRE OR ARGENT', None), # XXX
    ('title :foo', None),
    ('-foo', None),
    ('foo -bar', None),
    ('+foo -bar', None),
    ('+1', None),
    ('-1', None),

    ('foo OR "-" OR bar OR -baz', ComplexQuery([Query(None, 'foo'), Query(None, '-'), Query(None, 'bar'), Query(None, '-baz')], operator='or')),
    ('foo "-" bar -baz',          ComplexQuery([Query(None, 'foo'), Query(None, '-'), Query(None, 'bar'), Query(None, '-baz')], operator='or')),
    ('title:foo',                 Query('title', 'foo')),
    ('title: foo',                Query('title', 'foo')),
    ('title:foo bar',             ComplexQuery([Query('title', 'foo'), Query(None, 'bar')], operator='or')),
    ('title:"foo bar"',           Query('title', 'foo bar')),
    ('"title:foo bar"',           Query(None, 'title:foo bar')),
    ('"foo bar"',                 Query(None, 'foo bar')),
    ('"foo   bar"',               Query(None, 'foo   bar')),
    ('foo AND bar',               ComplexQuery([Query(None, 'foo'), Query(None, 'bar')], operator='and')),
    ('foo OR bar',                ComplexQuery([Query(None, 'foo'), Query(None, 'bar')], operator='or')),
    ('"foo AND bar"',             Query(None, 'foo AND bar')),
    ('"foo and bar"',             Query(None, 'foo and bar')),
    ('"foo OR bar"',              Query(None, 'foo OR bar')),
    ('"foo or bar"',              Query(None, 'foo or bar')),
    ('"foo% bar"',                Query(None, 'foo% bar')),
    ('"foo %bar"',                Query(None, 'foo %bar')),
    ('>1',                        Query(None, '1', '>')),
    ('">1"',                      Query(None, '>1')),
    ('>a',                        Query(None, 'a', '>')),
    ('">a"',                      Query(None, '>a')),
    ('>1 0',                      ComplexQuery([Query(None, '1', '>'), Query(None, '0')], operator='or')),
    ('>=1',                       Query(None, '1', '>=')),
    ('>"=1"',                     Query(None, '=1', '>')),
    ('-"1"',                      ComplexQuery([Query(None, '-'), Query(None, '1')], operator='or')),
    ('"!-1"',                     Query(None, '!-1')),
#    (r"a:'tu:\'tu\''",            ['a', "tu:'tu'"]),
    (r'''b:"tu:\'tu\'"''',        Query('b', "tu:\\'tu\\'")),
    (r'''c:"tu:'tu'"''',          Query('c', "tu:'tu'")),
    (r'd:"tu:\"tu\""',            Query('d', 'tu:"tu"')),
    ('toto: tutu tutu',           ComplexQuery([Query('toto', 'tutu'), Query(None, 'tutu')], operator='or')),
    ('(tutu) (toto:tata)',        ComplexQuery([Query(None, 'tutu'), Query('toto', 'tata')], operator='or')),
    ('(tutu) (toto:"tata")',      ComplexQuery([Query(None, 'tutu'), Query('toto', 'tata')], operator='or')),
#    ('toto:',                     ['toto', '']),
    ('toto:""',                   Query('toto', '')),
#    ("''",                        ''),
    ('""',                        Query(None, '')),
    (r'"\""',                     Query(None, '"')),
    (r'"\n"',                     Query(None, '\\n')),
#こんにちは
    (u'ん',                       None),
    (u'(toto:ん) OR (titi:ん)',   ComplexQuery([Query('toto', u'ん'), Query('titi', u'ん')], operator='or')),
    ('ん',                        None),
    ('(toto:ん) OR (titi:ん)',    ComplexQuery([Query('toto', 'ん'), Query('titi', 'ん')], operator='or')),
    ('(foo)',                     Query(None, 'foo')),
    ('toto:(foo)',                Query('toto', 'foo')),
    ('(foo OR bar)',              ComplexQuery([Query(None, 'foo'), Query(None, 'bar')], operator='or')),
    ('(a AND b) OR (c AND (d OR e))',
                                  ComplexQuery([ComplexQuery([Query(None, 'a'), Query(None, 'b')], operator='and'), ComplexQuery([Query(None, 'c'), ComplexQuery([Query(None, 'd'), Query(None, 'e')], operator='or')], operator='and')], operator='or')),
    ('(foo:"") (bar:baz)',        ComplexQuery([Query('foo', ''), Query('bar', 'baz')], operator='or')),
    ('(foo:"") (OR:bar)',         ComplexQuery([Query('foo', ''), Query('OR', 'bar')], operator='or')),
#    ('foo: OR',                   ['foo', 'or']),
#    ('foo: OR ',                  ['foo', 'or']),
#    ('(foo:)',                    ['foo', '']),
    ('(foo: bar)',                Query('foo', 'bar')),
    ('(a:b) AND (c:d)',           ComplexQuery([Query('a', 'b'), Query('c', 'd')], operator='and')),
    ('a:(b c)',                   ComplexQuery([Query('a', 'b'), Query('a', 'c')], operator='or')),
    ('a:(b OR c)',                ComplexQuery([Query('a', 'b'), Query('a', 'c')], operator='or')),
    ('a:(b c d)',                 ComplexQuery([Query('a', 'b'), Query('a', 'c'), Query('a', 'd')], operator='or')),
    ('a:(b (c d))',               ComplexQuery([Query('a', 'b'), Query('a', 'c'), Query('a', 'd')], operator='or')),
    ('a:(b OR (c d))',            ComplexQuery([Query('a', 'b'), Query('a', 'c'), Query('a', 'd')], operator='or')),
    ('"JeanANDPaul"',             Query(None, 'JeanANDPaul')),
    ('"Jean" AND "Paul"',         ComplexQuery([Query(None, 'Jean'), Query(None, 'Paul')], operator='and')),
    ('"jean paul" OR "thierry"',  ComplexQuery([Query(None, 'jean paul'), Query(None, 'thierry')], operator='or')),
    ('title:Paul Jean Lili',      ComplexQuery([Query('title', 'Paul'), Query(None, 'Jean'), Query(None, 'Lili')], operator='or')),
    ('toto AND titi OR tutu AND tata OR toto',
                                  ComplexQuery([ComplexQuery([Query(None, 'toto'), Query(None, 'titi')], operator='and'), ComplexQuery([Query(None, 'tutu'), Query(None, 'tata')], operator='and'), Query(None, 'toto')], operator='or')),
    ('toto AND (titi OR tutu) AND tata OR toto',
                                  ComplexQuery([ComplexQuery([Query(None, 'toto'), ComplexQuery([Query(None, 'titi'), Query(None, 'tutu')], operator='or'), Query(None, 'tata')], operator='and'), Query(None, 'toto')], operator='or')),
    ('"OR ARGENT"',               Query(None, 'OR ARGENT')),
    ('1 AND 2 OR 3',              ComplexQuery([ComplexQuery([Query(None, '1'), Query(None, '2')], operator='and'), Query(None, '3')], operator='or')),
    ('1 OR 2 AND 3',              ComplexQuery([Query(None, '1'), ComplexQuery([Query(None, '2'), Query(None, '3')], operator='and')], operator='or')),
    ('1 AND 2 3',                 ComplexQuery([ComplexQuery([Query(None, '1'), Query(None, '2')], operator='and'), Query(None, '3')], operator='or')),
    ('1 2 AND 3',                 ComplexQuery([Query(None, '1'), ComplexQuery([Query(None, '2'), Query(None, '3')], operator='and')], operator='or')),
    ('10 11 OR 12 13',            ComplexQuery([Query(None, '10'), Query(None, '11'), Query(None, '12'), Query(None, '13')], operator='or')),
    ('((1 AND 2 OR 3) OR (4 AND 5 6) OR (7 8 AND 9) OR (10 11 OR 12 13))',
                                  ComplexQuery([ComplexQuery([Query(None, '1'), Query(None, '2')], operator='and'), Query(None, '3'), ComplexQuery([Query(None, '4'), Query(None, '5')], operator='and'), Query(None, '6'), Query(None, '7'), ComplexQuery([Query(None, '8'), Query(None, '9')], operator='and'), Query(None, '10'), Query(None, '11'), Query(None, '12'), Query(None, '13')], operator='or')),
    ('((titi:foo) AND (toto:bar)) OR ((titi:bar) AND (toto:foo))',
                                  ComplexQuery([ComplexQuery([Query('titi', 'foo'), Query('toto', 'bar')], operator='and'), ComplexQuery([Query('titi', 'bar'), Query('toto', 'foo')], operator='and')], operator='or')),
    ('title:(Paul Jean OR Lili)', ComplexQuery([Query('title', 'Paul'), Query('title', 'Jean'), Query('title', 'Lili')], operator='or')),
    ('title:Paul Jean OR Lili',   ComplexQuery([Query('title', 'Paul'), Query(None, 'Jean'), Query(None, 'Lili')], operator='or')),
  ]

  def walk(node, key=None):
    """
      Recusrively walk given AST and build ComplexQuery & Query instances for each node.
    """
    if node.isLeaf():
      comparison_operator = node.getComparisonOperator()
      if comparison_operator == '':
        comparison_operator = '='
      result = Query(key, node.getValue(), comparison_operator=comparison_operator)
    elif node.isColumn():
      result = walk(node.getSubNode(), node.getColumnName())
    else:
      query_list = [walk(x, key) for x in node.getNodeList()]
      operator = node.getLogicalOperator()
      if operator == 'not' or len(query_list) > 1:
        result = ComplexQuery(query_list, operator=operator)
      elif len(query_list) == 1:
        result = query_list[0]
      else:
        result = None
    return result

  original_parse = _parse
  fake_column_id_set = set(['a', 'b', 'c', 'd', 'title', 'toto', 'titi', 'foo', 'bar'])

  def parse(input, *args, **kw):
    """
      Parse input and walk generated AST.
    """
    result = original_parse(input, fake_column_id_set, *args, **kw)
    if result is not None:
      #print repr(result)
      result = walk(result)
    return result

  success_count = 0
  for input, expected in check_list:
    try:
      result = parse(input)
    except ParserOrLexerError, message:
      print "ERROR when checking %r" % (input, )
      print " crashed with: %s" % (message, )
      print " instead of producing %r" % (expected, )
    else:
      if result != expected:
        print "ERROR when checking %r:" % (input, )
        print " produced   %r" % (result, )
        print " instead of %r" % (expected, )
      else:
        success_count += 1
  print '%i/%i checks succeeded.' % (success_count, len(check_list))
  while 1:
    try:
      input = raw_input('catalog> ')
    except (EOFError, KeyboardInterrupt):
      break
    print repr(input)
    try:
      try:
        detector_result = getAdvancedSearchTextDetector()(input, fake_column_id_set)
      except ParserOrLexerError, message:
        print '  Detector raise: %r' % (message, )
        detector_result = False
      else:
        print '  Detector: %r' % (detector_result, )
      if detector_result:
        print '  LEX:'
        lexer = getAdvancedSearchTextParser().lexer
        lexer.input(input)
        while 1:
          tok = lexer.token()
          if not tok: break      # No more input
          print '    %s' % (tok, )
        print '  YACC:'
        print '    %r' % (parse(input, debug=2), )
      else:
        print '    %r' % (input, )
    except ParserOrLexerError, message:
      print message
  print

