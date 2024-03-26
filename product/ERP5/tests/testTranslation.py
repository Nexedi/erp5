# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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

import MethodObject

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Utils import getMessageIdWithContext, str2unicode, unicode2str

# dependency order
target_business_templates = (
  'erp5_base',
  'erp5_simulation',
  'erp5_pdm',
  'erp5_trade',

  'erp5_accounting',
  'erp5_invoicing',

  'erp5_apparel',

  'erp5_budget',
  'erp5_public_accounting_budget',

  'erp5_consulting',

  'erp5_ingestion',
  'erp5_ingestion_mysql_innodb_catalog',
  'erp5_crm',

  'erp5_web',
  'erp5_dms',

  'erp5_commerce',

  'erp5_forge',

  'erp5_immobilisation',

  'erp5_item',

  'erp5_mrp',

  'erp5_payroll',

  'erp5_project',

  'erp5_calendar',

  'erp5_l10n_fr',
  'erp5_l10n_ja',
  'erp5_l10n_pl_PL',
  'erp5_l10n_pt-BR',
)

class TestWorkflowStateTitleTranslation(ERP5TypeTestCase):
  run_all_test = 1
  domain = 'erp5_ui'
  lang = 'en'

  def getTitle(self):
    return "Translation Test"

  def getBusinessTemplateList(self):
    """  """
    return target_business_templates

  def getTranslation(self, msgid):

    result = self.portal.Localizer.erp5_ui.gettext(
          msgid, default='')
    #result = self.portal.Localizer.translate(
        #domain=self.domain, msgid=msgid, lang=self.lang)
    if (result == msgid) and (self.lang != 'en'):
      #result = None
      result = self.portal.Localizer.erp5_ui.gettext(msgid)
    return unicode2str(result)

  def logMessage(self, message):
    self.message += '%s\n' % message

  def checkWorkflowStateTitle(self, quiet=0, run=run_all_test):
    """
    Test workflow state title translation.
    Check that using portal_catalog can not return strange results to the user.
    Each translation must be only related to one state ID.
    """
    if not run: return
    self.message = '\n'

    translation_dict = {}

    workflow_tool = self.portal.portal_workflow
    for workflow_id in workflow_tool.objectIds():
      workflow = workflow_tool._getOb(workflow_id)
      class_name = workflow.__class__.__name__
      if class_name == 'DCWorkflowDefinition':
        for state in workflow.states.items():
          state_title = state[1].title
          state_id = state[0]
          msgid = getMessageIdWithContext(state_title, 'state', workflow_id)
          translated_state_title = self.getTranslation(msgid)

          if translated_state_title is not None:
            try:
              translation_dict[translated_state_title].add(state_id)
            except KeyError:
              translation_dict[translated_state_title] = {state_id}


    for key, value in translation_dict.items():
      if len(value) == 1:
        translation_dict.pop(key)

    if translation_dict != {}:
      # State ID has multiple translation associated, and it leads to
      # unexpected results for the user when using portal catalog.
      rejected_key_list = translation_dict.keys()
      result_dict = {x: [] for x in rejected_key_list}
      error_dict =  {x: [] for x in rejected_key_list}
      error = 0

      # Browse all workflows to ease fixing this issue.
      for workflow in self.portal.portal_workflow.objectValues():
        if workflow.__class__.__name__ == 'DCWorkflowDefinition':
          workflow_id = workflow.id
          workflow_dict = {}
          for state_id, state in workflow.states._mapping.items():
            state_title = state.title
            translated_state_title = \
              self.portal.Localizer.erp5_ui.gettext(state_title, lang=self.lang)
            if translated_state_title in rejected_key_list:
              result_dict[translated_state_title].append(
                  (workflow_id, state_id, state_title))

      # XXX To be improved
      not_used_workflow_id_list = []
      for key, item_list in result_dict.items():
        wrong_state_id_list = [x[1] for x in item_list]
        for workflow_id, wrong_state_id, state_title in item_list:
          if workflow_id not in not_used_workflow_id_list:
            workflow = self.portal.portal_workflow._getOb(workflow_id)
            state_id_list = []
            for state_id in workflow.states._mapping.keys():
              if (state_id in wrong_state_id_list) and \
                  (state_id != wrong_state_id):
                state_id_list.append(state_id)

            if len(state_id_list) != 0:
              error_dict[key].append((
                workflow_id, wrong_state_id, state_title, state_id_list))
              error = 1

      if error:
        for key, item_list in error_dict.items():
          if len(item_list) != 0:
            self.logMessage("\n'%s'" % unicode2str(key))
            self.logMessage('\t### Conflicting workflow with common states (ie, what user can see) ###')
            for item in item_list:
              # XXX Improve rendering
              self.logMessage(
                  "\t%r\t%r\t'%s'\t%r" % \
                  item)
            self.logMessage('\n\t### All conflicting workflows (ie, problems asking to happen) ###')
            for item in result_dict[key]:
              # XXX Improve rendering
              self.logMessage(
                  "\t%r\t%r\t'%s'" % \
                  item)

        self.fail(self.message)

  def afterSetUp(self):
    self.portal.Localizer._default_language = 'en'
    self.portal.Localizer.set_languages(['en', 'fr'])

  def test_01_EnglishTranslation(self, quiet=0, run=run_all_test):
    """
    Test English translation
    """
    self.lang = 'en'
    self.checkWorkflowStateTitle(quiet=quiet, run=run)

  def test_02_FrenchTranslation(self, quiet=0, run=run_all_test):
    """
    Test French translation
    """
    self.lang = 'fr'
    self.checkWorkflowStateTitle(quiet=quiet, run=run)

  def test_03_JapaneseTranslation(self, quiet=0, run=run_all_test):
    """
    Test Japanese translation
    """
    self.lang = 'ja'
    self.checkWorkflowStateTitle(quiet=quiet, run=run)

  def test_04_PolishTranslation(self, quiet=0, run=run_all_test):
    """
    Test Polish translation
    """
    self.lang = 'pl'
    self.checkWorkflowStateTitle(quiet=quiet, run=run)

  def test_05_PortugueseTranslation(self, quiet=0, run=run_all_test):
    """
    Test Portuguese translation
    """
    self.lang = 'pt-BR'
    self.checkWorkflowStateTitle(quiet=quiet, run=run)

  def test_06_FrenchTranslationOfMessageWithContext(self, quiet=0,
         run=run_all_test):
    """
    Test French translation
    """
    self.lang = 'fr'

    message_catalog = self.portal.Localizer.erp5_ui
    message_catalog.gettext('Validated', add=1)
    message_catalog.gettext('Draft', add=1)
    message_catalog.gettext(getMessageIdWithContext('Validated',
                                                    'state',
                                                    'item_workflow'),
                            add=1)
    message_catalog.message_edit('Validated', self.lang,
                                 str2unicode('Validé'), '')
    message_catalog.message_edit(getMessageIdWithContext('Validated',
                                                         'state',
                                                         'item_workflow'),
                                 self.lang, "En bon usage", '')
    message_catalog.message_edit('Draft', self.lang, '', '')
    portal_type = 'Organisation'
    organisation_module = self.getPortal().getDefaultModule(portal_type)
    organisation = organisation_module.newContent(
                  portal_type=portal_type,
                  title='My Organisation')
    organisation.validate()
    portal_type = 'Item'
    item_module = self.getPortal().getDefaultModule(portal_type)
    item = item_module.newContent(portal_type=portal_type, title='Lot A')

    self.tic()
    self.portal.Localizer._default_language = 'fr'

    self.assertEqual(item.getTranslatedValidationStateTitle(), 'Draft')
    item.validate()
    self.assertEqual(item.getTranslatedValidationStateTitle(), "En bon usage")
    self.assertEqual(organisation.getTranslatedValidationStateTitle(),
                      'Validé')
    # Now run indexation of translations.
    self.portal.ERP5Site_updateTranslationTable()
    self.tic()
    # Ckeck queries with translated workflow state title generated with
    # getMessageIdWithContext
    self.assertEqual(1, len(self.portal.portal_catalog(
      translated_validation_state_title="En bon usage")))
    self.assertEqual(1, len(self.portal.portal_catalog(
      translated_validation_state_title="En bon usage", portal_type='Item')))
    self.assertEqual(0, len(self.portal.portal_catalog(
      translated_validation_state_title="En bon usage",
      portal_type='Organisation')))

  def test_07_NegatedQueryForTranslation(self, quiet=0, run=run_all_test):
    """
    Check that catalog search with a negated query parameter doesn't return
    unexpected results.
     - get a portal type ans its related workflow
     - add a new context translation for the original state
     - update the catalog tables
     - verify the catalog result
    """
    self.lang = 'en'
    # Get one portal type and its related workflow
    portal_type_id = 'Bug'
    workflow_id = 'bug_workflow'
    workflow_value = self.portal.portal_workflow._getOb(workflow_id)
    assert(workflow_value in \
            self.portal.portal_workflow.getWorkflowValueListFor(portal_type_id))
    bug = self.portal.getDefaultModule(portal_type_id).newContent(
        portal_type=portal_type_id)
    state_title = bug.getSimulationStateTitle()

    # add a new context translation for the original state
    message_catalog = self.portal.Localizer.erp5_ui
    message_catalog.gettext(state_title, add=1)
    message_catalog.gettext(getMessageIdWithContext(state_title,
                                                    'state',
                                                    workflow_id),
                            add=1)
    assert(bug.getTranslatedSimulationStateTitle() == state_title)

    try:
      message_catalog.message_edit(getMessageIdWithContext(state_title,
                                                           'state',
                                                           workflow_id),
                                   self.lang, "%s in context" % state_title, '')
      assert(bug.getTranslatedSimulationStateTitle() == \
                                    "%s in context" % state_title)

      # Update the translation table
      self.portal.ERP5Site_updateTranslationTable()
      self.tic()

      # Check the catalog result
      assert(len(self.portal.portal_catalog(portal_type=portal_type_id)) == 1)
      result = self.portal.portal_catalog(portal_type=portal_type_id,
          translated_simulation_state_title='!="%s in context"' % state_title)
      self.assertEqual(len(result), 0)
    finally:
      # Clean the new context message
      message_catalog.message_del(getMessageIdWithContext(state_title,
                                                      'state',
                                                      workflow_id))
      # Update the translation table
      self.portal.ERP5Site_updateTranslationTable()
      self.tic()

