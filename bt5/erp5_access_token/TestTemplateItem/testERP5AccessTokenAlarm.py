# Copyright (c) 2002-2013 Nexedi SA and Contributors. All Rights Reserved.
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestERP5AccessTokenAlarm(ERP5TypeTestCase):

  def test_alarm_old_validated_restricted_access_token(self):
    access_token = self.portal.access_token_module.newContent(
      portal_type="One Time Restricted Access Token",
    )
    access_token.workflow_history['edit_workflow'] = [{
        'comment':'Fake history',
        'error_message': '',
        'actor': 'ERP5TypeTestCase',
        'state': 'current',
        'time': DateTime('2012/11/15 11:11'),
        'action': 'foo_action'
        }]
    self.portal.portal_workflow._jumpToStateFor(access_token, 'validated')
    self.tic()
    
    self.portal.portal_alarms.\
      erp5_garbage_collect_one_time_restricted_access_token.activeSense()
    self.tic()

    self.assertEqual('invalidated', access_token.getValidationState())
    self.assertEqual(
        'Unused for 1 day.',
        access_token.workflow_history['validation_workflow'][-1]['comment'])

  def test_alarm_recent_validated_restricted_access_token(self):
    access_token = self.portal.access_token_module.newContent(
      portal_type="One Time Restricted Access Token",
    )
    self.portal.portal_workflow._jumpToStateFor(access_token, 'validated')
    self.tic()
    
    self.portal.portal_alarms.\
      erp5_garbage_collect_one_time_restricted_access_token.activeSense()
    self.tic()

    self.assertEqual('validated', access_token.getValidationState())

  def test_alarm_old_non_validated_restricted_access_token(self):
    access_token = self.portal.access_token_module.newContent(
      portal_type="One Time Restricted Access Token",
    )
    access_token.workflow_history['edit_workflow'] = [{
        'comment':'Fake history',
        'error_message': '',
        'actor': 'ERP5TypeTestCase',
        'state': 'current',
        'time': DateTime('2012/11/15 11:11'),
        'action': 'foo_action'
        }]
    self.tic()
    
    self.portal.portal_alarms.\
      erp5_garbage_collect_one_time_restricted_access_token.activeSense()
    self.tic()

    self.assertEqual('draft', access_token.getValidationState())
