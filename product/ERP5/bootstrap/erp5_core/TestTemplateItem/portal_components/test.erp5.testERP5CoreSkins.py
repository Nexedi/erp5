# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2024 Nexedi SA and Contributors.
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
#
##############################################################################

import transaction
from zExceptions import Unauthorized
from DateTime import DateTime
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from time import sleep


class TemporaryAlarmScript(object):
  """
  Context manager for temporary alarm python scripts
  """
  def __init__(self, portal, script_name, fake_return="", attribute=None):
    self.script_name = script_name
    self.portal = portal
    self.fake_return = fake_return
    self.attribute = attribute

  def __enter__(self):
    if self.script_name in self.portal.portal_skins.custom.objectIds():
      raise ValueError('Precondition failed: %s exists in custom' % self.script_name)
    if self.attribute is None:
      content = """portal_workflow = context.portal_workflow
portal_workflow.doActionFor(context, action='edit_action', comment='Visited by %s')
return %s""" % (self.script_name, self.fake_return)
    else:
      content = """portal_workflow = context.portal_workflow
context.edit(%s='Visited by %s')
return %s""" % (self.attribute, self.script_name, self.fake_return)
    createZODBPythonScript(self.portal.portal_skins.custom,
                        self.script_name,
                        '*args, **kwargs',
                        '# Script body\n' + content)
    transaction.commit()

  def __exit__(self, exc_type, exc_value, traceback):
    if self.script_name in self.portal.portal_skins.custom.objectIds():
      self.portal.portal_skins.custom.manage_delObjects(self.script_name)
    transaction.commit()


