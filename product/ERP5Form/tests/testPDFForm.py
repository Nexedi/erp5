##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
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

from Products.ERP5Form.PDFForm import PDFForm
from Products.ERP5.Document.Document import Document


class TestPDFForm(unittest.TestCase):
  """Tests PDF Form
  """

  def getTitle(self):
    return "PDF Form"

  def setUp(self):
    """Creates a PDFForm, and a document on which the PDF form is rendered.
    """
    self.document = Document('doc_id')
    pdf_file = open(os.path.join(os.path.dirname(__file__),
                                      'data', 'test_1.pdf'), 'rb')
    self.pdf_form = PDFForm('test_pdf_form').__of__(self.document)
    self.pdf_form.manage_upload(pdf_file)
    
  def test_getCellNames(self):
    self.assertEquals(['text_1', 'text_2', 'text_3'],
                      self.pdf_form.getCellNames())

  def test_SimpleGeneratePDF(self):
    self.pdf_form.setCellTALES('text_1', 'string:Something simple')
    self.failUnless(self.pdf_form.generatePDF())
    # aliases
    self.failUnless(self.pdf_form.index_html())
    self.failUnless(self.pdf_form())
  
  def test_EmptyGeneratePdf(self):
    self.failUnless(self.pdf_form.generatePDF())
    # aliases
    self.failUnless(self.pdf_form.index_html())
    self.failUnless(self.pdf_form())
  
  def test_showCellName(self):
    self.failUnless(self.pdf_form.showCellNames())
  
  def test_CellTALES(self):
    self.pdf_form.setCellTALES('text_1', 'here/getId')
    self.assertEquals('here/getId', self.pdf_form.getCellTALES('text_1'))

  def test_setInvalidTALES(self):
    from Products.PageTemplates.TALES import CompilerError
    self.pdf_form.setCellTALES('text_1', 'python:(inv.alid "= ')
    # maybe should raise when setting the TALES, not when getting ?
    self.assertRaises(CompilerError, self.pdf_form.evaluateCell, 'text_1')
  
  def test_EditCells(self):
    self.pdf_form.doEditCells(REQUEST=dict(text_1='here/getId',
                                           text_2='string:'))
    self.assertEquals('here/getId', self.pdf_form.getCellTALES('text_1'))
    self.assertEquals('string:', self.pdf_form.getCellTALES('text_2'))
  
  def test_EvaluateCell(self):
    self.pdf_form.setCellTALES('text_1', 'here/getId')
    self.assertEquals('doc_id', self.pdf_form.evaluateCell('text_1'))
  
  def test_EvaluateNonExistCell(self):
    self.assertRaises(KeyError, self.pdf_form.evaluateCell,
                      'this_cell_does_not_exist')
  
  def test_CalculateCellValues(self):
    self.pdf_form.setCellTALES('text_1', 'here/getId')
    self.pdf_form.setCellTALES('text_2', 'string:static')
    calculated_values = self.pdf_form.calculateCellValues()
    self.assertEquals('doc_id', calculated_values['text_1'])
    self.assertEquals('static', calculated_values['text_2'])
  
  def test_CalculateCellValuesWithCellKey(self):
    self.pdf_form.setCellTALES('text_1', 'here/getId')
    self.pdf_form.setCellTALES('text_2', 'cell/text_1')
    calculated_values = self.pdf_form.calculateCellValues()
    self.assertEquals('doc_id', calculated_values['text_1'])
    self.assertEquals('doc_id', calculated_values['text_2'])
  
  def test_CalculateCellValuesTotal(self):
    # The original use case of `cell`
    self.pdf_form.setCellTALES('text_1', 'python:3')
    self.pdf_form.setCellTALES('text_2', 'python:2')
    self.pdf_form.setCellTALES('text_3',
                               'python:cell["text_1"] + cell["text_2"]')
    self.assertEquals(3 + 2, self.pdf_form.calculateCellValues()['text_3'])
  
  def test_CalculateCellValuesCircularRefs(self):
    self.pdf_form.setCellTALES('text_1', 'cell/text2')
    self.pdf_form.setCellTALES('text_2', 'cell/text_1')
    from Products.ERP5Form.PDFForm import CircularReferencyError
    self.assertRaises(CircularReferencyError,
                      self.pdf_form.calculateCellValues)
  
  def test_CalculateCellValuesParms(self):
    self.pdf_form.setCellTALES('text_1', 'a_parameter')
    calculated_values = self.pdf_form.calculateCellValues(a_parameter='Value')
    self.assertEquals('Value', calculated_values['text_1'])
  

class TestPDFFormButtons(unittest.TestCase):
  """Tests PDF Form with buttons
  """
  def setUp(self):
    """Creates a PDFForm with buttons, and a document on which the PDF form is
    rendered.
    """
    self.document = Document('doc_id')
    pdf_file = open(os.path.join(os.path.dirname(__file__),
                        'data', 'test_button.pdf'), 'rb')
    self.pdf_form = PDFForm('test_pdf_form').__of__(self.document)
    self.pdf_form.manage_upload(pdf_file)
    
  def test_getCellNames(self):
    self.assertEquals(['check_box',],
                      self.pdf_form.getCellNames())

  def test_SimpleGeneratePDF(self):
    self.pdf_form.setCellTALES('check_box', 'python: 1')
    self.failUnless(self.pdf_form.generatePDF())
    # aliases
    self.failUnless(self.pdf_form.index_html())
    self.failUnless(self.pdf_form())

    # XXX for debugging:
    # file('/tmp/out.pdf', 'w').write(self.pdf_form())
    # os.system('xpdf /tmp/out.pdf')


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPDFForm))
  suite.addTest(unittest.makeSuite(TestPDFFormButtons))
  return suite
