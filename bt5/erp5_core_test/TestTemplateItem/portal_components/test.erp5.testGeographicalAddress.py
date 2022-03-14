##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import createZODBPythonScript


class TestGeographicalAddress(ERP5TypeTestCase):
  """
  ERP5 Geographical Address related tests.

  The purpose of this test is to check that the getText function defined
  on a Geographical Address returns the standard text format.
  """

  entity_portal_type = 'Person'
  address_portal_type = 'Address'
  street_address_text = "rue Truc"
  street_address_number = "11"
  zip_code_text = "12345"
  city_text = "City1"

  def afterSetUp(self):
    self.category_tool = self.getCategoryTool()
    self.createCategories()

  def createCategories(self):
    """
      Light install create only base categories, so we create
      some categories for testing them
    """
    region_category_list = ['country1', 'country2', ]
    if len(self.category_tool.region.contentValues()) == 0 :
      for category_id in region_category_list:
        self.category_tool.region.newContent(portal_type='Category',
                                               id=category_id,
                                               title=category_id.capitalize())
    self.region_category_list = ['region/%s' % x for x \
                                  in region_category_list]

  def stepCreateEntity(self, sequence=None, sequence_list=None, **kw):
    """
    Create an entity
    """
    portal = self.portal
    module = portal.getDefaultModule(self.entity_portal_type)
    entity = module.newContent(portal_type=self.entity_portal_type)
    sequence.edit(
        entity=entity,
    )

  def stepCreateAddress(self, sequence=None, sequence_list=None, **kw):
    """
    Create a address
    """
    entity = sequence.get('entity')
    address = entity.newContent(portal_type=self.address_portal_type)
    sequence.edit(
        address=address,
    )

  def stepSetTextAddressValue(self, sequence=None, sequence_list=None, **kw):
    """
    Set standard text value.
    """
    address = sequence.get('address')
    address.setStreetAddress("%s %s" % (self.street_address_number,
                                        self.street_address_text))
    address.setZipCode(self.zip_code_text)
    address.setCity(self.city_text)
    address.setRegionValue(self.portal.portal_categories.region.country1)

  def stepCheckAddressText(self, sequence=None,
                           sequence_list=None, **kw):
    """
    Check getAddressText
    """
    address = sequence.get('address')
    self.assertEqual(address.asText(),
        "%s %s\n%s %s" % (self.street_address_number,
                          self.street_address_text,
                          self.zip_code_text,
                          self.city_text,))

  def test_01_standardAddress(self):
    """
      Test property existence
    """
    sequence_list = SequenceList()
    sequence_string = '\
              CreateEntity \
              CreateAddress \
              SetTextAddressValue \
              CheckAddressText \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCreateAsTextScript(self, sequence=None, **kw) :
    """
    This script returns a different address format.
    """
    createZODBPythonScript(self.portal.portal_skins.custom,
                           'Address_asText', '', """
return '%s\\n%s %s COUNTRY' % \\
       (context.getStreetAddress(),
        context.getZipCode(), context.getCity())
""")

  def stepCheckAddressAsTextScript(self, sequence=None,
                                   sequence_list=None, **kw):
    """
    Check getAddressText
    """
    address = sequence.get('address')
    self.assertEqual(address.asText(),
        "%s %s\n%s %s COUNTRY" % (self.street_address_number,
                          self.street_address_text,
                          self.zip_code_text,
                          self.city_text))

  def test_02_asTextScript(self):
    """
      Test property existence
    """
    sequence_list = SequenceList()
    sequence_string = '\
              CreateEntity \
              CreateAddress \
              SetTextAddressValue \
              CreateAsTextScript \
              CheckAddressAsTextScript \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

