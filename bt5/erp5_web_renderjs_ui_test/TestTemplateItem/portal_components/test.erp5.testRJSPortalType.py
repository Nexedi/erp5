##############################################################################
#
# Copyright (c) 2018 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestRenderJSPortalType(ERP5TypeTestCase):
  """Test Web Script & Web Style portal types added by Render JS.
  """

  def afterSetUp(self):
    self.web_site = self.portal.web_site_module.newContent(
      portal_type='Web Site',
      skin_selection_name='RJS',
    )
    self.web_site.publish()

  def test_web_style(self):
    web_style = self.portal.web_page_module.newContent(
      portal_type='Web Style',
      reference='test_web_style.css'
    )
    web_style.setTextContent(b'/* cl\xc3\xa0sse */ .classe { background: red }'.decode('utf-8'))
    web_style.publish()
    self.tic()
    self.assertEqual('text/css', web_style.getContentType())

    # test HTTP response
    response = self.publish(
      '%s/%s' % (self.web_site.getPath(), web_style.getReference())
    )
    self.assertEqual(
      b'/* cl\xc3\xa0sse */ .classe { background: red }',
      response.getBody()
    )
    self.assertEqual(
      'text/css; charset=utf-8',
      response.getHeader('content-type')
    )

  def test_web_script(self):
    web_script = self.portal.web_page_module.newContent(
      portal_type='Web Script',
      reference='test_web_script.js'
    )
    web_script.setTextContent(b'alert("h\xc3\xa9h\xc3\xa9")'.decode('utf-8'))
    web_script.publish()
    self.tic()
    self.assertEqual('application/javascript', web_script.getContentType())

    # test HTTP response
    response = self.publish(
      '%s/%s' % (self.web_site.getPath(), web_script.getReference())
    )
    self.assertEqual(
      b'alert("h\xc3\xa9h\xc3\xa9")',
      response.getBody()
    )
    self.assertEqual(
      'application/javascript; charset=utf-8',
      response.getHeader('content-type')
    )

