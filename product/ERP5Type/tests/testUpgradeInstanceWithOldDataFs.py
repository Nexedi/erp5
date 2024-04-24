##############################################################################
# coding: utf-8
# Copyright (c) 2024 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Utils import str2bytes
import io
import six.moves.urllib as urllib
import six.moves.http_client
from DateTime import DateTime


class OldDataFsSetup(ERP5TypeTestCase):
  """Set up of the "old" site, executed when saving.
  """
  def setUpOnce(self):
    self.tic()
    self.configure_security()
    self.create_person_with_login()
    self.generate_ids()
    self.create_documents()
    self.tic()

  def configure_security(self):
    self.category_test_group = \
      self.portal.portal_categories.group.newContent(
        portal_type='Category',
        title='Test Group',
        id='test_g',
        codification='TESTG'
      )
    for module_portal_type in (
      'Document Module',
      'Organisation Module',
      'Person Module',
    ):
      self.portal.portal_types[module_portal_type].newContent(
        portal_type='Role Information',
        role_category_list=(self.category_test_group.getRelativeUrl(),),
        role_name_list=('Auditor', 'Author'),
      )
      self.portal.portal_types[module_portal_type].updateRoleMapping()
    for document_portal_type in ('Organisation', 'Person', 'File'):
      self.portal.portal_types[document_portal_type].newContent(
        portal_type='Role Information',
        role_category_list=(self.category_test_group.getRelativeUrl(),),
        role_name_list=('Assignee', 'Assignor'),
      )
    self.tic()

  def create_person_with_login(self):
    person = self.portal.person_module.newContent(
      portal_type='Person',
      first_name='test person',
      id='test_person_login',
    )
    person.validate()
    person.newContent(
      portal_type='ERP5 Login',
      reference='user-login',
      password='secret',
    ).validate()
    person.newContent(
      portal_type='Assignment',
      group_value=self.category_test_group,
    ).open()
    self.tic()

  def generate_ids(self):
    self.portal.portal_ids.generateNewId(
      id_group='test_id_group_document',
      default=123,
      id_generator='document',
    )
    self.portal.portal_ids.generateNewId(
      id_group='test_id_group_uid',
      default=456,
      id_generator='uid',
    )

  def create_documents(self):
    self.loginByUserName('user-login')
    o = self.portal.organisation_module.newContent(
      id='test_organisation',
      portal_type='Organisation',
      title='test héhé',
      description="test\nhéhé",
    )
    with self.pinDateTime(DateTime(2123, 4, 5)):
      o.validate(comment="Workflow comment héhé")
    self.portal.organisation_module.newContent(
      portal_type='Organisation',
      title='another organisation',
    )
    self.portal.person_module.newContent(
      portal_type='Person',
      title='another person',
    )
    self.portal.document_module.newContent(
      portal_type='File',
      id='file_content_ascii',
      data=b'easy',
    )
    self.portal.document_module.newContent(
      portal_type='File',
      id='file_content_valid_utf8',
      data=b'\xc3\xa9'
    )
    self.portal.document_module.newContent(
      portal_type='File',
      id='file_content_invalid_utf8',
      data=b'\xff',
    )


