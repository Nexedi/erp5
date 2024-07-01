# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.runUnitTest import log_directory
from Products.ERP5Type.tests.utils import createZODBPythonScript
import os
import requests


def get_Z2_log_last_line():
  z2_log_path = os.path.join(log_directory, 'Z2.log')
  f = open(z2_log_path, 'r')
  try:
    f.seek(-256, os.SEEK_END) # Assumes last line is not longer than 256 chars (it should be about 130)
  except IOError: # too short
    pass
  last_line = f.readlines()[-1]
  f.close()
  return last_line


class TestXForwardedFor(ERP5TypeTestCase):
  def test_request_with_x_forwarded_for(self):
    script_container = self.portal.portal_skins.custom
    script_id = 'ERP5Site_getClientAddr'
    createZODBPythonScript(script_container, script_id, '', 'return context.REQUEST.getClientAddr()')
    self.commit()
    import ZPublisher.HTTPRequest

    # test without configuration
    ZPublisher.HTTPRequest.trusted_proxies = []
    response = requests.get(
      '%s/%s' % (self.portal.absolute_url(), script_id),
      headers={'X-Forwarded-For': '1.2.3.4'},
      timeout=5,
    )
    self.assertNotEqual(response.text, '1.2.3.4')
    last_line = get_Z2_log_last_line()
    self.assertFalse(last_line.startswith('1.2.3.4 - '), last_line)
    response = requests.get(
      '%s/%s' % (self.portal.absolute_url(), script_id),
      headers={'X-Forwarded-For': '1.2.3.4, 5.6.7.8'},
      timeout=5,
    )
    self.assertNotEqual(response.text, '1.2.3.4')
    self.assertNotEqual(response.text, '5.6.7.8')
    last_line = get_Z2_log_last_line()
    self.assertFalse(last_line.startswith('1.2.3.4 - '), last_line)
    self.assertFalse(last_line.startswith('5.6.7.8 - '), last_line)
    response = requests.get(
      '%s/%s' % (self.portal.absolute_url(), script_id),
      timeout=5,
    )
    self.assertNotEqual(response.text, '1.2.3.4')
    last_line = get_Z2_log_last_line()
    self.assertFalse(last_line.startswith('1.2.3.4 - '), last_line)

    # test with configuration
    ZPublisher.HTTPRequest.trusted_proxies = ('0.0.0.0',)
    response = requests.get(
      '%s/%s' % (self.portal.absolute_url(), script_id),
      headers={'X-Forwarded-For': '1.2.3.4'},
      timeout=5,
    )
    self.assertEqual(response.text, '1.2.3.4')
    last_line = get_Z2_log_last_line()
    self.assertTrue(last_line.startswith('1.2.3.4 - '), last_line)
    response = requests.get(
      '%s/%s' % (self.portal.absolute_url(), script_id),
      headers={'X-Forwarded-For': '1.2.3.4, 5.6.7.8'},
      timeout=5,
    )
    self.assertEqual(response.text, '1.2.3.4')
    last_line = get_Z2_log_last_line()
    self.assertTrue(last_line.startswith('1.2.3.4 - '), last_line)
    response = requests.get(
      '%s/%s' % (self.portal.absolute_url(), script_id),
      timeout=5,
    )
    self.assertNotEqual(response.text, '1.2.3.4')
    last_line = get_Z2_log_last_line()
    self.assertFalse(last_line.startswith('1.2.3.4 - '), last_line)
