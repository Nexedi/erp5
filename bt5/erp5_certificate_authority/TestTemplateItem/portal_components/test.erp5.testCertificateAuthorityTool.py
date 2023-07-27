# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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

import os
import random
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from erp5.component.tool.CertificateAuthorityTool import CertificateAuthorityBusy
#from AccessControl import Unauthorized

class TestCertificateAuthorityTool(ERP5TypeTestCase):

  def afterSetUp(self):
    if "TEST_CA_PATH" in os.environ:
      self.portal.portal_certificate_authority.certificate_authority_path = \
          os.environ['TEST_CA_PATH']

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_certificate_authority')

  def test_lock_unlock(self):
    certificate_authority_tool = self.portal.portal_certificate_authority
    certificate_authority_tool._checkCertificateAuthority()
    try:
      certificate_authority_tool._lockCertificateAuthority()
      certificate_authority_tool._unlockCertificateAuthority()
      certificate_authority_tool._lockCertificateAuthority()
      self.assertRaises(CertificateAuthorityBusy, certificate_authority_tool._lockCertificateAuthority)
    finally:
      certificate_authority_tool._unlockCertificateAuthority()

  def test_getNewCertificate(self):
    certificate_authority_tool = self.portal.portal_certificate_authority

    common_name = str(random.random())
    certificate_dict = certificate_authority_tool.getNewCertificate(common_name)
    self.assertEqual(common_name, certificate_dict['common_name'])
    self.assertNotEqual(None, certificate_dict['id'])
    self.assertNotEqual(None, certificate_dict['key'])
    self.assertNotEqual(None, certificate_dict['certificate'])

    self.assertIn('CN=%s' % common_name, certificate_dict['certificate'])

    # Check serial
    serial = certificate_authority_tool._getValidSerial(common_name)
    self.assertEqual(serial, [certificate_dict['id'].upper()])

    self.assertRaises(ValueError,
      certificate_authority_tool.getNewCertificate, common_name)

  def test_getNewCertificate_locked(self):
    certificate_authority_tool = self.portal.portal_certificate_authority
    certificate_authority_tool._checkCertificateAuthority()
    try:
      certificate_authority_tool._lockCertificateAuthority()

      common_name = str(random.random())
      self.assertRaises(CertificateAuthorityBusy,
        certificate_authority_tool.getNewCertificate, common_name)
      certificate_authority_tool._unlockCertificateAuthority()
      certificate_dict = certificate_authority_tool.getNewCertificate(common_name)
      self.assertEqual(common_name, certificate_dict['common_name'])
    finally:
      certificate_authority_tool._unlockCertificateAuthority()

  def test_revokeCertificate_raise(self):
    certificate_authority_tool = self.portal.portal_certificate_authority
    common_name = str(random.random())
    self.assertRaises(ValueError,
        certificate_authority_tool.revokeCertificate, common_name)

  def test_revokeCertificate(self):
    certificate_authority_tool = self.portal.portal_certificate_authority

    common_name = str(random.random())
    certificate_dict = certificate_authority_tool.getNewCertificate(common_name)
    self.assertEqual(common_name, certificate_dict['common_name'])
    self.assertNotEqual(None, certificate_dict['id'])
    self.assertIn('CN=%s' % common_name, certificate_dict['certificate'])

    # Check serial
    serial_list = certificate_authority_tool._getValidSerial(common_name)
    self.assertEqual(len(serial_list), 1)
    self.assertEqual(serial_list[0], certificate_dict['id'].upper())

    revoke_dict = certificate_authority_tool.revokeCertificate(serial_list[0])
    self.assertNotEqual(revoke_dict['crl'], None)

    # No valid certificate anymore
    self.assertRaises(ValueError, certificate_authority_tool._getValidSerial, common_name)

  def test_revokeCertificateByName(self):
    certificate_authority_tool = self.portal.portal_certificate_authority

    common_name = str(random.random())
    certificate_dict = certificate_authority_tool.getNewCertificate(common_name)
    self.assertEqual(common_name, certificate_dict['common_name'])
    self.assertNotEqual(None, certificate_dict['id'])
    self.assertIn('CN=%s' % common_name, certificate_dict['certificate'])

    serial_list = certificate_authority_tool._getValidSerial(common_name)
    self.assertEqual(len(serial_list), 1)
    self.assertEqual(serial_list[0], certificate_dict['id'].upper())

    response = certificate_authority_tool.revokeCertificateByCommonName(common_name)
    self.assertEqual(None, response)

    # No valid certificate anymore
    self.assertRaises(ValueError, certificate_authority_tool._getValidSerial, common_name)

  def test_revokeCertificate_locked(self):
    certificate_authority_tool = self.portal.portal_certificate_authority
    common_name = str(random.random())
    certificate_dict = certificate_authority_tool.getNewCertificate(common_name)
    self.assertEqual(common_name, certificate_dict['common_name'])

    try:
      certificate_authority_tool._lockCertificateAuthority()

      self.assertRaises(CertificateAuthorityBusy,
        certificate_authority_tool.revokeCertificateByCommonName, common_name)
      certificate_authority_tool._unlockCertificateAuthority()
      response = certificate_authority_tool.revokeCertificateByCommonName(common_name)
      self.assertEqual(None, response)
      # No valid certificate anymore
      self.assertRaises(ValueError, certificate_authority_tool._getValidSerial, common_name)
    finally:
      certificate_authority_tool._unlockCertificateAuthority()

