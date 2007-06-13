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
import os, sys
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
from Products.ERP5Type.tests.utils import createZODBPythonScript

class TestGeographicalAddress(ERP5TypeTestCase):
  """
  ERP5 Geographical Address related tests.

  The purpose of this test is to check that the getText function defined
  on a Geographical Address returns the standard text format.
  """

  run_all_test = 1
  entity_portal_type = 'Person'
  address_portal_type = 'Address'
  street_address_text = "rue Truc"
  street_address_number = "11"
  zip_code_text = "12345"
  city_text = "City1"

  def getTitle(self):
    return "Geographical Address"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base', )

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

  def enableLightInstall(self):
    """
    You can override this. 
    Return if we should do a light install (1) or not (0)
    """
    return 1

  def enableActivityTool(self):
    """
    You can override this.
    Return if we should create (1) or not (0) an activity tool.
    """
    return 1

  def afterSetUp(self, quiet=1, run=run_all_test):
    self.login()
    self.portal = self.getPortal()
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
        o = self.category_tool.region.newContent(portal_type='Category',
                                               id=category_id,
                                               title=category_id.capitalize())
    self.region_category_list = ['region/%s' % x for x \
                                  in region_category_list]

  def stepTic(self,**kw):
    self.tic()

  def stepCreateEntity(self, sequence=None, sequence_list=None, **kw):
    """
    Create an entity
    """
    portal = self.getPortal()
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
    self.assertEquals(address.asText(),
        "%s %s\n%s %s" % (self.street_address_number,
                          self.street_address_text,
                          self.city_text,
                          self.zip_code_text))

  def test_01_standardAddress(self, quiet=0, run=run_all_test):
    """
      Test property existence
    """
    if not run: return
    
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
    createZODBPythonScript(self.getPortal().portal_skins.custom,
                           'Address_asText', '', """
return '%s\\n%s %s' % \\
       (context.getStreetAddress(),
        context.getZipCode(), context.getCity())
""")
  
  def stepCheckAddressAsTextScript(self, sequence=None,
                                   sequence_list=None, **kw):
    """
    Check getAddressText
    """
    address = sequence.get('address')
    self.assertEquals(address.asText(),
        "%s %s\n%s %s" % (self.street_address_number,
                          self.street_address_text,
                          self.zip_code_text,
                          self.city_text))

  def test_02_asTextScript(self, quiet=0, run=run_all_test):
    """
      Test property existence
    """
    if not run: return
    
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

if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGeographicalAddress))
    return suite
