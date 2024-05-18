##############################################################################
#
# Copyright (c) 2002-2011 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import hashlib
import DateTime
import random

def sha1(s):
  return hashlib.sha1(s).hexdigest()

class TestERP5PayzenSecurePaymentMixin(ERP5TypeTestCase):
  """
  An ERP5 Payzen Secure Payment test case
  """

  def getTitle(self):
    return "ERP5 Payzen Secure Payment"

  def afterSetUp(self):
    self.portal = self.getPortalObject()
    if not self.portal.hasObject('portal_secure_payments'):
      self.portal.manage_addProduct['ERP5SecurePayment'].manage_addTool(
        'ERP5 Secure Payment Tool', None)
      self.tic()
    self.service = self.portal.portal_secure_payments.newContent(
      portal_type='Payzen Service')
    self.tic()

def getMessageList(o):
  return [str(q.getMessage()) for q in o.checkConsistency()]

class TestERP5PayzenSecurePaymenConstraint(TestERP5PayzenSecurePaymentMixin):
  def _test(self, message, prop, value='12345'):
    self.assertIn(message, getMessageList(self.service))
    self.service.edit(**{prop: value})
    self.assertNotIn(message, getMessageList(self.service))

  def test_service_username(self):
    self._test('service_username have to be set', 'service_username')

  def test_service_password(self):
    self._test('service_password has to be set.', 'service_password')

  def test_service_api_key(self):
    self._test('service_api_key has to be set.', 'service_api_key')

  def test_link_url_string(self):
    self._test('Payzen URL have to be set', 'link_url_string')

  def test_payzen_vads_version(self):
    message = 'Payzen vads_version have to be V2'
    self.assertRaises(AssertionError, self._test,
      message, 'payzen_vads_version')
    self._test(message, 'payzen_vads_version', 'V2')

  def test_payzen_vads_page_action(self):
    message = 'Payzen vads_page_action have to be one of REGISTER, '\
      'REGISTER_UPDATE, REGISTER_PAY, REGISTER_SUBSCRIBE, '\
      'REGISTER_PAY_SUBSCRIBE, PAYMENT'
    self.assertRaises(AssertionError, self._test,
      message, 'payzen_vads_page_action')
    for v in ['REGISTER', 'REGISTER_UPDATE', 'REGISTER_PAY',
        'REGISTER_SUBSCRIBE', 'REGISTER_PAY_SUBSCRIBE', 'PAYMENT']:
      self._test(message, 'payzen_vads_page_action', v)
      self.service.edit(payzen_vads_page_action='')

  def test_payzen_vads_action_mode(self):
    message = 'Payzen vads_action_mode have to be SILENT or INTERACTIVE'
    self.assertRaises(AssertionError, self._test,
      message, 'payzen_vads_action_mode')
    self._test(message, 'payzen_vads_action_mode', 'INTERACTIVE')
    self.service.edit(payzen_vads_action_mode='')
    self._test(message, 'payzen_vads_action_mode', 'SILENT')

  def test_payzen_vads_ctx_mode(self):
    message = 'Payzen vads_ctx_mode have to be TEST or PRODUCTION'
    self.assertRaises(AssertionError, self._test,
      message, 'payzen_vads_ctx_mode')
    self._test(message, 'payzen_vads_ctx_mode', 'TEST')
    self.service.edit(payzen_vads_ctx_mode='')
    self._test(message, 'payzen_vads_ctx_mode', 'PRODUCTION')

class TestERP5PayzenSecurePayment(TestERP5PayzenSecurePaymentMixin):
  def afterSetUp(self):
    super(TestERP5PayzenSecurePayment, self).afterSetUp()
    self.service_password = '0123456789012345'
    self.service.edit(service_password=self.service_password)
    self.tic()

  def test_getSignature_dict_simple(self):
    self.assertEqual(
      self.service._getSignature({'key': 'value'}, ['key']),
      sha1(('value+' + self.service_password).encode())
    )

  def test_getSignature_dict_key_sort(self):
    self.assertEqual(
      self.service._getSignature({'key': 'value', 'key1': 'value1'}, ['key',
        'key1']),
      sha1(('value+value1+' + self.service_password).encode())
    )
    self.assertEqual(
      self.service._getSignature({'key': 'value', 'key1': 'value1'}, ['key1',
        'key']),
      sha1(('value1+value+' + self.service_password).encode())
    )

  def test_getSignature_dict_date_as_datetime(self):
    now = DateTime.DateTime().asdatetime()
    d = {'key': now}
    self.assertEqual(
      self.service._getSignature(d, ['key']),
      sha1((now.strftime('%Y%m%d') + '+' + self.service_password).encode())
    )
    # dict was updated
    self.assertEqual(d['key'], now)

  def test_navigate(self):
    self.service.edit(
      link_url_string='http://payzen/',
      payzen_vads_action_mode='INTERACTIVE',
      payzen_vads_ctx_mode='TEST',
      payzen_vads_page_action='REGISTER',
      payzen_vads_version='V2',
      service_username='0123456',
      service_api_key='ABC123'
    )
    pt_id = str(random.random())
    self.portal.portal_skins.custom.manage_addProduct['PageTemplates']\
                .manage_addPageTemplate(id = pt_id, text='''<tal:block tal:repeat="value here/field_list">key=<tal:block tal:replace="python: value[0]"/> value=<tal:block tal:replace="python: value[1]"/>
</tal:block>''')
    # flush skin cache
    self.portal.changeSkin(None)
    try:
      result = self.service.navigate(pt_id, {"key": 'value'})
      signature = sha1(('value+INTERACTIVE+ERP5+TEST+REGISTER+SINGLE+0123456+V2+'
        + self.service_password).encode())
      self.assertEqual(result, """key=key value=value
key=signature value=%s
key=vads_action_mode value=INTERACTIVE
key=vads_contrib value=ERP5
key=vads_ctx_mode value=TEST
key=vads_page_action value=REGISTER
key=vads_payment_config value=SINGLE
key=vads_site_id value=0123456
key=vads_version value=V2
""" % signature)
    finally:
      self.portal.portal_skins.custom.manage_delObjects([pt_id])
      # flush skin cache
      self.portal.changeSkin(None)
