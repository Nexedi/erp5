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


class TestRenderJSTrailingSlashRedirection(ERP5TypeTestCase):
  """Test that RJS web site renders correctly when missing the trailing /
  """

  def afterSetUp(self):
    self.web_site = self.portal.web_site_module.renderjs_runner

  def test_no_language_missing_trailing_slash(self):
    # test HTTP response
    response = self.publish(
      '%s?foo=bar' % (self.web_site.getPath(), )
    )
    expected_redirection_url = 'http://%s%s/%s/%s/?foo=bar' % (
      self.portal.REQUEST['SERVER_NAME'],
      ":%s" % self.portal.REQUEST['SERVER_PORT'] if (self.portal.REQUEST['SERVER_PORT'] != '80') else "",
      self.portal.getId(),
      self.web_site.getRelativeUrl()
    )
    self.assertEqual(
      'Redirecting to %s' % expected_redirection_url,
      response.getBody()
    )
    self.assertEqual(
      'text/plain; charset=utf-8',
      response.getHeader('content-type')
    )
    self.assertEqual(
      expected_redirection_url,
      response.getHeader('location')
    )
    self.assertEqual(
      302,
      response.getStatus()
    )
