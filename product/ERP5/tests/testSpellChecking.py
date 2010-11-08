# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#               Fabien Morin <fabien@nexedi.com
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
from Products.ERP5.tests.testXHTML import TestXHTML
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import popen2

class aspell:
    def __init__(self):
        self._f = popen2.Popen3("aspell -l en_GB -a")
        self._f.fromchild.readline() #skip the credit line
    def __call__(self, words):
        words = words.split(' ')
        output = []
        for word in words:
            self._f.tochild.write(word+'\n')
            self._f.tochild.flush()
            s = self._f.fromchild.readline().strip()
            self._f.fromchild.readline() #skip the blank line
            if s == "*":
                output.append(None)
            elif s[0] == '#':
                output.append("No Suggestions")
            else:
                output.append(s.split(':')[1].strip().split(', '))
        return output

class TestSpellChecking(ERP5TypeTestCase):

  run_all_test = 1
  spellChecker = aspell()

  def getTitle(self):
    return "Spell Checking Test"

  def getBusinessTemplateList(self):
    return (
      'erp5_base',)

  def validate_spell(self, word):
    '''
      validate the spell. Return True if the word is well spelled, False else,
      whith an error message
    '''
    result = self.spellChecker(word)
    message = ''
    if result != [None] and result != ['No Suggestions']:
      message = '"%s" is missspelled, suggestion are : "%s"' % \
          (word, '", "'.join(result[0]))
    if result == ['No Suggestions']:
      message = '"%s" is missspelled, there is no suggestion.' % word
    return result == [None], message

  def test_checkSpellChecker(self):
    # check a well spelled world
    self.assertEquals((self.validate_spell('cancelled')), (True, ''))

    # check some suggestion are given for a small mistake
    self.assertEquals(self.validate_spell('canceled')[0], False)
    self.assertTrue(len(self.validate_spell('canceled')[1]) > 0)

    # check no suggestion are given for a very bad spelled word
    self.assertEquals(self.validate_spell('cancelefqfdsqfdsfqdsf')[0], False)
    self.assertTrue('no suggestion' in self.validate_spell('cancelefqfdsqfdsfqdsf')[1])

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSpellChecking))
  return suite