class TestUpgradeInstanceWithOldDataFs(OldDataFsSetup):

  def getBusinessTemplateList(self):
    return (
      'erp5_core_proxy_field_legacy',
      'erp5_full_text_mroonga_catalog',
      'erp5_base',
      'erp5_simulation',
      'erp5_accounting',
      'erp5_configurator',
      'erp5_pdm',
      'erp5_trade',
      'erp5_ingestion_mysql_innodb_catalog',
      'erp5_ingestion',
      'erp5_crm',
      'erp5_jquery_ui',
      'erp5_knowledge_pad',
      'erp5_project',
      'erp5_forge',
      'erp5_web',
      'erp5_jquery_plugin_mbmenu',
      'erp5_jquery_plugin_sheet',
      'erp5_jquery_plugin_jqchart',
      'erp5_jquery_plugin_colorpicker',
      'erp5_jquery_plugin_elastic',
      'erp5_jquery_sheet_editor',
      'erp5_svg_editor',
      'erp5_dms',
      'erp5_mrp',
      'erp5_hal_json_style',
      'erp5_font',
      'erp5_web_renderjs_ui',
      'erp5_code_mirror',
      'erp5_multimedia',
      'erp5_smart_assistant',
      'erp5_run_my_doc',
      'erp5_notebook',
      'erp5_officejs',
      'erp5_configurator_standard_trade_template',
      'erp5_monaco_editor',
      'erp5_upgrader',
     )

  def run_upgrader(self):
    if not self.portal.portal_templates.getRepositoryList():
      self.setupAutomaticBusinessTemplateRepository(
        searchable_business_template_list=["erp5_core", "erp5_base", "erp5_notebook"])

    from Products.ERP5Type.tests.utils import createZODBPythonScript
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'Base_getUpgradeBusinessTemplateList',
      '',
      """return (('erp5_base',
         'erp5_configurator_standard_trade_template',
         'erp5_configurator_standard',
         'erp5_jquery',
         'erp5_xhtml_style',
         'erp5_upgrader',
         'erp5_accounting',
         'erp5_trade',
         'erp5_pdm',
         'erp5_crm',
         'erp5_project',
         'erp5_forge',
         'erp5_dms',
         'erp5_mrp',
         'erp5_officejs',
         'erp5_web_renderjs_ui'),
         ())""")
    self.tic()

    alarm = self.portal.portal_alarms.promise_check_upgrade

    # Ensure it is viewable
    alarm.view()
    # Call active sense
    alarm.activeSense()
    self.tic()
    # XXX No idea why active sense must be called twice...
    alarm.activeSense()
    self.tic()

    self.assertNotEqual([x.detail for x in alarm.getLastActiveProcess().getResultList()], [])

    # XXX We only check that Base_callDialogMethod can be correctly executed
    # and we do not check the result (the redirect can be an Unauthorized error)
    # A better version would be to use the Location header result to trigger Alarm_solve
    ret = self.publish(
      '%s/portal_alarms/promise_check_upgrade' % self.portal.getPath(),
      basic='%s:current' % self.id(),
      stdin=io.BytesIO(str2bytes(urllib.parse.urlencode({
        'Base_callDialogMethod:method': '',
        'dialog_id': 'Alarm_viewSolveDialog',
        'dialog_method': 'Alarm_solve',
        'form_id': 'Alarm_view',
        'selection_name': 'foo_selection',
      }))),
      request_method="POST",
      handle_errors=False
    )
    self.assertEqual(six.moves.http_client.FOUND, ret.getStatus())

    alarm.Alarm_solve()
    self.tic(delay=2400)
    self.assertEqual([x.detail for x in alarm.getLastActiveProcess().getResultList()], [])

  def check_portal_type_not_broken(self):
    # Make sure that *all* Portal Type can be loaded after upgrade
    import erp5.portal_type
    from Products.ERP5Type.dynamic.lazy_class import ERP5BaseBroken
    error_list = []
    for portal_type_obj in self.portal.portal_types.listTypeInfo():
      portal_type_id = portal_type_obj.getId()
      portal_type_class = getattr(erp5.portal_type, portal_type_id)
      portal_type_class.loadClass()
      if issubclass(portal_type_class, ERP5BaseBroken):
        error_list.append(portal_type_id)
    self.assertEqual(
      error_list, [],
      msg="The following Portal Type classes could not be loaded (see zLOG.log): %r" % error_list)

  def check_user_can_login(self):
    ret = self.publish(self.portal.person_module.getPath(), basic='user-login:secret')
    self.assertIn(b'Persons', ret.getBody())
    self.assertEqual(ret.getStatus(), six.moves.http_client.OK)
    self.loginByUserName('user-login')
    self.assertIn(
      'Invalidate',
      [a['name']
        for a in self.portal.portal_actions.listFilteredActionsFor(
          object=self.portal.person_module.test_person_login)['workflow']])

  def check_portal_ids(self):
    new_id_document = self.portal.portal_ids.generateNewId(
      id_group='test_id_group_document',
      id_generator='document',
    )
    self.assertEqual(new_id_document, 124)
    new_id_uid = self.portal.portal_ids.generateNewId(
      id_group='test_id_group_uid',
      id_generator='uid',
    )
    self.assertEqual(new_id_uid, 457)

  def check_existing_documents(self):
    self.assertEqual(len(self.portal.organisation_module.contentValues()), 2)
    organisation = self.portal.organisation_module.test_organisation
    self.assertEqual(organisation.getTitle(), 'test héhé')
    self.assertEqual(organisation.getDescription(), 'test\nhéhé')
    workflow_history = self.portal.portal_workflow.getInfoFor(
      organisation,
      'history',
      wf_id='validation_workflow',
    )
    self.assertEqual(workflow_history[-1]['comment'], 'Workflow comment héhé')
    self.assertEqual(
      workflow_history[-1]['actor'],
      self.portal.person_module.test_person_login.getUserId())
    self.assertEqual(workflow_history[-1]['time'], DateTime(2123, 4, 5))

    organisation.setDescription('test\nhéhé\nafter')
    self.tic()
    self.assertEqual(organisation.getDescription(), 'test\nhéhé\nafter')

  def check_existing_dms_documents(self):
    self.assertEqual(
      self.portal.document_module.file_content_ascii.getData(),
      b'easy',
    )
    self.assertEqual(
      self.portal.document_module.file_content_valid_utf8.getData(),
      b'\xc3\xa9',
    )
    self.assertEqual(
      self.portal.document_module.file_content_invalid_utf8.getData(),
      b'\xff',
    )

  def check_new_documents(self):
    existing_document_list = list(self.portal.document_module.contentValues())
    self.assertTrue(existing_document_list)
    self.portal.document_module.newContent(portal_type='File')
    self.tic()
    self.assertEqual(
      len(list(self.portal.document_module.contentValues())),
      len(existing_document_list) + 1,
    )

  def check_documents(self):
    self.check_existing_documents()
    self.check_existing_dms_documents()
    self.check_new_documents()

  def check_catalog_as_manager(self):
    self.login()
    self.assertEqual(
      [
        brain.getObject().getTitle()
        for brain in self.portal.portal_catalog(
          title='test héhé',
          portal_type='Organisation',
        )
      ], ['test héhé'])

  def check_catalog_as_user(self):
    self.login(self.portal.person_module.test_person_login.getUserId())
    self.assertEqual(
      [
        brain.getObject().getTitle()
        for brain in self.portal.portal_catalog(
          title='test héhé',
          portal_type='Organisation',
        )
      ], ['test héhé'])
    self.assertEqual(
      [
        brain.getObject().getTitle()
        for brain in self.portal.portal_catalog(
          title='test person',
          portal_type='Person',
        )
      ], ['test person'])
    self.assertEqual(
      [
        brain.getObject().getTitle()
        for brain in self.portal.portal_catalog(
          title='test person',
          portal_type='Person',
          local_roles=['Assignee'],
        )
      ], ['test person'])

  def check_catalog_as_anonymous(self):
    self.logout()
    self.assertFalse(
      self.portal.portal_catalog(
        title='test héhé',
        portal_type='Organisation',
      )
    )

  def check_catalog(self):
    self.check_catalog_as_manager()
    self.check_catalog_as_user()
    self.check_catalog_as_anonymous()

  def test_upgrade(self):
    self.run_upgrader()
    self.check_portal_type_not_broken()
    self.check_user_can_login()
    self.check_portal_ids()
    self.check_documents()
    self.check_catalog()
