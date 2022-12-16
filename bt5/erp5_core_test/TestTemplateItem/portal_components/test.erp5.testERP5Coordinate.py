##############################################################################
#
# Copyright (c) 2005-2011 Nexedi SARL and Contributors. All Rights Reserved.
#                    Kevin Deldycke <kevin_AT_nexedi_DOT_com>
#                    Nicolas Delaby <nicolas@nexedi.com>
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


import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestERP5Coordinate(ERP5TypeTestCase):
  """Check Coordinate API
  """
  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "ERP5 Coordinate"

  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_core_proxy_field_legacy',
            'erp5_full_text_mroonga_catalog',
            'erp5_base',)

  def afterSetUp(self):
    ERP5TypeTestCase.afterSetUp(self)
    self.default_site_preference = self.portal.portal_preferences.default_site_preference
    if self.default_site_preference.getPreferenceState() != 'global':
      self.default_site_preference.enable()
      self.tic()

  def beforeTearDown(self):
    self.abort()
    for module in ( self.portal.person_module,
                    self.portal.organisation_module, ):
      module.manage_delObjects(list(module.objectIds()))
    self.tic()

  def test_data_coordinate_text_property(self):
    """Check New Coordinate API:
    asText compute printable value
    setCoordinateText store user value
    getCoordinateText return user value
    """
    person = self.getPersonModule().newContent(portal_type='Person')
    # check telephone
    telephone = person.newContent(portal_type='Telephone')
    self.assertEqual(telephone.getCoordinateText(), None)
    self.assertEqual(telephone.getCoordinateText(''), '')
    phone_number = '0320595959'
    telephone.setCoordinateText(phone_number)
    self.assertEqual(telephone.getCoordinateText(), phone_number)
    self.assertEqual(telephone.asText(), '+(0)-' + phone_number)

    # check address
    address = person.newContent(portal_type='Address')
    self.assertEqual(address.getCoordinateText(), None)
    self.assertEqual(address.getCoordinateText(''), '')
    address_text = """15 flower street
75016 PARIS"""
    address.setCoordinateText(address_text)
    self.assertEqual(address.getCoordinateText(), address_text)
    self.assertEqual(address.asText(), address_text)

    # Check Email
    email = person.newContent(portal_type='Email')
    self.assertEqual(email.getCoordinateText(), None)
    self.assertEqual(email.getCoordinateText(''), '')
    email_text = 'toto@example.com'
    email.setCoordinateText(email_text)
    self.assertEqual(email.getCoordinateText(), email_text)
    self.assertEqual(email.asText(), email_text)
    # check acquired accessors
    person.setDefaultEmailCoordinateText(email_text)
    self.assertEqual(person.getDefaultEmailCoordinateText(), email_text)
    self.assertEqual(person.getDefaultEmailText(), email_text)

  # Old API check backward compatibility
  def test_TelephoneAsText(self):
    # Test asText method
    pers = self.getPersonModule().newContent(portal_type='Person')
    tel = pers.newContent(portal_type='Telephone')
    tel.setTelephoneCountry(33)
    tel.setTelephoneArea(2)
    tel.setTelephoneNumber(12345678)
    tel.setTelephoneExtension(999)
    self.assertEqual('+33(0)2-12345678/999', tel.asText())

  def test_TelephonePreference(self):
    pers = self.getPersonModule().newContent(portal_type='Person')
    tel = pers.newContent(portal_type='Telephone')
    self.default_site_preference.setPreferredTelephoneDefaultCountryNumber('33')
    self.default_site_preference.setPreferredTelephoneDefaultAreaNumber('2')
    self.tic()

    tel.fromText(coordinate_text='11111111')
    self.assertEqual('+33(0)2-11111111',tel.asText())

  def test_TelephoneCountryAndAreaCodeRemains(self):
    pers = self.getPersonModule().newContent(portal_type='Person')
    tel = pers.newContent(portal_type='Telephone')
    self.default_site_preference.setPreferredTelephoneDefaultCountryNumber('')
    self.default_site_preference.setPreferredTelephoneDefaultAreaNumber('')
    self.tic()

    tel.fromText(coordinate_text='+11 1 11111111')
    tel.fromText(coordinate_text='+22333445555')
    self.assertEqual('+(0)-22333445555',tel.asText())

  def test_TelephoneInputList(self):
    pers = self.getPersonModule().newContent(portal_type='Person')
    tel = pers.newContent(portal_type='Telephone')
    input_list = [
      ['+11(0)1-11111111/111', '+11(0)1-11111111/111'],
      ['+11(0)1-11111111/', '+11(0)1-11111111'],
      ['+11(0)1-11111111', '+11(0)1-11111111'],
      ['+11(0)-1111111/111', '+11(0)-1111111/111'],
      ['+11(0)-1111111/', '+11(0)-1111111'],
      ['+11(0)-1111111', '+11(0)-1111111'],
      ['+11 111 1111 1111/111', '+11(0)111-1111-1111/111'],
      ['+11(1)11111111/', '+11(0)1-11111111'],
      ['+11(1)11111111', '+11(0)1-11111111'],
      ['+11()11111111/111', '+11(0)-11111111/111'],
      ['+11()11111111/', '+11(0)-11111111'],
      ['+11()11111111', '+11(0)-11111111'],
      ['+11()-11111111/111', '+11(0)-11111111/111'],
      ['+11()-11111111/', '+11(0)-11111111'],
      ['+11()-11111111', '+11(0)-11111111'],
      ['+11(111)011111/', '+11(0)111-011111'],
      ['+11-011-11111111/111', '+11(0)011-11111111/111'],
      ['+11-011-11111111/', '+11(0)011-11111111'],
      ['+11-011-11111111', '+11(0)011-11111111'],
      ['+110 1111111/111', '+110(0)-1111111/111'],
      ['+110 1111111/', '+110(0)-1111111'],
      ['+110 1111111', '+110(0)-1111111'],
      ['+111 11111111/111', '+111(0)-11111111/111'],
      ['+111 11111111/', '+111(0)-11111111'],
      ['+111 11111111', '+111(0)-11111111'],
      ['+(0)1-1111-1111/111', '+(0)1-1111-1111/111'],
      ['+(0)1-1111-1111/', '+(0)1-1111-1111'],
      ['+(0)1-1111-1111', '+(0)1-1111-1111'],
      ['+(0)1-11111111/111', '+(0)1-11111111/111'],
      ['+(0)1-11111111/', '+(0)1-11111111'],
      ['+(0)1-11111111', '+(0)1-11111111'],
      ['+(0)-11111111/111', '+(0)-11111111/111'],
      ['+(0)-11111111/', '+(0)-11111111'],
      ['+(0)-11111111', '+(0)-11111111'],
      ['+11(111)011111/111', '+11(0)111-011111/111'],
      ['+11(111)011111', '+11(0)111-011111'],
      ['(11)11111111/', '+(0)11-11111111'],
      ['(11)11111111', '+(0)11-11111111'],
      ['(11)-11111111/111', '+(0)11-11111111/111'],
      ['(11)-11111111/', '+(0)11-11111111'],
      ['(11)-11111111', '+(0)11-11111111'],
      ['+11 1 011111111/1', '+11(0)1-011111111/1'],
      ['+11 1 011111111', '+11(0)1-011111111'],
      ['+11 111 1111 1111/', '+11(0)111-1111-1111'],
      ['1-11 01 11 11/111', '+(0)1-11-011111/111'],
      ['1-11 01 11 11/', '+(0)1-11-011111'],
      ['1-11 01 11 11', '+(0)1-11-011111'],
      ['11 01 11 11/111', '+(0)11-01-1111/111'],
      ['11 01 11 11/', '+(0)11-01-1111'],
      ['11 01 11 11', '+(0)11-01-1111'],
      ['111 11 11/111', '+(0)111-11-11/111'],
      ['111 11 11/', '+(0)111-11-11'],
      ['111 11 11', '+(0)111-11-11'],
      ['111-11 11/111', '+(0)111-11-11/111'],
      ['111-11 11/', '+(0)111-11-11'],
      ['111-11 11', '+(0)111-11-11'],
      ['1111111/11', '+(0)-1111111/11'],
      ['011-111-1111/111', '+(0)11-111-1111/111'],
      ['011-111-1111/', '+(0)11-111-1111'],
      ['011-111-1111', '+(0)11-111-1111'],
      ['011(111)1111/111', '+(0)11-1111111/111'],
      ['011(111)1111/', '+(0)11-1111111'],
      ['011(111)1111', '+(0)11-1111111'],
      ['111/111-1111/111', '+(0)111-111-1111/111'],
      ['111/111-1111/', '+(0)111-111-1111'],
      ['111/111-1111', '+(0)111-111-1111'],
      ['+11 111111111/111', '+11(0)-111111111/111'],
      ['+11 111111111/', '+11(0)-111111111'],
      ['+11 111111111', '+11(0)-111111111'],
      ['+111-1101110/111', '+111(0)-1101110/111'],
      ['+111-1101110/', '+111(0)-1101110'],
      ['+111-1101110', '+111(0)-1101110'],
      ['110-111111/111', '+(0)110-111111/111'],
      ['110-111111/', '+(0)110-111111'],
      ['110-111111', '+(0)110-111111'],
      ['111.111.1111/111', '+(0)111-1111111/111'],
      ['111.111.1111/', '+(0)111-1111111'],
      ['111.111.1111', '+(0)111-1111111'],
      ['+ 11 (0)1-11 11 01 01/111', '+11(0)1-11-110101/111'],
      ['+ 11 (0)1-11 11 01 01/', '+11(0)1-11-110101'],
      ['+ 11 (0)1-11 11 01 01', '+11(0)1-11-110101'],
      ['+11-1 11 11 01 11/111', '+11(0)1-11-110111/111'],
      ['+11-1 11 11 01 11/', '+11(0)1-11-110111'],
      ['+11-1 11 11 01 11', '+11(0)1-11-110111'],
      ['+111 (0) 1 111 11011/111', '+111(0)1-11111011/111'],
      ['+111 (0) 1 111 11011/', '+111(0)1-11111011'],
      ['+111 (0) 1 111 11011', '+111(0)1-11111011'],
      ['+111 (0) 111111101-01/111', '+111(0)-11111110101/111'],
      ['+111 (0) 111111101-01/', '+111(0)-11111110101'],
      ['+111 (0) 111111101-01', '+111(0)-11111110101'],
      ['+111 111111/111', '+111(0)-111111/111'],
      ['+111 111111/', '+111(0)-111111'],
      ['+111 111111', '+111(0)-111111'],
      ['+111 101011111/111', '+111(0)-101011111/111'],
      ['+111 101011111/', '+111(0)-101011111'],
      ['+111 101011111', '+111(0)-101011111'],
      ['+11 (0)11 1011 1100/111', '+11(0)11-1011-1100/111'],
      ['+11 (0)11 1011 1100/', '+11(0)11-1011-1100'],
      ['+11 (0)11 1011 1100', '+11(0)11-1011-1100'],
      ['+11 (0)10 1101 1111/111', '+11(0)10-1101-1111/111'],
      ['+11 (0)10 1101 1111/', '+11(0)10-1101-1111'],
      ['+11 (0)10 1101 1111', '+11(0)10-1101-1111'],
      ['(111 11) 111111/111', '+111(0)11-111111/111'],
      ['(111 11) 111111/', '+111(0)11-111111'],
      ['(111 11) 111111', '+111(0)11-111111'],
      ['(111 11) 111-11-11/111', '+111(0)11-1111111/111'],
      ['(111 11) 111-11-11/', '+111(0)11-1111111'],
      ['(111 11) 111-11-11', '+111(0)11-1111111'],
      ['(111 11)101011/111', '+111(0)11-101011/111'],
      ['(111 11)101011/', '+111(0)11-101011'],
      ['(111 11)101011', '+111(0)11-101011'],
      ['(+111)101111111/111', '+111(0)-101111111/111'],
      ['(+111)101111111/', '+111(0)-101111111'],
      ['(+111)101111111', '+111(0)-101111111'],
      ['(+111) 11110011/111', '+111(0)-11110011/111'],
      ['(+111) 11110011/', '+111(0)-11110011'],
      ['(+111) 11110011', '+111(0)-11110011'],
      ['+11 (11) 1111 1111/111', '+11(0)11-11111111/111'],
      ['+11 (11) 1111 1111/', '+11(0)11-11111111'],
      ['+11 (11) 1111 1111', '+11(0)11-11111111'],
      ['+11 (11)-10111111/111', '+11(0)11-10111111/111'],
      ['+11 (11)-10111111/', '+11(0)11-10111111'],
      ['+11 (11)-10111111', '+11(0)11-10111111'],
      ['(+11-111) 1111111/111', '+11(0)111-1111111/111'],
      ['(+11-111) 1111111/', '+11(0)111-1111111'],
      ['(+11-111) 1111111', '+11(0)111-1111111'],
      ['(+11-11)-1111111/111', '+11(0)11-1111111/111'],
      ['(+11-11)-1111111/', '+11(0)11-1111111'],
      ['(+11-11)-1111111', '+11(0)11-1111111'],
      ['(11-11) 111-1111/111', '+11(0)11-1111111/111'],
      ['(11-11) 111-1111/', '+11(0)11-1111111'],
      ['(11-11) 111-1111', '+11(0)11-1111111'],
      ['(11-1) 1.111.111/111', '+11(0)1-1111111/111'],
      ['(11-1) 1.111.111/', '+11(0)1-1111111'],
      ['(11-1) 1.111.111', '+11(0)1-1111111'],
      ['+111-11111110/111', '+111(0)-11111110/111'],
      ['+111-11111110/', '+111(0)-11111110'],
      ['+111-11111110', '+111(0)-11111110'],
      ['(11 11) 110 11 11/111', '+11(0)11-1101111/111'],
      ['(11 11) 110 11 11/', '+11(0)11-1101111'],
      ['(11 11) 110 11 11', '+11(0)11-1101111'],
      ['(11 011) 110-10-11/111', '+11(0)011-1101011/111'],
      ['(11 011) 110-10-11/', '+11(0)011-1101011'],
      ['(11 011) 110-10-11', '+11(0)011-1101011'],
      ['+1 (111) 1101-111/111', '+1(0)111-1101111/111'],
      ['+1 (111) 1101-111/', '+1(0)111-1101111'],
      ['+1 (111) 1101-111', '+1(0)111-1101111'],
      ['1 (111) 1101-101/111', '+1(0)111-1101101/111'],
      ['1 (111) 1101-101/', '+1(0)111-1101101'],
      ['1 (111) 1101-101', '+1(0)111-1101101'],
      ['+10 (111) 110 11 11/111', '+10(0)111-1101111/111'],
      ['+10 (111) 110 11 11/', '+10(0)111-1101111'],
      ['+10 (111) 110 11 11', '+10(0)111-1101111'],
      ['+ 111 1 1101 101/111', '+111(0)1-1101-101/111'],
      ['+ 111 1 1101 101/', '+111(0)1-1101-101'],
      ['+ 111 1 1101 101', '+111(0)1-1101-101'],
      ['+11 1111-1111/111', '+11(0)-11111111/111'],
      ['+11 1111-1111/', '+11(0)-11111111'],
      ['+11 1111-1111', '+11(0)-11111111'],
      ['+(111 11) 100-11-11/111', '+111(0)11-1001111/111'],
      ['+(111 11) 100-11-11/', '+111(0)11-1001111'],
      ['+(111 11) 100-11-11', '+111(0)11-1001111'],
      ['+ 111-11-1110111/111', '+111(0)11-1110111/111'],
      ['+ 111-11-1110111/', '+111(0)11-1110111'],
      ['+ 111-11-1110111', '+111(0)11-1110111'],
      ['+ (111) 111-111/111', '+111(0)-111111/111'],
      ['+ (111) 111-111/', '+111(0)-111111'],
      ['+ (111) 111-111', '+111(0)-111111'],
      ['+111/1/1111 1100/111', '+111(0)1-11111100/111'],
      ['+111/1/1111 1100/', '+111(0)1-11111100'],
      ['+111/1/1111 1100', '+111(0)1-11111100'],
      ['+11(0)11-1111-1111/111', '+11(0)11-1111-1111/111'],
    ]

    for i in input_list:
      tel.fromText(coordinate_text=i[0])
      self.assertEqual(i[1],tel.asText())

  def test_TelephoneWhenTheDefaultCountryAndAreaPreferenceIsBlank(self):
    pers = self.getPersonModule().newContent(portal_type='Person')
    tel = pers.newContent(portal_type='Telephone')
    self.default_site_preference.setPreferredTelephoneDefaultCountryNumber('')
    self.default_site_preference.setPreferredTelephoneDefaultAreaNumber('')
    self.tic()
    tel.fromText(coordinate_text='12345678')
    self.assertEqual('+(0)-12345678',tel.asText())

  def test_TelephoneAsTextBlankNumber(self):
    # Test asText method with blank number
    pers = self.getPersonModule().newContent(portal_type='Person')
    tel = pers.newContent(portal_type='Telephone')
    self.assertEqual('', tel.asText())

  def test_TelephoneUrl(self):
    # http://www.rfc-editor.org/rfc/rfc3966.txt
    pers = self.getPersonModule().newContent(portal_type='Person')
    tel = pers.newContent(portal_type='Telephone')
    tel.setTelephoneCountry(33)
    tel.setTelephoneNumber(123456789)
    self.assertEqual('tel:+33123456789', tel.asURL())

    tel = pers.newContent(portal_type='Telephone')
    tel.setTelephoneNumber(123456789)
    self.assertEqual('tel:0123456789', tel.asURL())

    tel = pers.newContent(portal_type='Telephone')
    tel.setCoordinateText('+33123456789')
    self.assertEqual('tel:+33123456789', tel.asURL())

    # from rfc3966
    # """ "tel" URIs MUST NOT use spaces in visual separators to avoid
    # excessive escaping."""
    tel = pers.newContent(portal_type='Telephone')
    tel.setCoordinateText('01 23 45 67 89')
    self.assertEqual('tel:0123456789', tel.asURL())

  def test_EmptyTelephoneAsText(self):
    # asText method returns an empty string for empty telephones
    pers = self.getPersonModule().newContent(portal_type='Person')
    self.assertEqual('', pers.newContent(portal_type='Telephone').asText())


  def test_EmptyFaxAsText(self):
    # asText method returns an empty string for empty faxes
    pers = self.getPersonModule().newContent(portal_type='Person')
    self.assertEqual('', pers.newContent(portal_type='Fax').asText())

  def test_EmailAsURL(self):
    # asURL method works on email
    pers = self.getPersonModule().newContent(portal_type='Person')
    pers.setDefaultEmailText('nobody@example.com')
    email = pers.getDefaultEmailValue()
    self.assertEqual('mailto:nobody@example.com', email.asURL())
    self.assertEqual('mailto:nobody@example.com',
                      pers.Entity_getDefaultEmailAsURL())

  def test_LinkAsURL(self):
    person = self.getPersonModule().newContent(portal_type='Person')
    link = person.newContent(portal_type='Link',
                             url_string='http://www.nexedi.com/')
    self.assertEqual(link.asURL(), 'http://www.nexedi.com/')
    link = person.newContent(portal_type='Link',
                             url_string='www.nexedi.com')
    self.assertEqual(link.asURL(), 'http://www.nexedi.com')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Coordinate))
  return suite
