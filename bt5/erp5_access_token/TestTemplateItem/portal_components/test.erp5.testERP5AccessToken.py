# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2019 Nexedi SA and Contributors. All Rights Reserved.
#                    Tristan Cavelier <tristan.cavelier@nexedi.com>
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

from DateTime import DateTime
from six.moves.urllib.parse import urlencode
import six.moves.http_client
import mock
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Utils import str2bytes


class AccessTokenTestCase(ERP5TypeTestCase):
  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_access_token')

  def _createPerson(self, new_id):
    """Creates a person in person module, and returns the object, after
    indexing is done. """
    person_module = self.getPersonModule()
    person = person_module.newContent(portal_type='Person',
      reference='TESTP-' + new_id)
    person.newContent(portal_type='Assignment').open()
    person.newContent(portal_type='ERP5 Login', reference=new_id).validate()
    self.tic()
    return person


class TestERP5AccessTokenSkins(AccessTokenTestCase):

  def generateNewId(self):
    return str(self.portal.portal_ids.generateNewId(
         id_group=('erp5_access_token_test_id')))

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.new_id = self.generateNewId()
    self.portal.portal_templates.TemplateTool_checkERP5AccessTokenExtractionPluginExistenceConsistency(
        fixit=True)
    self.tic()

  def _getTokenCredential(self, request):
    """Authenticate the request and return (user_id, login) or None if not authorized."""
    plugin = self.portal.acl_users.erp5_access_token_plugin
    return plugin.authenticateCredentials(plugin.extractCredentials(request))

  def _createRestrictedAccessToken(self, new_id, person, method, url_string):
    access_token = self.portal.access_token_module.newContent(
                    portal_type="Restricted Access Token",
                    url_string=url_string,
                    url_method=method,
                  )
    if person:
      access_token.edit(agent_value=person)
    return access_token

  def _createOneTimeRestrictedAccessToken(self, new_id, person, method, url_string):
    access_token = self.portal.access_token_module.newContent(
                    portal_type="One Time Restricted Access Token",
                    url_string=url_string,
                    url_method=method,
                  )
    if person:
      access_token.edit(agent_value=person)
    return access_token

  def test_working_token(self):
    person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST.form["access_token"] = access_token.getId()
    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url
    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    with mock.patch(
        'Products.ERP5Security.ERP5AccessTokenExtractionPlugin._setUserNameForAccessLog'
      ) as _setUserNameForAccessLog:
      result = self._getTokenCredential(self.portal.REQUEST)
    self.assertTrue(result)
    user_id, login = result
    self.assertEqual(user_id, person.Person_getUserId())
    # tokens have a login value, for auditing purposes. This is the ID of the plugin
    # and the relative URL of the token.
    self.assertEqual('erp5_access_token_plugin=%s' % access_token.getRelativeUrl(), login)
    # this is also what will appear in Z2.log
    _setUserNameForAccessLog.assert_called_once_with(login, self.portal.REQUEST)

  def test_user_caption(self):
    person = self._createPerson(self.new_id)
    access_url = "%s/Base_getUserCaption" % self.portal.absolute_url()
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(
        self.new_id,
        person,
        access_method,
        access_url)
    access_token.validate()
    self.tic()

    response = self.publish('/%s/Base_getUserCaption?%s' % (
        self.portal.getId(),
        urlencode({
            'access_token': access_token.getId(),
            'access_token_secret': access_token.getReference()})))
    self.assertEqual(response.getStatus(), six.moves.http_client.OK)
    # XXX caption currently shows plugin id and relative URL of the token,
    # that's not ideal.
    self.assertEqual(
        response.getBody(),
        str2bytes('erp5_access_token_plugin=%s' % access_token.getRelativeUrl()))

  def test_bad_token(self):
    person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST.form["access_token"] = "XYSYDT-YDTYSD"
    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url
    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    result = self._getTokenCredential(self.portal.REQUEST)
    self.assertFalse(result)

  def test_token_without_assignment(self):
    # Token does not work when person has no open assignment
    person = self._createPerson(self.new_id)
    for assignment in person.contentValues(portal_type='Assignment'):
      assignment.close()
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST.form["access_token"] = access_token.getId()
    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url
    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    result = self._getTokenCredential(self.portal.REQUEST)
    self.assertFalse(result)

  def test_token_without_login(self):
    # Token does not work when person has no validated login
    person = self._createPerson(self.new_id)
    for login in person.contentValues(portal_type='ERP5 Login'):
      login.invalidate()
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST.form["access_token"] = access_token.getId()
    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url
    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    result = self._getTokenCredential(self.portal.REQUEST)
    self.assertFalse(result)

  def test_RestrictedAccessToken_getUserValue(self):
    person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url
    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    result = access_token.RestrictedAccessToken_getUserValue()

    self.assertEqual(result, person)
    self.assertEqual(access_token.getValidationState(), 'validated')

  def test_RestrictedAccessToken_getUserValue_access_token_secret(self):
    person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url

    result = access_token.RestrictedAccessToken_getUserValue()
    self.assertEqual(result, None)

    self.portal.REQUEST.form["access_token_secret"] = "XYXYXYXY"
    self.assertEqual(result, None)

    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    result = access_token.RestrictedAccessToken_getUserValue()

    self.assertEqual(result, person)
    self.assertEqual(access_token.getValidationState(), 'validated')

  def test_RestrictedAccessToken_getUserValue_no_agent(self):
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        None,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url
    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    result = access_token.RestrictedAccessToken_getUserValue()
    self.assertEqual(result, None)

  def test_RestrictedAccessToken_getUserValue_wrong_values(self):
    person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    self.tic()
    result = access_token.RestrictedAccessToken_getUserValue()
    self.assertEqual(result, None)

    access_token.validate()
    self.tic()

    self.portal.REQUEST["REQUEST_METHOD"] = "POST"
    self.portal.REQUEST["ACTUAL_URL"] = access_url
    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    result = access_token.RestrictedAccessToken_getUserValue()
    self.assertEqual(result, None)

    self.portal.REQUEST["ACTUAL_URL"] = "http://exemple.com/foo.bar"

    result = access_token.RestrictedAccessToken_getUserValue()
    self.assertEqual(result, None)

    access_token.invalidate()
    self.tic()

    result = access_token.RestrictedAccessToken_getUserValue()
    self.assertEqual(result, None)


  def test_OneTimeRestrictedAccessToken_getUserValue(self):
    person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createOneTimeRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url

    result = access_token.OneTimeRestrictedAccessToken_getUserValue()

    self.assertEqual(result, person)
    self.assertEqual(access_token.getValidationState(), 'invalidated')

  def test_OneTimeRestrictedAccessToken_getUserValue_wrong_values(self):
    person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "POST"
    access_token = self._createOneTimeRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    self.tic()
    result = access_token.OneTimeRestrictedAccessToken_getUserValue()
    self.assertEqual(result, None)

    access_token.validate()
    self.tic()

    self.portal.REQUEST["REQUEST_METHOD"] = "GET"
    self.portal.REQUEST["ACTUAL_URL"] = access_url

    result = access_token.OneTimeRestrictedAccessToken_getUserValue()
    self.assertEqual(result, None)

    self.portal.REQUEST["ACTUAL_URL"] = "http://exemple.com/foo.bar"

    result = access_token.OneTimeRestrictedAccessToken_getUserValue()
    self.assertEqual(result, None)


class TestERP5AccessTokenAlarm(AccessTokenTestCase):

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