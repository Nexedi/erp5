# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#               Fabien Morin <fabien@nexedi.com>
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
from subprocess import Popen, PIPE
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import six


# XXX (lucas): this list must be added in text file
except_word_list = ('todo',
                    'journalised',)


class Aspell(object):

  language_list = ('en_GB',)

  def __call__(self, sentence):
    word_list = sentence.split()
    output_dict = {}
    for word in word_list:
      if word.lower() in except_word_list:
        output_dict[word] = ['*']
        continue

      for language in self.language_list:
        output_dict[word] = self.getSpellCheckResultList(word, language)

    return output_dict

  def getSpellCheckResultList(self, word, language):
    command = 'echo %s | aspell -l %s -a' % (word, language)
    subprocess = Popen(command, shell=True, stdin=PIPE,
                                     stdout=PIPE, stderr=PIPE, close_fds=True)
    return subprocess.communicate()[0].split('\n')[1:]

class TestSpellChecking(ERP5TypeTestCase):

  run_all_test = 1
  spellChecker = Aspell()

  def getTitle(self):
    return "Spell Checking Test"

  def getBusinessTemplateList(self):
    return ('erp5_full_text_mroonga_catalog',
            'erp5_base',
            'erp5_simulation',
            'erp5_accounting',
            'erp5_pdm',
            'erp5_trade',
            'erp5_jquery',
            'erp5_jquery_ui',
            'erp5_web',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_ingestion',
            'erp5_invoicing',
            'erp5_advanced_invoicing',
            'erp5_apparel',
            'erp5_archive',
            'erp5_budget',
            'erp5_calendar',
            'erp5_commerce',
            'erp5_consulting',
            'erp5_content_translation',
            'erp5_crm',
            'erp5_credential',
            'erp5_data_protection',
            'erp5_dms',
            'erp5_forge',
            'erp5_hr',
            'erp5_immobilisation',
            'erp5_item',
            'erp5_knowledge_pad',
            'erp5_mrp',
            'erp5_open_trade',
            'erp5_payroll',
            'erp5_project',
            'erp5_publication',
            'erp5_simulation_performance_test',
            'erp5_ui_test',
            )

  def validate_spell(self, sentence):
    """
      Validate the spell. Return True if the word is well spelled, False else,
      with an error message.
    """
    message = '"%s" is misspelled, suggestion are : "%s"'
    result_dict = {}
    for word, result_list in six.iteritems(self.spellChecker(sentence)):
      filtered_result_list = filter(lambda x: x not in ('*', ''), result_list)
      if filtered_result_list:
        result_dict[word] = message % (word, \
                                filtered_result_list[0].split(':')[-1].strip())
    return result_dict

  def test_checkSpellChecker(self):
    """
      Simple test for Aspell class.
    """
    # check a well spelled world
    self.assertEqual(self.validate_spell('cancelled'), {})
    self.assertEqual(self.validate_spell('globally enabled'), {})
    self.assertEqual(self.validate_spell('http://www.erp5.com'), {})
    self.assertEqual(self.validate_spell('2010/11/20'), {})

    # check some suggestion are given for a small mistake
    self.assertNotEqual(self.validate_spell('canceled'), {})
    self.assertIn('is misspelled',
                             list(self.validate_spell('canceled').values())[0])

  def test_business_template_list_with_workflow_template_item(self):
    """
      Make sure that we have installed on this test all public
      business template which has WorkflowTemplateItem.
    """

  def test_spell_check_workflow_states(self):
    """
      Running spell check on each state object of all installed workflows.
      It will check the attributes:
       - id
       - title
    """
    message = 'State %s: %s, \n Workflow: %s \n Suggestions: %s'
    attribute_list = ['reference', 'title']
    error_list = []
    for workflow in self.portal.portal_workflow.objectValues():
      for state in workflow.getStateValueList():
        for attribute in attribute_list:
          sentence = state.getProperty(attribute)
          result_dict = self.validate_spell(sentence)
          if result_dict:
            error_list.append(message % (attribute, sentence, workflow.getId(),
                                         result_dict.pop(sentence)))

    if error_list:
      self.fail('\n'.join(error_list))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSpellChecking))
  return suite