class LanguageGetter(MethodObject.Method):

  def __init__(self, lang):
    self.lang = lang

  def __call__(self, context):
    return self.lang

class TestTranslation(ERP5TypeTestCase):

  lang = 'fr'

  def getTitle(self):
    return 'Test Translation'

  def getBusinessTemplateList(self):
    return ['erp5_base',]

  def _setUpTranslations(self):
    self.portal.Localizer.manage_addLanguage(self.lang)
    erp5_ui = self.portal.Localizer.erp5_ui
    erp5_ui.gettext('Draft', add=1)
    erp5_ui.gettext('Person', add=1)
    erp5_ui.message_edit('Draft', self.lang, 'Brouillon', '')
    erp5_ui.message_edit('Person', self.lang, 'Personne', '')
    self.portal.ERP5Site_updateTranslationTable()

  def _cleanUpTranslations(self):
    erp5_ui = self.portal.Localizer.erp5_ui
    for msgid in ('Person', 'Draft'):
      translations = erp5_ui.get_translations(msgid)
      translations.pop(self.lang, None)
    self.portal.ERP5Site_updateTranslationTable()

  def afterSetUp(self):
    super(TestTranslation, self).afterSetUp()
    self._setUpTranslations()

    # replace Localizer.utils.lang_negotiator in MessageCatalog to return
    # self.lang
    from Products.Localizer import MessageCatalog
    self.old_lang_negotiator = MessageCatalog.lang_negotiator
    def lang_negotiator(avilable_languages, self=self):
      return self.lang
    MessageCatalog.lang_negotiator = lang_negotiator

    # patch get_selected_language, used by portal_catalog queries that use
    # translation
    self.portal.Localizer.get_selected_language = LanguageGetter(self.lang)

    # create the zpt used by self.translate_by_zpt()
    dispatcher = self.portal.manage_addProduct['PageTemplates']
    dispatcher.manage_addPageTemplate('myzpt')
    self.myzpt = self.portal.myzpt
    self.tic()

  def beforeTearDown(self):
    self.abort()
    # unpatch lang_negotiator and get_selected_message
    from Products.Localizer import MessageCatalog
    MessageCatalog.lang_negotiator = self.old_lang_negotiator
    del self.portal.Localizer.get_selected_language

    self._cleanUpTranslations()
    # test clean-up actually worked
    erp5_ui = self.portal.Localizer.erp5_ui
    self.assertEqual(erp5_ui.gettext('Person', lang=self.lang), 'Person')
    self.assertEqual(erp5_ui.gettext('Draft', lang=self.lang), 'Draft')

    # erase created objects
    for module in (self.portal.person_module, self.portal.organisation_module):
      module.manage_delObjects(list(module.objectIds()))
    self.portal.manage_delObjects(['myzpt'])

    self.tic()
    super(TestTranslation, self).beforeTearDown()

  def test_Localizer_translation(self):
    # basically, test afterSetUp worked...
    erp5_ui = self.portal.Localizer.erp5_ui
    self.assertEqual(erp5_ui.gettext('Person', lang=self.lang), 'Personne')

  def translate_by_zpt(self, domain, *words):
    zpt_template = """
    <tal:ommit xmlns:i18n="http://xml.zope.org/namespaces/i18n"
               i18n:domain="%s">
      <tal:ommit repeat="word options/words" content="word"
                 i18n:translate="">Word</tal:ommit>
    </tal:ommit>
    """ % domain
    self.myzpt.pt_edit(zpt_template, 'text/html')
    return unicode2str(self.myzpt(words=words)).split()

  def test_ZPT_translation(self):
    results = self.translate_by_zpt('erp5_ui', 'Person', 'Draft')
    self.assertEqual(results, ['Personne', 'Brouillon'])

  def test_ZPT_translation_with_domain_alias(self):
    # test with a translation domain alias
    results = self.translate_by_zpt('ui', 'Person', 'Draft')
    self.assertEqual(results, ['Personne', 'Brouillon'])

  def test_portal_type_and_state_title_translation_on_portal_catalog(self):
    # make sure we can search by "translated_validation_state_title" and
    # "translated_portal_type"
    person_1 = self.portal.person_module.newContent(portal_type='Person')
    person_1.validate()
    person_2 = self.portal.person_module.newContent(portal_type='Person')
    organisation = self.portal.organisation_module.newContent(
                            portal_type='Organisation')

    self.tic()
    self.assertEqual({person_1, person_2}, {x.getObject() for x in
          self.portal.portal_catalog(translated_portal_type='Personne')})

    self.assertEqual({person_2, organisation}, {x.getObject() for x in
          self.portal.portal_catalog(translated_validation_state_title='Brouillon',
                                     portal_type=('Person', 'Organisation'))})
    self.assertEqual([person_2],
        [x.getObject() for x in
          self.portal.portal_catalog(translated_validation_state_title='Brouillon',
                                     translated_portal_type='Personne')])

class TestTranslationWithBusinessTemplate(TestTranslation):

  def _setUpTranslations(self):
    self.manuallyInstallBusinessTemplate('erp5_l10n_fr')

  def _cleanUpTranslations(self):
    self.uninstallBusinessTemplate('erp5_l10n_fr')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTranslation))
  suite.addTest(unittest.makeSuite(TestTranslationWithBusinessTemplate))
  suite.addTest(unittest.makeSuite(TestWorkflowStateTitleTranslation))
  return suite
