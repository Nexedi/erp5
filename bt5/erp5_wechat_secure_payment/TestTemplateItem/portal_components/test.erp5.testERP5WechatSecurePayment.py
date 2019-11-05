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
import mock

def sha1(s):
  return hashlib.sha1(s).hexdigest()

class TestERP5WechatSecurePaymentMixin(ERP5TypeTestCase):
  """
  An ERP5 Wechat Secure Payment test case
  """

  def getTitle(self):
    return "ERP5 Wechat Secure Payment"

  def afterSetUp(self):
    self.portal = self.getPortalObject()
    if not self.portal.hasObject('portal_secure_payments'):
      self.portal.manage_addProduct['ERP5SecurePayment'].manage_addTool(
        'ERP5 Secure Payment Tool', None)
      self.tic()
    self.service = self.portal.portal_secure_payments.newContent(
      portal_type='Wechat Service')
    self.tic()

def getMessageList(o):
  return [str(q.getMessage()) for q in o.checkConsistency()]

class TestERP5WechatSecurePaymenConstraint(TestERP5WechatSecurePaymentMixin):
  def _test(self, message, prop, value='12345'):
    self.assertTrue(message in getMessageList(self.service))
    self.service.edit(**{prop: value})
    self.assertFalse(message in getMessageList(self.service))

  def test_link_url_string(self):
    self._test('Wechat URL has to be set.', 'link_url_string')

  def test_api_key(self):
    self._test('api_key has to be set.', 'service_api_key')

  def test_appid(self):
    self._test('APP ID has to be set.', 'service_appid')

  def test_mch_id(self):
    self._test('mch_id has to be set.', 'service_mch_id')

  def test_wechat_mode(self):
    message = 'Wechat mode has to be SANDBOX or PRODUCTION.'
    self.assertRaises(AssertionError, self._test,
      message, 'wechat_mode')
    self._test(message, 'wechat_mode', 'SANDBOX')
    self.service.edit(wechat_mode='')
    self._test(message, 'wechat_mode', 'PRODUCTION')

class TestERP5WechatSecurePayment(TestERP5WechatSecurePaymentMixin):
  def afterSetUp(self):
    super(TestERP5WechatSecurePayment, self).afterSetUp()
    self.service_password = '0123456789012345'
    self.service.edit(service_password=self.service_password)
    self.tic()

  def test_calculateSign_dict_simple(self):
    self.assertEqual(
      self.service.calculateSign({'key': 'value'}, 'mysecretkey'),
      hashlib.md5("key=value&key=mysecretkey").hexdigest().upper()
    )

  def test_calculateSign_dict_key_sort(self):
    self.assertEqual(
      self.service.calculateSign({'key0': 'value0', 'key1': 'value1'}, 'mysecretkey'),
      hashlib.md5("key0=value0&key1=value1&key=mysecretkey").hexdigest().upper()
    )
    self.assertEqual(
      self.service.calculateSign({'key1': 'value1', 'key0': 'value0'}, 'mysecretkey'),
      hashlib.md5("key0=value0&key1=value1&key=mysecretkey").hexdigest().upper()
    )

  def test_navigate(self):
    self.service.edit(
      link_url_string='http://wechat/',
      service_mch_id='0123456789',
      service_appid='my_appid',
      service_api_key='0000DEADBEEFCAFEDECA',
      wechat_mode='PRODUCTION',
    )
    with mock.patch.object(
      self.service, 'callWechatApi', return_value={"result_code": 'SUCCESS', "code_url": 'http://somecodeurl'}):
      result = self.service.navigate({"out_trade_no": '1234', "total_fee": '5000'})
      self.assertEqual(result, "https://softinst109876.host.vifib.net/erp5/#wechat_payment?trade_no=1234&price=5000&payment_url=http://somecodeurl")


