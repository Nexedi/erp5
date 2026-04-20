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

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestAuoLogout(ERP5TypeTestCase):
  """
  Test for erp5_auto_logout business template.
  """
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

    # setup short auto-logout period
    portal.portal_preferences.default_site_preference.setPreferredMaxUserInactivityDuration(5)
    portal.portal_preferences.default_site_preference.enable()
    self.tic()

  def test_01_AutoLogout(self):
    """
      Test auto logout feature of ERP5.
    """
    portal = self.getPortal()
    response = self.publish(
      portal.absolute_url_path() + '/view',
      basic='%s:%s' % (self.manager_username, self.manager_password),
    )
    self.assertIn(b'Welcome to ERP5', response.getBody())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestAuoLogout))
  return suite
