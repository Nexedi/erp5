# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################


import unittest
import os

from Products.ERP5OOo.OOoUtils import OOoParser
import six


def makeFilePath(name):
  return os.path.join(os.path.dirname(__file__), 'test_document', name)

class TestOOoParser(unittest.TestCase):
  """ OOoParser tests
  """
  def test_getSpreadSheetMapping(self):
    parser = OOoParser()
    parser.openFile(open(makeFilePath('import_data_list.ods'), 'rb'))
    mapping = parser.getSpreadsheetsMapping()
    self.assertEqual(['Person'], list(mapping.keys()))
    person_mapping = mapping['Person']
    self.assertTrue(isinstance(person_mapping, list))
    self.assertTrue(102, len(person_mapping))
    self.assertEqual(person_mapping[0],
       ['Title', 'First Name', 'Last Name', 'Default Email Text'])
    self.assertEqual(person_mapping[1],
       ['John Doe 0', 'John', 'Doe 0', 'john.doe0@foo.com'])

  def test_openFromBytes(self):
    parser = OOoParser()
    with open(makeFilePath('import_data_list.ods'), 'rb') as f:
      parser.openFromBytes(f.read())
    mapping = parser.getSpreadsheetsMapping()
    self.assertEqual(['Person'], list(mapping.keys()))

  def test_getSpreadSheetMappingStyle(self):
    parser = OOoParser()
    with open(makeFilePath('import_data_list_with_style.ods'), 'rb') as f:
      parser.openFile(f)
    mapping = parser.getSpreadsheetsMapping()
    self.assertEqual(['Feuille1'], list(mapping.keys()))
    self.assertEqual(mapping['Feuille1'][1],
                      ['a line with style'])
    self.assertEqual(mapping['Feuille1'][2],
                      ['a line with multiple styles'])
    self.assertEqual(mapping['Feuille1'][3],
                      ['http://www.erp5.org'])
    self.assertEqual(mapping['Feuille1'][4],
                      ['john.doe@example.com'])

  def test_getSpreadSheetMappingDataTypes(self):
    parser = OOoParser()
    with open(makeFilePath('import_data_list_data_type.ods'), 'rb') as f:
      parser.openFile(f)
    mapping = parser.getSpreadsheetsMapping()
    self.assertEqual(['Feuille1'], list(mapping.keys()))
    self.assertEqual(mapping['Feuille1'][0],
                      ['1234.5678'])
    self.assertEqual(mapping['Feuille1'][1],
                      ['1234.5678'])
    self.assertEqual(mapping['Feuille1'][2],
                      ['0.1'])
    self.assertEqual(mapping['Feuille1'][3],
                      ['2008-11-14'])
    self.assertEqual(mapping['Feuille1'][4],
                      ['2008-11-14T10:20:30']) # supported by DateTime
    self.assertEqual(mapping['Feuille1'][5],
                      ['PT12H34M56S']) # maybe not good, this is raw format
    self.assertEqual(mapping['Feuille1'][6],
                      ['With note'])

  def test_BigSpreadSheet_can_be_parsed(self,):
    """Test than OOoimport can parse a file with more than 40000 lines
    """
    parser = OOoParser()
    parser.openFile(open(makeFilePath('import_big_spreadsheet.ods'), 'rb'))
    mapping = parser.getSpreadsheetsMapping()
    not_ok = 1
    for spread, values in six.iteritems(mapping):
      self.assertEqual(len(values), 41001)
      not_ok = 0
    if not_ok:
      self.fail('Spreadsheet not read!')

  def test_getSpreadSheetMappingText(self):
    parser = OOoParser()
    parser.openFile(open(makeFilePath('complex_text.ods'), 'rb'))
    mapping = parser.getSpreadsheetsMapping()
    self.assertEqual(['Feuille1'], list(mapping.keys()))
    self.assertEqual(mapping['Feuille1'][0], [' leading space'])
    self.assertEqual(mapping['Feuille1'][1], ['   leading space'])
    self.assertEqual(mapping['Feuille1'][2], ['tab\t'])
    self.assertEqual(mapping['Feuille1'][3], ['New\nLine'])

  def test_getSpreadSheetMappingEmptyCells(self):
    parser = OOoParser()
    parser.openFile(open(makeFilePath('empty_cells.ods'), 'rb'))
    mapping = parser.getSpreadsheetsMapping()
    self.assertEqual(['Feuille1'], list(mapping.keys()))
    self.assertEqual(mapping['Feuille1'],
      [
        ['A1', None, 'C1'],
        [],
        [None, 'B3',],
      ])


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOOoParser))
  return suite
