##############################################################################
#
# Copyright (c) 2002-2012 Nexedi SA and Contributors. All Rights Reserved.
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

import random
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase, get_request


def getMessageList(o):
  return [str(q.getMessage()) for q in o.checkConsistency()]

class TestERP5PaypalSecurePaymentMixin(ERP5TypeTestCase):
  """
  An ERP5 Paypal Secure Payment test case
  """

  def getTitle(self):
    return "ERP5 Paypal Secure Payment"

  def afterSetUp(self):
    self.portal = self.getPortalObject()
    if not self.portal.hasObject('portal_secure_payments'):
      self.portal.manage_addProduct['ERP5SecurePayment'].manage_addTool(
        'ERP5 Secure Payment Tool', None)
      self.tic()
    self.service = self.portal.portal_secure_payments.newContent(
      portal_type='Paypal Service',
      reference="default")
    self.tic()


class TestERP5PaypalSecurePaymenConstraint(TestERP5PaypalSecurePaymentMixin):

  def _test(self, message, prop, value='12345'):
    self.assertIn(message, getMessageList(self.service))
    self.service.edit(**{prop: value})
    self.assertNotIn(message, getMessageList(self.service))

  def test_link_url_string(self):
    self._test('Paypal URL have to be set', 'link_url_string')


class TestERP5PaypalSecurePayment(TestERP5PaypalSecurePaymentMixin):

  def test_navigate(self):
    self.service.edit(
      link_url_string='http://paypal/',
      service_username="business@sample.com"
    )
    pt_id = str(random.random())
    page_template_text = """<tal:block tal:repeat="value here/field_list">key=<tal:block tal:replace="python: value[0]"/> value=<tal:block tal:replace="python: value[1]"/>
</tal:block>link=<tal:block tal:replace='here/link_url_string'/>
business=<tal:block tal:replace='here/service_username'/>
    """
    self.portal.portal_skins.custom.manage_addProduct['PageTemplates']\
                .manage_addPageTemplate(id=pt_id, text=page_template_text)
    # flush skin cache
    self.portal.changeSkin(None)
    paypal_dict = {
        "return" : "http://ipn/"
    }
    try:
      result = self.service.navigate(page_template=pt_id, paypal_dict=paypal_dict)
      self.assertEqual(result, """key=return value=http://ipn/
link=http://paypal/
business=business@sample.com""")
    finally:
      self.portal.portal_skins.custom.manage_delObjects([pt_id])
      # flush skin cache
      self.portal.changeSkin(None)

  def test_reportPaymentStatus(self):
    script_id = "Base_paymentResponse"
    custom_skin = self.portal.portal_skins.custom
    custom_skin.manage_addProduct['PythonScripts']\
               .manage_addPythonScript(id=script_id)
    script = custom_skin[script_id]
    script.ZPythonScript_edit('**kw', "return 'VERIFIED'")
    self.tic()
    script_absolute_url = script.absolute_url()
    self.service.edit(link_url_string=script_absolute_url)
    response = self.service.reportPaymentStatus(get_request())
    self.assertTrue(response)
