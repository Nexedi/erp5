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

def sha1(s):
  return hashlib.sha1(s).hexdigest()

class TestERP5PayzenSecurePaymentMixin(ERP5TypeTestCase):
  """
  An ERP5 Payzen Secure Payment test case
  """

  def getTitle(self):
    return "ERP5 Payzen Secure Payment"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ('erp5_base'
          , 'erp5_secure_payment'
          , 'erp5_payzen_secure_payment')

  def afterSetUp(self):
    self.portal = self.getPortalObject()
    if not self.portal.hasObject('portal_secure_payments'):
      self.portal.manage_addProduct['ERP5SecurePayment'].manage_addTool(
        'ERP5 Secure Payment Tool', None)
      self.stepTic()
    self.service = self.portal.portal_secure_payments.newContent(
      portal_type='Payzen Service')
    self.stepTic()

class TestERP5PayzenSecurePayment(TestERP5PayzenSecurePaymentMixin):
  def afterSetUp(self):
    super(TestERP5PayzenSecurePayment, self).afterSetUp()
    self.service_password = '0123456789012345'
    self.service.edit(service_password=self.service_password)
    self.stepTic()

  def test_getSignature_dict_simple(self):
    self.assertEqual(
      self.service._getSignature({'key': 'value'}, ['key']),
      sha1('value+' + self.service_password)
    )

  def test_getSignature_dict_key_sort(self):
    self.assertEqual(
      self.service._getSignature({'key': 'value', 'key1': 'value1'}, ['key',
        'key1']),
      sha1('value+value1+' + self.service_password)
    )
    self.assertEqual(
      self.service._getSignature({'key': 'value', 'key1': 'value1'}, ['key1',
        'key']),
      sha1('value1+value+' + self.service_password)
    )

  def test_getSignature_dict_date_as_DateTime(self):
    now = DateTime.DateTime()
    d = {'key': now}
    self.assertEqual(
      self.service._getSignature(d, ['key']),
      sha1(now.strftime('%Y%m%d') + '+' + self.service_password)
    )
    # dict was updated
    self.assertEqual(d['key'], now.strftime('%Y-%m-%dT%H:%M:%S'))

  def test_getSignature_dict_date_as_DateTime_output_date(self):
    now = DateTime.DateTime()
    d = {'key': now}
    self.assertEqual(
      self.service._getSignature(d, ['key'], output_date_format='%Y'),
      sha1(now.strftime('%Y%m%d') + '+' + self.service_password)
    )
    # dict was updated with passed format
    self.assertEqual(d['key'], now.strftime('%Y'))

  def test_getSignature_dict_date_as_DateTime_signature_format(self):
    now = DateTime.DateTime()
    d = {'key': now}
    self.assertEqual(
      self.service._getSignature(d, ['key'], signature_date_format='%Y'),
      sha1(now.strftime('%Y') + '+' + self.service_password)
    )
    # dict was updated with passed format
    self.assertEqual(d['key'], now.strftime('%Y-%m-%dT%H:%M:%S'))

  def test_getSignature_dict_date_as_string(self):
    now = DateTime.DateTime()
    d = {'keyDaTe': now.strftime('%Y-%m-%d %H:%M:%S')}
    self.assertEqual(
      self.service._getSignature(d, ['keyDaTe']),
      sha1(now.strftime('%Y%m%d') + '+' + self.service_password)
    )
    # dict was updated with passed format
    self.assertEqual(d['keyDaTe'], now.strftime('%Y-%m-%dT%H:%M:%S'))
