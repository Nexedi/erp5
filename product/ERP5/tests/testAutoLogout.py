# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004, 2005, 2006 Nexedi SARL and Contributors.
# All Rights Reserved.
#          Ivan Tyagov <ivan@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from functools import partial
from StringIO import StringIO
import unittest
import urllib
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime

class TestAuoLogout(ERP5TypeTestCase):
  """
  Test for erp5_auto_logout business template.
  """
  manager_username = 'zope'
  manager_password = 'zope'

  credential = '%s:%s' % (manager_username, manager_password)
  def getTitle(self):
    return "TestAuthenticationPolicy"

  def getBusinessTemplateList(self):
    """
    Return the list of required business templates.
    """
    return ('erp5_core_proxy_field_legacy',
            'erp5_base',)

  def afterSetUp(self):
    portal = self.getPortal()

    uf = portal.acl_users
    uf._doAddUser(self.manager_username, self.manager_password, ['Manager'], [])
    self.loginByUserName(self.manager_username)

    # setup short auto-logout period
    portal.portal_preferences.default_site_preference.setPreferredMaxUserInactivityDuration(5)
    portal.portal_preferences.default_site_preference.enable()
    self.tic()

  def test_01_AutoLogout(self):
    """
      Test auto logout feature of ERP5.
    """
    portal = self.getPortal()
    request = self.app.REQUEST

    stdin = urllib.urlencode({
      '__ac_name': self.manager_username,
      '__ac_password': self.manager_password,
    })
    now = DateTime()
    publish = partial(
      self.publish,
      portal.absolute_url_path() + '/view',
      request_method='POST',
    )
    response = publish(stdin=StringIO(stdin))
    self.assertIn('Welcome to ERP5', response.getBody())

    # check '__ac' cookie has set an expire timeout
    ac_cookie = response.getCookie('__ac')
    self.assertNotEqual(ac_cookie, None)
    cookie_expire = ac_cookie['expires']
    one_second = 1/24.0/60.0/60.0
    self.assertGreater((now + (5 + 1) * one_second), DateTime(cookie_expire)) # give 1s tollerance

    # if we disable auto-logout then cookie will expire at end of session
    portal.portal_preferences.default_site_preference.disable()
    self.tic()
    portal.portal_caches.clearAllCache()

    response = publish(stdin=StringIO(stdin))
    self.assertIn('Welcome to ERP5', response.getBody())
    ac_cookie = response.getCookie('__ac')
    self.assertNotEqual(ac_cookie, None)
    self.assertEqual(ac_cookie.get('expires', None), None)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAuoLogout))
  return suite
