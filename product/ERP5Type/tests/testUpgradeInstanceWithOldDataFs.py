##############################################################################
#
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
#          Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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
import StringIO
import urllib
from zope.globalrequest import setRequest #  pylint: disable=no-name-in-module, import-error
from Acquisition import aq_base

# XXX Copy/pasted from erp5_hal_json_style tests
def do_fake_request(request_method, headers=None, data=()):
  __version__ = "0.1"
  if (headers is None):
    headers = {}
  env={}
  env['SERVER_NAME']='bobo.server'
  env['SERVER_PORT']='80'
  env['REQUEST_METHOD']=request_method
  env['REMOTE_ADDR']='204.183.226.81 '
  env['REMOTE_HOST']='bobo.remote.host'
  env['HTTP_USER_AGENT']='Bobo/%s' % __version__
  env['HTTP_HOST']='127.0.0.1'
  env['SERVER_SOFTWARE']='Bobo/%s' % __version__
  env['SERVER_PROTOCOL']='HTTP/1.0 '
  env['HTTP_ACCEPT']='image/gif, image/x-xbitmap, image/jpeg, */* '
  env['SERVER_HOSTNAME']='bobo.server.host'
  env['GATEWAY_INTERFACE']='CGI/1.1 '
  env['SCRIPT_NAME']='Main'
  env.update(headers)
  body_stream = StringIO.StringIO()

  # for some mysterious reason QUERY_STRING does not get parsed into data fields
  if data and request_method.upper() == 'GET':
    # see: GET http://www.cgi101.com/book/ch3/text.html
    env['QUERY_STRING'] = '&'.join(
      '{}={}'.format(urllib.quote_plus(key), urllib.quote(value))
      for key, value in data
    )

  if data and request_method.upper() == 'POST':
    # see: POST request body https://tools.ietf.org/html/rfc1866#section-8.2.1
    env['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
    for key, value in data:
      body_stream.write('{}={!s}&'.format(
        urllib.quote_plus(key), urllib.quote(value)))

  request = HTTPRequest(body_stream, env, HTTPResponse())
  if data and request_method.upper() == 'POST':
    for key, value in data:
      request.form[key] = value

  return request

def replace_request(new_request, context):
  base_chain = [aq_base(x) for x in context.aq_chain]
  # Grab existig request (last chain item) and create a copy.
  request_container = base_chain.pop()
  # request = request_container.REQUEST

  setRequest(new_request)

  new_request_container = request_container.__class__(REQUEST=new_request)
  # Recreate acquisition chain.
  my_self = new_request_container
  base_chain.reverse()
  for item in base_chain:
    my_self = item.__of__(my_self)
  return my_self

class TestUpgradeInstanceWithOldDataFs(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy',
            'erp5_full_text_mroonga_catalog',
            'erp5_base',
            'erp5_workflow',
            'erp5_simulation',
            'erp5_accounting',
            'erp5_configurator',
            'erp5_pdm',
            'erp5_trade',
            'erp5_accounting',
            'erp5_configurator_standard_trade_template',
            'erp5_upgrader')

  def testUpgrade(self):
    if not self.portal.portal_templates.getRepositoryList():
      self.setupAutomaticBusinessTemplateRepository(
        searchable_business_template_list=["erp5_core", "erp5_base"])

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

    self.assertNotEquals([x.detail for x in alarm.getLastActiveProcess().getResultList()], [])

    # Solve divergencies, like called from the form_dialog
    fake_request = do_fake_request("POST", data=(
      ('dialog_method', 'Alarm_solve'),
      ('dialog_id', 'Alarm_viewSolveDialog'),
      ('form_id', 'Alarm_view'),
      ('selection_name', 'foo_selection')
    ))
    fake_portal = replace_request(fake_request, self.portal)

    result = fake_portal.portal_alarms.promise_check_upgrade.Base_callDialogMethod(
      dialog_method='Alarm_solve',
      dialog_id='Alarm_viewSolveDialog',
      form_id='Alarm_view',
    )
    self.assertEqual(fake_request.RESPONSE.status, 302)

    # alarm.solve()
    self.tic()

    self.assertEquals([x.detail for x in alarm.getLastActiveProcess().getResultList()], [])

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
    self.assertEquals(
      error_list, [],
      msg="The following Portal Type classes could not be loaded (see zLOG.log): %r" % error_list)