class TestBase_reindexAndSenseAlarm(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    """Business Templates required for this test.
    """
    return ('erp5_full_text_mroonga_catalog', 'erp5_simulation_test', )

  def afterSetUp(self):
    # Ensure the alarms has a workflow history
    for alarm_id in ['invoice_builder_alarm',
                     'packing_list_builder_alarm']:
      alarm = self.portal.portal_alarms[alarm_id]
      old_comment = alarm.getProperty('comment')
      alarm.edit(comment='%s foo' % old_comment)
      alarm.edit(comment=old_comment)

    return super(TestBase_reindexAndSenseAlarm, self).afterSetUp()

  def beforeTearDown(self):
    transaction.abort()

  def assertLessThan(self, value1, value2):
    self.assertTrue(value1 < value2, 'Expected: %s < %s' % (value1, value2))

  def getIndexationDate(self, document):
    return DateTime(self.portal.portal_catalog(
      uid=document.getUid(),
      select_list=['indexation_timestamp']
    )[0].indexation_timestamp)

  def test_reindexAndSenseAlarm_REQUEST_disallowed(self):
    document = self.portal.internal_order_module
    self.assertRaises(
      Unauthorized,
      document.Base_reindexAndSenseAlarm,
      [],
      REQUEST={})

  def test_reindexAndSenseAlarm_callAlarmAfterContextReindex(self):
    # Check that the alarm is triggered
    # only after the context is reindexed
    document = self.portal.internal_order_module
    alarm = self.portal.portal_alarms.invoice_builder_alarm
    document.Base_reindexAndSenseAlarm(['invoice_builder_alarm'])

    previous_indexation_timestamp = self.getIndexationDate(document)
    workflow_history_count = len(alarm.workflow_history['edit_workflow'])

    # Sadly, catalog indexation timestamp has a second precision
    # It is needed to wait this 1 second to be able to verify new indexation
    sleep(1)
    with TemporaryAlarmScript(alarm, 'Alarm_buildInvoice'):
      self.tic()

    next_indexation_timestamp = self.getIndexationDate(document)
    edit_timestamp = alarm.getModificationDate()
    # check that the document has been reindexed
    self.assertLessThan(previous_indexation_timestamp, next_indexation_timestamp)
    # check that alarm was called after the object was reindexed
    self.assertLessThan(next_indexation_timestamp, edit_timestamp)

    self.assertEqual(
      len(alarm.workflow_history['edit_workflow']),
      workflow_history_count + 1
    )
    self.assertEqual(
      'Visited by Alarm_buildInvoice',
      alarm.workflow_history['edit_workflow'][-1]['comment']
    )

  def test_reindexAndSenseAlarm_callAlarmWithoutContextReindex(self):
    # Check that the alarm is triggered
    # without reindexing the context
    document = self.portal.internal_order_module
    alarm = self.portal.portal_alarms.invoice_builder_alarm
    document.Base_reindexAndSenseAlarm(['invoice_builder_alarm'],
                                       must_reindex_context=False)

    previous_indexation_timestamp = self.getIndexationDate(document)
    workflow_history_count = len(alarm.workflow_history['edit_workflow'])

    # Sadly, catalog indexation timestamp has a second precision
    # It is needed to wait this 1 second to be able to verify new indexation
    sleep(1)
    with TemporaryAlarmScript(alarm, 'Alarm_buildInvoice'):
      self.tic()

    next_indexation_timestamp = self.getIndexationDate(document)
    edit_timestamp = alarm.getModificationDate()
    # check that the document was not reindexed
    self.assertEqual(previous_indexation_timestamp, next_indexation_timestamp)
    # check that alarm was called after the object was reindexed
    self.assertLessThan(next_indexation_timestamp, edit_timestamp)

    self.assertEqual(
      len(alarm.workflow_history['edit_workflow']),
      workflow_history_count + 1
    )
    self.assertEqual(
      'Visited by Alarm_buildInvoice',
      alarm.workflow_history['edit_workflow'][-1]['comment']
    )

  def test_reindexAndSenseAlarm_doesNotReindexIfNoAlarm(self):
    # Check that no alarm is triggered
    # and the context is not reindexed
    document = self.portal.internal_order_module
    alarm = self.portal.portal_alarms.invoice_builder_alarm
    document.Base_reindexAndSenseAlarm([])

    previous_indexation_timestamp = self.getIndexationDate(document)
    workflow_history_count = len(alarm.workflow_history['edit_workflow'])

    # Sadly, catalog indexation timestamp has a second precision
    # It is needed to wait this 1 second to be able to verify new indexation
    sleep(1)
    with TemporaryAlarmScript(alarm, 'Alarm_buildInvoice'):
      self.tic()

    next_indexation_timestamp = self.getIndexationDate(document)
    # check that the document was not reindex
    self.assertEqual(previous_indexation_timestamp, next_indexation_timestamp)
    # check that the alarm was not triggered
    self.assertEqual(
      len(alarm.workflow_history['edit_workflow']),
      workflow_history_count
    )

  def test_reindexAndSenseAlarm_twiceInTheSameTransaction(self):
    # Check that the alarm is triggered only ONCE
    # if the script is called twice in a transaction
    document = self.portal.internal_order_module
    alarm = self.portal.portal_alarms.invoice_builder_alarm
    document.Base_reindexAndSenseAlarm(['invoice_builder_alarm'])
    document.Base_reindexAndSenseAlarm(['invoice_builder_alarm'])

    previous_indexation_timestamp = self.getIndexationDate(document)
    workflow_history_count = len(alarm.workflow_history['edit_workflow'])

    # Sadly, catalog indexation timestamp has a second precision
    # It is needed to wait this 1 second to be able to verify new indexation
    sleep(1)
    with TemporaryAlarmScript(alarm, 'Alarm_buildInvoice'):
      self.tic()

    next_indexation_timestamp = self.getIndexationDate(document)
    edit_timestamp = alarm.getModificationDate()
    # check that the document has been reindexed
    self.assertLessThan(previous_indexation_timestamp, next_indexation_timestamp)
    # check that alarm was called ONCE after the object was reindexed
    self.assertLessThan(next_indexation_timestamp, edit_timestamp)

    self.assertEqual(
      len(alarm.workflow_history['edit_workflow']),
      workflow_history_count + 1
    )
    self.assertEqual(
      'Visited by Alarm_buildInvoice',
      alarm.workflow_history['edit_workflow'][-1]['comment']
    )

  def test_reindexAndSenseAlarm_twiceInTheSameTransactionWithoutReindex(self):
    # Check that the alarm is triggered only ONCE
    # if the script is called twice in a transaction
    document = self.portal.internal_order_module
    alarm = self.portal.portal_alarms.invoice_builder_alarm
    document.Base_reindexAndSenseAlarm(['invoice_builder_alarm'],
                                       must_reindex_context=False)
    document.Base_reindexAndSenseAlarm(['invoice_builder_alarm'],
                                       must_reindex_context=False)

    workflow_history_count = len(alarm.workflow_history['edit_workflow'])

    with TemporaryAlarmScript(alarm, 'Alarm_buildInvoice'):
      self.tic()

    # check that alarm was called ONCE
    self.assertEqual(
      len(alarm.workflow_history['edit_workflow']),
      workflow_history_count + 1
    )
    self.assertEqual(
      'Visited by Alarm_buildInvoice',
      alarm.workflow_history['edit_workflow'][-1]['comment']
    )

  def test_reindexAndSenseAlarm_twiceInTheTwoTransactions(self):
    # Check that the alarm is triggered only ONCE
    # if the script is called twice in a transaction
    document = self.portal.internal_order_module
    alarm = self.portal.portal_alarms.invoice_builder_alarm
    document.Base_reindexAndSenseAlarm(['invoice_builder_alarm'])
    transaction.commit()
    document.Base_reindexAndSenseAlarm(['invoice_builder_alarm'])

    previous_indexation_timestamp = self.getIndexationDate(document)
    workflow_history_count = len(alarm.workflow_history['edit_workflow'])

    # Sadly, catalog indexation timestamp has a second precision
    # It is needed to wait this 1 second to be able to verify new indexation
    sleep(1)
    with TemporaryAlarmScript(alarm, 'Alarm_buildInvoice'):
      self.tic()

    next_indexation_timestamp = self.getIndexationDate(document)
    edit_timestamp = alarm.getModificationDate()
    # check that the document has been reindexed
    self.assertLessThan(previous_indexation_timestamp, next_indexation_timestamp)
    # check that alarm was called ONCE after the object was reindexed
    self.assertLessThan(next_indexation_timestamp, edit_timestamp)

    self.assertEqual(
      len(alarm.workflow_history['edit_workflow']),
      workflow_history_count + 1
    )
    self.assertEqual(
      'Visited by Alarm_buildInvoice',
      alarm.workflow_history['edit_workflow'][-1]['comment']
    )

  def test_reindexAndSenseAlarm_alarmActive(self):
    # Check that the script wait for the alarm to be not activate
    # before triggering it again
    document = self.portal.internal_order_module
    alarm = self.portal.portal_alarms.invoice_builder_alarm

    tag = 'foobar'
    alarm.activate(tag=tag).getId()
    # Call edit, to ensure the last edit contains the comment value
    alarm.activate(after_tag=tag, tag=tag+'1').edit(description=alarm.getDescription() + ' ')
    alarm.activate(after_tag=tag+'1').edit(description=alarm.getDescription()[:-1])
    transaction.commit()
    document.Base_reindexAndSenseAlarm(['invoice_builder_alarm'],
                                       must_reindex_context=False)

    workflow_history_count = len(alarm.workflow_history['edit_workflow'])
    with TemporaryAlarmScript(alarm, 'Alarm_buildInvoice'):
      self.tic()

    self.assertEqual(
      len(alarm.workflow_history['edit_workflow']),
      workflow_history_count + 3
    )
    self.assertEqual(
      'Visited by Alarm_buildInvoice',
      alarm.workflow_history['edit_workflow'][-1]['comment']
    )

  def test_reindexAndSenseAlarm_twoContextSameTransaction(self):
    # Check that the script wait for the alarm to be not activate
    # before triggering it again
    document1 = self.portal.internal_order_module
    document2 = self.portal.internal_packing_list_module
    alarm = self.portal.portal_alarms.invoice_builder_alarm

    document1.Base_reindexAndSenseAlarm(['invoice_builder_alarm'])
    document2.Base_reindexAndSenseAlarm(['invoice_builder_alarm'])

    previous_indexation_timestamp1 = self.getIndexationDate(document1)
    previous_indexation_timestamp2 = self.getIndexationDate(document2)
    workflow_history_count = len(alarm.workflow_history['edit_workflow'])

    # Sadly, catalog indexation timestamp has a second precision
    # It is needed to wait this 1 second to be able to verify new indexation
    sleep(1)
    with TemporaryAlarmScript(alarm, 'Alarm_buildInvoice'):
      self.tic()

    next_indexation_timestamp1 = self.getIndexationDate(document1)
    next_indexation_timestamp2 = self.getIndexationDate(document2)
    edit_timestamp = alarm.getModificationDate()
    # check that the document has been reindexed
    self.assertLessThan(previous_indexation_timestamp1, next_indexation_timestamp1)
    self.assertLessThan(previous_indexation_timestamp2, next_indexation_timestamp2)
    # check that alarm was called after the object was reindexed
    self.assertLessThan(next_indexation_timestamp1, edit_timestamp)
    self.assertLessThan(next_indexation_timestamp2, edit_timestamp)

    self.assertEqual(
      len(alarm.workflow_history['edit_workflow']),
      workflow_history_count + 1
    )
    self.assertEqual(
      'Visited by Alarm_buildInvoice',
      alarm.workflow_history['edit_workflow'][-1]['comment']
    )

  def test_reindexAndSenseAlarm_twoContextDifferentTransaction(self):
    # Check that the script wait for the alarm to be not activate
    # before triggering it again
    document1 = self.portal.internal_order_module
    document2 = self.portal.internal_packing_list_module
    alarm = self.portal.portal_alarms.invoice_builder_alarm

    document1.Base_reindexAndSenseAlarm(['invoice_builder_alarm'])
    document2.Base_reindexAndSenseAlarm(['invoice_builder_alarm'])

    previous_indexation_timestamp1 = self.getIndexationDate(document1)
    transaction.commit()
    previous_indexation_timestamp2 = self.getIndexationDate(document2)
    workflow_history_count = len(alarm.workflow_history['edit_workflow'])

    # Sadly, catalog indexation timestamp has a second precision
    # It is needed to wait this 1 second to be able to verify new indexation
    sleep(1)
    with TemporaryAlarmScript(alarm, 'Alarm_buildInvoice'):
      self.tic()

    next_indexation_timestamp1 = self.getIndexationDate(document1)
    next_indexation_timestamp2 = self.getIndexationDate(document2)
    edit_timestamp = alarm.getModificationDate()
    # check that the document has been reindexed
    self.assertLessThan(previous_indexation_timestamp1, next_indexation_timestamp1)
    self.assertLessThan(previous_indexation_timestamp2, next_indexation_timestamp2)
    # check that alarm was called after the object was reindexed
    self.assertLessThan(next_indexation_timestamp1, edit_timestamp)
    self.assertLessThan(next_indexation_timestamp2, edit_timestamp)

    self.assertEqual(
      len(alarm.workflow_history['edit_workflow']),
      workflow_history_count + 1
    )
    self.assertEqual(
      'Visited by Alarm_buildInvoice',
      alarm.workflow_history['edit_workflow'][-1]['comment']
    )

  def test_reindexAndSenseAlarm_twoAlarm(self):
    # Check that the script wait for the alarm to be not activate
    # before triggering it again
    document = self.portal.internal_order_module
    alarm1 = self.portal.portal_alarms.invoice_builder_alarm
    alarm2 = self.portal.portal_alarms.packing_list_builder_alarm

    document.Base_reindexAndSenseAlarm(['invoice_builder_alarm',
                                        'packing_list_builder_alarm'])

    previous_indexation_timestamp = self.getIndexationDate(document)
    workflow_history_count1 = len(alarm1.workflow_history['edit_workflow'])
    workflow_history_count2 = len(alarm2.workflow_history['edit_workflow'])

    # Sadly, catalog indexation timestamp has a second precision
    # It is needed to wait this 1 second to be able to verify new indexation
    sleep(1)
    with TemporaryAlarmScript(alarm1, 'Alarm_buildInvoice'):
      with TemporaryAlarmScript(alarm2, 'Alarm_buildPackingList'):
        self.tic()

    next_indexation_timestamp = self.getIndexationDate(document)
    edit_timestamp1 = alarm1.getModificationDate()
    edit_timestamp2 = alarm2.getModificationDate()
    self.assertLessThan(previous_indexation_timestamp, next_indexation_timestamp)
    # check that alarm was called after the object was reindexed
    self.assertLessThan(next_indexation_timestamp, edit_timestamp1)
    self.assertLessThan(next_indexation_timestamp, edit_timestamp2)

    self.assertEqual(
      len(alarm1.workflow_history['edit_workflow']),
      workflow_history_count1 + 1
    )
    self.assertEqual(
      'Visited by Alarm_buildInvoice',
      alarm1.workflow_history['edit_workflow'][-1]['comment']
    )
    self.assertEqual(
      len(alarm2.workflow_history['edit_workflow']),
      workflow_history_count2 + 1
    )
    self.assertEqual(
      'Visited by Alarm_buildPackingList',
      alarm2.workflow_history['edit_workflow'][-1]['comment']
    )
