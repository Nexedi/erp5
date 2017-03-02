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
import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl import Unauthorized

class TestCertificateAuthority(ERP5TypeTestCase):

  def getTitle(self):
    return "Test Certificate Authority"

  def afterSetUp(self):
    self.portal.portal_certificate_authority.certificate_authority_path = \
        os.environ['TEST_CA_PATH']

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_certificate_authority')

  def _createPerson(self):
    login = str(random.random())
    person = self.portal.person_module.newContent(portal_type='Person',
      reference=login, password=login)
    person.newContent(portal_type='Assignment').open()
    person.newContent(portal_type='ERP5 Login', reference=login).validate()
    self.tic()
    return person.getUserId(), login

  def test_person_request_certificate(self):
    user_id, login = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    certificate = person.getCertificate()
    self.assertTrue('CN=%s' % user_id in certificate['certificate'])

  def test_person_revoke_certificate(self):
    user_id, login = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    self.assertRaises(ValueError, person.revokeCertificate)

  def test_person_request_revoke_certificate(self):
    user_id, login = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    certificate = person.getCertificate()
    self.assertTrue('CN=%s' % user_id in certificate['certificate'])
    person.revokeCertificate()

  def test_person_request_certificate_twice(self):
    user_id, login = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    certificate = person.getCertificate()
    self.assertTrue('CN=%s' % user_id in certificate['certificate'])
    self.assertRaises(ValueError, person.getCertificate)

  def test_person_request_certificate_for_another(self):
    user_id, login = self._createPerson()
    user_id2, login2 = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    self.loginByUserName(login2)
    self.assertRaises(Unauthorized, person.getCertificate)

  def test_person_revoke_certificate_for_another(self):
    user_id, login = self._createPerson()
    user_id2, login2 = self._createPerson()
    self.loginByUserName(login)
    person = self.portal.portal_membership.getAuthenticatedMember().getUserValue()
    certificate = person.getCertificate()
    self.assertTrue('CN=%s' % user_id in certificate['certificate'])
    self.loginByUserName(login2)
    self.assertRaises(Unauthorized, person.revokeCertificate)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCertificateAuthority))
  return suite
