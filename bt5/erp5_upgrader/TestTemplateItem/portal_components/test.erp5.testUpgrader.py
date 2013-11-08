##############################################################################
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#                         Gabriel M. Monnerat <gabriel@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import re
import transaction
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5.Tool.TemplateTool import BusinessTemplateUnknownError
from Products.ERP5Type.tests.Sequence import SequenceList

DETAIL_PATTERN = re.compile(r"(?P<relative_url>.*)\ \<\>\ " + \
      r"(?P<reference>\w+)\ \-\>\ (?P<new_reference>\w+)")

class TestUpgrader(ERP5TypeTestCase):
  """
    Test one upgrader using constraints
  """

  script_id = "Person_checkPreUpgradeReferenceConsistency_custom"
  property_sheet_id = "TestPersonConstraint"

  def getTitle(self):
    return "Upgrader Tests"

  def getBusinessTemplateList(self):
    return ('erp5_upgrader',)

  def stepCreatePerson(self, sequence):
    module = self.portal.person_module
    person = module.newContent(portal_type="Person", title="User",
      reference="user%s" % module.getLastId())
    sequence.edit(person=person)

  def stepValidatePerson(self, sequence):
    sequence.get("person").validate()

  def afterSetUp(self):
    self.portal.portal_types['Person Module'].setTypePropertySheetList(None)
    self.stepRemoveConstraintFromPersonPortalType()
    for person in self.portal.person_module.searchFolder(
        validation_state='validated', title="User"):
      if person.getValidationState() == "validated":
        person.invalidate()
    self.tic()

  def stepClearCache(self, sequence=None):
    self.portal.portal_caches.clearCache(
      cache_factory_list=('erp5_content_medium',))

  def stepCreatePropertySheetToValidateOrganisation(self, sequence=None):
    portal = self.portal
    skin_folder = portal.portal_skins.custom
    script_id = "Organisation_changeWorkflowFromDraftToValidated"
    custom_script = getattr(skin_folder, script_id, None)
    if custom_script is None:
      skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(script_id)
      custom_script = getattr(skin_folder, script_id)
      script_body = "error_list = []\n" + \
        "if context.getValidationState() == 'draft':\n" + \
        "  kw = {'relative_url': context.getRelativeUrl()}\n" + \
        "  error_list.append('%(relative_url)s should be validated' % kw)\n" + \
        "  if fixit:\n" + \
        "    context.validate()\nreturn error_list"
      custom_script.ZPythonScript_edit('fixit=False, **kw', script_body)

    property_sheet_id = "OrganisationDraftConstraint"
    property_sheet = getattr(portal.portal_property_sheets, property_sheet_id, None)
    if property_sheet is None:
      property_sheet = portal.portal_property_sheets.newContent(
        portal_type="Property Sheet", id=property_sheet_id)
    script_constraint_id = "organsation_draft_constraint"
    script_constraint = getattr(property_sheet, script_constraint_id, None)
    if script_constraint is None:
      script_constraint = property_sheet.newContent(portal_type="Script Constraint",
        id=script_constraint_id)
    script_constraint.edit(script_id=script_id, constraint_type="upgrader")

  def stepCreateScriptCheckPreUpgradeReferenceConsistency(self, sequence=None):
    portal = self.portal
    skin_folder = portal.portal_skins.custom
    custom_script = getattr(skin_folder, self.script_id, None)
    if custom_script is None:
      skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(self.script_id)
      custom_script = getattr(skin_folder, self.script_id)
      script_body = "error_list = []\n" + \
        "person = context\n" + \
        "reference = person.getReference()\n" + \
        "if reference and not person.getReference().startswith('old_'):\n" + \
        "  kw = {'relative_url': person.getRelativeUrl(), 'reference': person.getReference()}\n" + \
        "  error_list.append('%(relative_url)s <> %(reference)s -> old_%(reference)s' % kw)\n" + \
        "  if fixit:\n" + \
        "    person.setReference('old_%s' % person.getReference())\nreturn error_list"
      custom_script.ZPythonScript_edit('fixit=False, **kw', script_body)
    property_sheet = getattr(portal.portal_property_sheets, self.property_sheet_id, None)
    if property_sheet is None:
      property_sheet = portal.portal_property_sheets.newContent(
        portal_type="Property Sheet", id=self.property_sheet_id)
    script_constraint_id = "person_old_reference_constraint"
    script_constraint = getattr(property_sheet, script_constraint_id, None)
    if script_constraint is None:
      script_constraint = property_sheet.newContent(portal_type="Script Constraint",
        id=script_constraint_id)
    script_constraint.edit(script_id=self.script_id, constraint_type="pre_upgrade")

  def stepCreatePersonPropertySheet(self, sequence=None):
    portal = self.portal
    property_sheet = getattr(portal.portal_property_sheets, self.property_sheet_id, None)
    if property_sheet is None:
      property_sheet = portal.portal_property_sheets.newContent(
        portal_type="Property Sheet", id=self.property_sheet_id)
    script_constraint_id = "person_old_reference_constraint"
    script_constraint = getattr(property_sheet, script_constraint_id, None)
    if script_constraint is None:
      script_constraint = property_sheet.newContent(portal_type="Script Constraint",
        id=script_constraint_id)
    script_constraint.edit(script_id=self.script_id, constraint_type="pre_upgrade")

  def stepSetConstraintInOrganisationPortalType(self, sequence=None):
    types_tool = self.portal.portal_types
    portal_type = types_tool['Organisation']
    property_sheet_id = 'OrganisationDraftConstraint'
    if property_sheet_id not in portal_type.getTypePropertySheetList():
      portal_type.setTypePropertySheetList(
        portal_type.getTypePropertySheetList() + [property_sheet_id,])

  def stepRemoveConstraintFromOrganisationPortalType(self, sequence=None):
    types_tool = self.portal.portal_types
    portal_type = types_tool['Organisation']
    property_sheet_id = 'OrganisationDraftConstraint'
    if property_sheet_id not in portal_type.getTypePropertySheetList():
      portal_type.setTypePropertySheetList(
        [i for i in portal_type.getTypePropertySheetList() \
          if i not in [property_sheet_id,]])

  def stepSetConstraintInPersonPortalType(self, sequence=None):
    types_tool = self.portal.portal_types
    portal_type = types_tool['Person']
    if 'TestPersonConstraint' not in portal_type.getTypePropertySheetList():
      portal_type.setTypePropertySheetList(
        portal_type.getTypePropertySheetList() + [self.property_sheet_id,])

  def _checkAlarmSense(self, alarm_id):
    alarm = getattr(self.portal.portal_alarms, alarm_id)
    alarm.activeSense()
    self.tic()
    active_process = alarm.getLastActiveProcess()
    detail_list = [result.detail for result in active_process.getResultList()]
    return alarm.sense(), detail_list

  def _checkEmptyConstraintList(self, alarm_id):
    alarm = getattr(self.portal.portal_alarms, alarm_id)
    active_process = alarm.getLastActiveProcess()
    if active_process is None:
      self.fail("No active process found")
    self.assertEqual(active_process.getResultList(), [])

  def _checkPersonPreUpgradeConstraintList(self):
    alarm = getattr(self.portal.portal_alarms, 'upgrader_check_pre_upgrade')
    active_process = alarm.getLastActiveProcess()
    result_list = active_process.getResultList()
    detail = result_list[0].detail[0]
    group_dict = DETAIL_PATTERN.match(detail).groupdict()
    person = self.portal.restrictedTraverse(group_dict['relative_url'])
    message_list = [m.message for m in person.checkConsistency()]
    self.assertNotEqual(result_list, [])
    self.assertEqual(len(result_list), 1)
    return person, group_dict, detail, message_list

  def stepCheckPersonPreUpgradeConstraintListAfterUpgrade(self, sequence=None):
    person, group_dict, _, message_list = \
      self._checkPersonPreUpgradeConstraintList()
    self.assertEqual(message_list, [])
    self.assertEqual(person.getReference(), group_dict['new_reference'])

  def stepCheckPersonPreUpgradeConstraintList(self, sequence=None):
    _, _, detail, message_list = self._checkPersonPreUpgradeConstraintList()
    self.assertNotEqual(message_list, [])
    self.assertEqual(message_list, [detail,])

  def stepRemoveConstraintFromPersonPortalType(self, sequence=None):
    if 'Person' in self.portal.portal_types.objectIds():
      portal_type = self.portal.portal_types['Person']
      portal_type.setTypePropertySheetList(
        [x for x in portal_type.getTypePropertySheetList() if x != self.property_sheet_id])

  def stepCheckPreUpgradeEmptyConstraintList(self, sequence=None):
    self._checkEmptyConstraintList('upgrader_check_pre_upgrade')

  def stepCheckPostUpgradeEmptyConstraintList(self, sequence=None):
    self._checkEmptyConstraintList('upgrader_check_post_upgrade')

  def stepCheckPosUpgradeWorkflowChainConsistency(self, sequence=None):
    alarm = getattr(self.portal.portal_alarms, 'upgrader_check_post_upgrade')
    active_process = alarm.getLastActiveProcess()
    detail_list = active_process.getResultList()[0].detail
    message = 'Preference - Expected: edit_workflow, preference_workflow <> Found: (Default)'
    self.assertTrue(message in detail_list, detail_list)
    self.assertTrue(detail_list.count(message), 1)

  def stepSetConstraintInPersonModulePortalType(self, sequence=None):
    types_tool = self.portal.portal_types
    portal_type = types_tool['Person Module']
    if 'PersonModulePostUpgraderConstraint' not in portal_type.getTypePropertySheetList():
      portal_type.setTypePropertySheetList(
        portal_type.getTypePropertySheetList() + ['PersonModulePostUpgraderConstraint',])

  def stepSetConstraintInTemplateToolPortalType(self, sequence=None):
    types_tool = self.portal.portal_types
    portal_type = types_tool['Template Tool']
    property_sheet_list = portal_type.getTypePropertySheetList()
    if 'TemplateToolUpgraderConstraint' not in property_sheet_list:
      portal_type.setTypePropertySheetList(
        portal_type.getTypePropertySheetList() + ['TemplateToolUpgraderConstraint',])
    if 'TemplateToolPostUpgradeConstraint' not in property_sheet_list:
      portal_type.setTypePropertySheetList(
        portal_type.getTypePropertySheetList() + ['TemplateToolPostUpgradeConstraint',])

  def stepSetDefaultWorkflowChainToPreference(self, sequence=None):
    workflow_chain_per_type_dict = {}
    for portal_type, workflow_chain_list in self.portal.ERP5Site_dumpWorkflowChainByPortalType().iteritems():
      workflow_chain_per_type_dict['chain_%s' % portal_type] = ",".join(workflow_chain_list)
    workflow_chain_per_type_dict['chain_Preference'] = '(Default)'
    self.portal.portal_workflow.manage_changeWorkflows(default_chain="",
      props=workflow_chain_per_type_dict)

  def _stepSolveAlarm(self, alarm_id):
    getattr(self.portal.portal_alarms, alarm_id).solve()

  def stepActiveSenseUpgradeAlarm(self, sequence=None):
    getattr(self.portal.portal_alarms, "upgrader_check_upgrader").activeSense()

  def stepActiveSensePostUpgradeAlarm(self, sequence=None):
    getattr(self.portal.portal_alarms,
      "upgrader_check_post_upgrade").activeSense()

  def stepActiveSensePreUpgradeAlarm(self, sequence=None):
    getattr(self.portal.portal_alarms,
      "upgrader_check_pre_upgrade").activeSense()

  def stepActiveSensePromiseCheckUpgrade(self, sequence=None):
    getattr(self.portal.portal_alarms,
      "promise_check_upgrade").activeSense()

  def stepRunFullUpgrader(self, sequence=None):
    self._stepSolveAlarm("promise_check_upgrade")

  def stepRunUpgrader(self, sequence=None):
    self._stepSolveAlarm("upgrader_check_upgrader")

  def stepRunPostUpgrade(self, sequence=None):
    self._stepSolveAlarm("upgrader_check_post_upgrade")

  def stepRunPreUpgrade(self, sequence=None):
    self._stepSolveAlarm("upgrader_check_pre_upgrade")

  def stepCheckUpgradeRequired(self, sequence=None):
    sense, detail_list = self._checkAlarmSense(
      alarm_id="upgrader_check_upgrader")
    self.assertTrue(sense, detail_list)

  def stepCheckUpgradeNotRequired(self, sequence=None):
    sense, detail_list = self._checkAlarmSense(
      alarm_id="upgrader_check_upgrader")
    self.assertFalse(sense, detail_list)

  def stepCheckPostUpgradeRequired(self, sequence=None):
    sense, detail_list = self._checkAlarmSense(
      alarm_id="upgrader_check_post_upgrade")
    self.assertTrue(sense, detail_list)

  def stepCheckFullUpgradeRequired(self, sequence=None):
    sense, detail_list = self._checkAlarmSense(
      alarm_id="promise_check_upgrade")
    self.assertTrue(sense, detail_list)

  def stepCheckPostUpgradeNotRequired(self, sequence=None):
    sense, detail_list = self._checkAlarmSense(
      alarm_id="upgrader_check_post_upgrade")
    self.assertFalse(sense, detail_list)

  def stepUninstallERP5Web(self, sequence=None):
    bt5 = self.portal.portal_templates.getInstalledBusinessTemplate('erp5_web')
    if bt5 is not None:
      bt5.uninstall()

  def stepCheckERP5WebBTInstalled(self, sequence=None):
    self.assertTrue('erp5_web' in \
      self.portal.portal_templates.getInstalledBusinessTemplateTitleList())

  def stepCheckNoActivitiesCreated(self, sequence=None):
    transaction.commit()
    portal_activities = self.getActivityTool()
    message = portal_activities.getMessageList()[0]
    self.assertEqual(message.method_id, "Alarm_runUpgrader")
    portal_templates = self.getTemplateTool()
    title_list = portal_templates.getInstalledBusinessTemplateTitleList()
    self.assertTrue('erp5_web' not in title_list,
      "%s found in %s" % ('erp5_web', title_list))
    portal_activities.manageInvoke(message.object_path, message.method_id)
    title_list = portal_templates.getInstalledBusinessTemplateTitleList()
    self.assertTrue('erp5_web' in title_list,
      "%s not found in %s" % ('erp5_web', title_list))
    transaction.commit()
    message_list = set([i.method_id for i in portal_activities.getMessageList()])
    self.assertTrue('callMethodOnObjectList' not in message_list)

  def stepCreateBigIncosistentData(self, sequence=None):
    for _ in range(101):
      self.portal.organisation_module.newContent(
        portal_type="Organisation",
        title="org_%s" % self.portal.organisation_module.getLastId())

  def stepCreateSmallIncosistentData(self, sequence=None):
    for _ in range(4):
      self.portal.organisation_module.newContent(
        portal_type="Organisation",
        title="org_%s" % self.portal.organisation_module.getLastId())

  def stepCheckActivitiesCreated(self, sequence=None):
    transaction.commit()
    portal_activities = self.getActivityTool()
    message = portal_activities.getMessageList()[0]
    self.assertEqual(message.method_id, "Alarm_runUpgrader")
    portal_activities.manageInvoke(message.object_path, message.method_id)
    transaction.commit()
    message_list = portal_activities.getMessageList()
    method_id_list = set([i.method_id for i in message_list])
    self.assertTrue('callMethodOnObjectList' in method_id_list)
    for message in message_list:
      if message.method_id == 'callMethodOnObjectList':
        self.assertEqual(message.args[-1], 'Base_postCheckConsistencyResult')

  def stepUninstallERP5UpgraderTestBT(self, sequence=None):
    bt5 = self.portal.portal_templates.getInstalledBusinessTemplate('erp5_web')
    bt5.uninstall()

  def stepInstallERP5UpgraderTestBT(self, sequence=None):
    template_tool = self.portal.portal_templates
    if 'erp5_upgrader_test' not in template_tool.getInstalledBusinessTemplateTitleList():
      template_tool.installBusinessTemplateListFromRepository('erp5_upgrader_test')

  def _getTemplateToolLastTimestampIndexation(self):
    portal = self.portal
    return portal.portal_catalog(select_list=['indexation_timestamp'],
      uid=portal.portal_templates.getUid())[0].indexation_timestamp

  def stepCheckSummaryForPreUpgradeRequired(self, sequence=None):
    alarm = self.portal.portal_alarms.upgrader_check_upgrader
    active_process = alarm.getLastActiveProcess()
    detail = active_process.getResultList()[0].detail
    self.assertTrue("Is required solve Pre Upgrade first" in detail)

  def stepCheckPersonNotInConstraintTypeListPerPortalType(self, sequence=None):
    constraint_type_per_type, _ = \
      self.portal.Base_getConstraintTypeListPerPortalType()
    self.assertFalse("Person" in constraint_type_per_type.keys(), \
      "Person in %s" % constraint_type_per_type.keys())

  def stepRemoveSameConstraintInPersonAndPersonModule(self, sequence=None):
    types_tool = self.portal.portal_types
    person_type = types_tool["Person"]
    constraint_id = "PersonModulePostUpgraderConstraint"
    propery_sheet_list = person_type.getTypePropertySheetList()
    if constraint_id in propery_sheet_list:
      propery_sheet_list.remove(constraint_id)      
      person_type.setTypePropertySheetList(propery_sheet_list)

    person_module_type = types_tool["Person Module"]
    propery_sheet_list = person_module_type.getTypePropertySheetList()
    if constraint_id in propery_sheet_list:
      propery_sheet_list.remove(constraint_id)
      person_module_type.setTypePropertySheetList(propery_sheet_list)

  def stepSameConstraintToPersonAndPersonModule(self, sequence=None):
    types_tool = self.portal.portal_types
    person_type = types_tool["Person"]
    constraint_id = "PersonModulePostUpgraderConstraint"
    propery_sheet_list = person_type.getTypePropertySheetList()
    if constraint_id not in propery_sheet_list:
      person_type.setTypePropertySheetList(
        [constraint_id,] + propery_sheet_list)

    person_module_type = types_tool["Person Module"]
    propery_sheet_list = person_module_type.getTypePropertySheetList()
    if constraint_id not in propery_sheet_list:
      person_module_type.setTypePropertySheetList(
        [constraint_id,] + propery_sheet_list)

    self.assertTrue(constraint_id in person_type.getTypePropertySheetList())
    self.assertTrue(
      constraint_id in person_module_type.getTypePropertySheetList())

  def stepCreateAndInstallBusinessTemplate(self, sequence=None):
    bt5 = self.portal.portal_templates.newContent(
      portal_type='Business Template',
      title=self.id())
    bt5.install()
    sequence.edit(bt5=bt5)

  def stepUninstallBusinessTemplateInstalled(self, sequence=None):
    sequence.get("bt5").uninstall()

  def stepCheckBusinessTemplateInstalled(self, sequence=None):
    self.assertTrue(sequence.get('bt5').getTitle() in \
      self.portal.portal_templates.getInstalledBusinessTemplateTitleList())

  def stepCheckConsistencyInTemplateTool(self, sequence=None):
    try:
      self.portal.portal_templates.checkConsistency()
    except BusinessTemplateUnknownError:
      self.fail("checkConsistency should not raise exception."
        "It means that one Business Template was not found in repositories")

  def test_workflow_chain_constraint(self):
    """ Check if Workflow chains is broken, it can be detected and fixed after
    upgrade"""
    sequence_list = SequenceList()
    sequence_string = """
      stepActiveSensePreUpgradeAlarm
      stepTic
      stepRunUpgrader
      stepTic
      stepCheckUpgradeNotRequired
      stepTic
      stepSetConstraintInTemplateToolPortalType
      stepActiveSensePostUpgradeAlarm
      stepTic
      stepCheckPostUpgradeEmptyConstraintList
      stepSetDefaultWorkflowChainToPreference
      stepActiveSensePostUpgradeAlarm
      stepTic
      stepCheckPosUpgradeWorkflowChainConsistency
      stepRunPostUpgrade
      stepTic
      stepActiveSensePostUpgradeAlarm
      stepTic
      stepCheckPostUpgradeEmptyConstraintList
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_not_post_many_active_result_when_upgrade(self):
    """ Check that is possible fix consistency before the upgrade"""
    sequence_list = SequenceList()
    sequence_string = """
      stepCreatePerson
      stepCreatePerson
      stepTic
      stepCreateScriptCheckPreUpgradeReferenceConsistency
      stepCreatePersonPropertySheet
      stepSetConstraintInPersonPortalType
      stepActiveSensePreUpgradeAlarm
      stepTic
      stepCheckPersonPreUpgradeConstraintList
      stepRunPreUpgrade
      stepTic
      stepCheckPersonPreUpgradeConstraintListAfterUpgrade
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_add_pre_upgrade_constraint(self):
    """ Check that is possible fix consistency before the upgrade"""
    sequence_list = SequenceList()
    sequence_string = """
      stepCreatePerson
      stepTic
      stepCreateScriptCheckPreUpgradeReferenceConsistency
      stepCreatePersonPropertySheet
      stepSetConstraintInPersonPortalType
      stepTic
      stepActiveSensePreUpgradeAlarm
      stepTic
      stepCheckPersonPreUpgradeConstraintList
      stepRemoveConstraintFromPersonPortalType
      stepActiveSensePreUpgradeAlarm
      stepTic
      stepCheckPreUpgradeEmptyConstraintList
      stepSetConstraintInPersonPortalType
      stepRunPreUpgrade
      stepTic
      stepCheckPersonPreUpgradeConstraintListAfterUpgrade
      stepActiveSensePreUpgradeAlarm
      stepTic
      stepCheckPreUpgradeEmptyConstraintList
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_can_not_run_post_upgrade_without_solve_upgrade(self):
    """Check that if there is something to solve in pre_upgrade and upgrade is
    not possible run the post upgrade"""
    sequence_list = SequenceList()
    sequence_string = """
      stepUninstallERP5Web
      stepSetConstraintInPersonModulePortalType
      stepTic
      stepCheckUpgradeRequired
      stepCheckPostUpgradeNotRequired
      stepCreatePerson
      stepValidatePerson
      stepTic
      stepCheckPostUpgradeRequired
      stepRunPostUpgrade
      stepTic
      stepCheckUpgradeRequired
      stepCheckPostUpgradeRequired
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_can_not_run_upgrade_without_solve_pre_upgrade(self):
    """Check that if there is something to solve in pre_upgrade is not possible
    run the upgrade"""
    sequence_list = SequenceList()
    sequence_string = """
      stepCreatePerson
      stepCreateScriptCheckPreUpgradeReferenceConsistency
      stepCreatePersonPropertySheet
      stepSetConstraintInPersonPortalType
      stepUninstallERP5Web
      stepTic
      stepActiveSensePreUpgradeAlarm
      stepTic
      stepRunUpgrader
      stepTic
      stepCheckSummaryForPreUpgradeRequired
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_upgrade_in_one_transaction(self):
    """Check that all constraints with contraint_type equal upgrade run in the 
    same transaction"""
    sequence_list = SequenceList()
    sequence_string = """
      stepCreatePropertySheetToValidateOrganisation
      stepUninstallERP5Web
      stepInstallERP5UpgraderTestBT
      stepTic
      stepActiveSensePromiseCheckUpgrade
      stepTic
      stepRunPreUpgrade
      stepTic
      stepSetConstraintInOrganisationPortalType
      stepCreateSmallIncosistentData
      stepTic
      stepActiveSenseUpgradeAlarm
      stepTic
      stepRunUpgrader
      stepCheckNoActivitiesCreated
      stepCreateBigIncosistentData
      stepTic
      stepActiveSenseUpgradeAlarm
      stepTic
      stepRunUpgrader
      stepCheckActivitiesCreated
      stepRemoveConstraintFromOrganisationPortalType
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_ignore_allowed_content_type(self):
    """
      Check that allowed content types should be ignored from a give \
      portal type in Base_getConstraintTypeListPerPortalType, \
      because checkConsistency is recursive in folders.
      Then, if not ignored this method will be called twice
    """
    sequence_list = SequenceList()
    sequence_string = """
      stepSameConstraintToPersonAndPersonModule
      stepCheckPersonNotInConstraintTypeListPerPortalType
      stepRemoveSameConstraintInPersonAndPersonModule
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_post_upgrade_with_bt5_that_not_exists_in_repository(self):
    """
      One Business Template installed that not exists in repository, 
      should not block checkConsistency in portal_templates
    """
    sequence_list = SequenceList()
    sequence_string = """
      stepCreateAndInstallBusinessTemplate
      stepTic
      stepCheckBusinessTemplateInstalled
      stepCheckConsistencyInTemplateTool
      stepUninstallBusinessTemplateInstalled
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_upgrade_instance(self):
    """Check that running the alarm the instance is upgraded completely"""
    sequence_list = SequenceList()
    sequence_string = """
      stepUninstallERP5Web
      stepInstallERP5UpgraderTestBT
      stepTic
      stepActiveSensePreUpgradeAlarm
      stepActiveSensePostUpgradeAlarm
      stepActiveSenseUpgradeAlarm
      stepTic
      stepCheckFullUpgradeRequired
      stepRunFullUpgrader
      stepTic
      stepCheckERP5WebBTInstalled
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)
