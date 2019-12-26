##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Kevin Deldycke <kevin_AT_nexedi_DOT_com>
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


import os
import unittest
from unittest import expectedFailure

from DateTime import DateTime
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import createZODBPythonScript, FileUpload
from AccessControl.SecurityManagement import newSecurityManager

class TestERP5Base(ERP5TypeTestCase):
  """ERP5 Base tests.

  Those are tests for erp5_base business template.
  """


  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_base',)


  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.login()
    self.datetime          = DateTime()
    self.portal            = self.getPortal()
    self.portal_categories = self.getCategoryTool()
    self.portal_catalog    = self.getCatalogTool()
    self.portal_preferences = self.getPreferenceTool()
    self.createCategories()

  def beforeTearDown(self):
    self.abort()
    for module in ( self.portal.person_module,
                    self.portal.organisation_module, ):
      module.manage_delObjects(list(module.objectIds()))
    self.tic()

  ##################################
  ##  Usefull methods
  ##################################

  def makeImageFileUpload(self, filename):
    return FileUpload(
            os.path.join(os.path.dirname(__file__),
            'test_data', 'images', filename))

  def login(self):
    """Create a new manager user and login.
    """
    user_name = 'kevin'
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser(user_name, '', ['Manager', 'Owner', 'Assignor'], [])
    user = user_folder.getUserById(user_name).__of__(user_folder)
    newSecurityManager(None, user)

  def login_as_auditor(self):
    """Create a new member user with Auditor role, and login
    """
    user_name = 'auditor_user'
    user_folder = self.portal.acl_users
    user_folder._doAddUser(user_name, '', ['Member', 'Auditor'], [])
    user = user_folder.getUserById(user_name).__of__(user_folder)
    newSecurityManager(None, user)

  def createCategories(self):
    """
      Create some categories for testing.
    """
    self.category_list = [
                         # Grade categories
                           {'base_category' : 'grade'
                           ,'category_relative_url': 'director'
                           ,'title': 'Director'
                           }
                         , {'base_category' : 'grade'
                           ,'category_relative_url': 'engineer'
                           ,'title': 'Engineer'
                           }

                         # Function categories
                         , {'base_category' : 'function'
                           ,'category_relative_url': 'hq'
                           ,'title': 'Headquarters'
                           }
                         , {'base_category' : 'functionwarehouse'
                           ,'category_relative_url': 'warehouse'
                           ,'title': 'Warehouse'
                           }
                         , {'base_category' : 'function'
                           ,'category_relative_url': 'research_center'
                           ,'title': 'Research Center'
                           }

                         # Activity categories
                         , {'base_category' : 'activity'
                           ,'category_relative_url': 'media'
                           ,'title': 'Media'
                           }
                         , {'base_category' : 'activity'
                           ,'category_relative_url': 'software'
                           ,'title': 'Software'
                           }
                         , {'base_category' : 'activity'
                           ,'category_relative_url': 'mechanics'
                           ,'title': 'Mechanics'
                           }
                         , {'base_category' : 'activity'
                           ,'category_relative_url': 'mechanics/aerospace'
                           ,'title': 'Aerospace'
                           }
                         , {'base_category' : 'activity'
                           ,'category_relative_url': 'mechanics/automotive'
                           ,'title': 'Automotive'
                           }

                         # Group categories
                         , {'base_category' : 'group'
                           ,'category_relative_url': 'nexedi'
                           ,'title': 'Nexedi'
                           }
                         , {'base_category' : 'group'
                           ,'category_relative_url': 'nexedi/storever'
                           ,'title': 'Storever'
                           }
                         , {'base_category' : 'group'
                           ,'category_relative_url': 'nexedi/rentalinux'
                           ,'title': 'Rentalinux'
                           }

                         # Role categories
                         , {'base_category' : 'role'
                           ,'category_relative_url': 'client'
                           ,'title': 'Client'
                           }
                         , {'base_category' : 'role'
                           ,'category_relative_url': 'supplier'
                           ,'title': 'Supplier'
                           }
                         , {'base_category' : 'role'
                           ,'category_relative_url': 'internal'
                           ,'title': 'Internal'
                           }

                         # Site categories
                         , {'base_category' : 'site'
                           ,'category_relative_url': 'production/madrid'
                           ,'title': 'Madrid Production Site'
                           }
                         , {'base_category' : 'site'
                           ,'category_relative_url': 'distibution/paris'
                           ,'title': 'Paris Distribution Site'
                           }
                         , {'base_category' : 'site'
                           ,'category_relative_url': 'distibution/tokyo'
                           ,'title': 'Tokyo Distribution Site'
                           }
                         , {'base_category' : 'site'
                           ,'category_relative_url': 'distibution/new_york'
                           ,'title': 'New York Distribution Site'
                           }

                         # Skill categories
                         , {'base_category' : 'skill'
                           ,'category_relative_url': 'design/graphic'
                           ,'title': 'Graphic'
                           }
                         , {'base_category' : 'skill'
                           ,'category_relative_url': 'design/sound'
                           ,'title': 'Sound'
                           }
                         , {'base_category' : 'skill'
                           ,'category_relative_url': 'it/consulting'
                           ,'title': 'Consulting'
                           }
                         , {'base_category' : 'skill'
                           ,'category_relative_url': 'it/programming'
                           ,'title': 'Programming'
                           }

                         # Region categories
                         , {'base_category' : 'region'
                           ,'category_relative_url': 'europe/france'
                           ,'title': 'France'
                           }
                         , {'base_category' : 'region'
                           ,'category_relative_url': 'europe/germany'
                           ,'title': 'Germany'
                           }
                         , {'base_category' : 'region'
                           ,'category_relative_url': 'america/canada'
                           ,'title': 'Canada'
                           }
                         , {'base_category' : 'region'
                           ,'category_relative_url': 'america/brazil'
                           ,'title': 'Brazil'
                           }

                         # Salary Level categories
                         , {'base_category' : 'salary_level'
                           ,'category_relative_url': 'france/1/A'
                           ,'title': '1.A'
                           }
                         , {'base_category' : 'salary_level'
                           ,'category_relative_url': 'france/1/B'
                           ,'title': '1.B'
                           }
                         , {'base_category' : 'salary_level'
                           ,'category_relative_url': 'france/1/C'
                           ,'title': '1.C'
                           }
                         , {'base_category' : 'salary_level'
                           ,'category_relative_url': 'france/2'
                           ,'title': '2'
                           }
                         ]

    # Create categories
    # Note : this code was taken from the CategoryTool_importCategoryFile python
    #        script (packaged in erp5_core).
    for category_dict in self.category_list:
      category_tool = self.portal_categories
      base_category_id = category_dict['base_category']
      if base_category_id not in category_tool.contentIds():
        category_tool.newContent(portal_type='Base Category',
                                 id=base_category_id)
      base_category_value = category_tool[base_category_id]
      category_relative_url = category_dict['category_relative_url']
      parent_value = base_category_value
      for category_id in category_relative_url.split('/'):
        # The current category is not existing
        if category_id not in parent_value.contentIds():
          parent_value.newContent(portal_type='Category',
                                  id=category_id)
        parent_value = parent_value[category_id]
      parent_value.setTitle(category_dict['title'])

  def getCategoryDictList(self, base_category):
    """
      Get a list of categories with same base categories.
    """
    return [category_dict for category_dict in self.category_list if\
            base_category == category_dict['base_category']]

  def _checkCategoryAccessorList(self, document, tested_base_category_list):
    """Check getters and setters on categories
    """
    for base_category in tested_base_category_list:
      category_dict_list = self.getCategoryDictList(base_category)
      base_accessor_id = convertToUpperCase(base_category)
      category_relative_url_list = []
      category_title_list = []
      category_value_list = []
      for category_dict in category_dict_list:
        category_relative_url = category_dict['category_relative_url']
        category_relative_url_list.append(category_relative_url)
        category_title = category_dict['title']
        category_title_list.append(category_title)
        category_path = '%s/%s' % (base_category, category_relative_url)
        category_document = self.portal_categories.resolveCategory(category_path)
        category_value_list.append(category_document)
        set_accessor = getattr(document, 'set' + base_accessor_id)
        set_accessor(category_relative_url)
        self.assertEqual(getattr(document, 'get' + base_accessor_id)(),
                          category_relative_url)
        self.assertEqual(getattr(document, 'get' + base_accessor_id + 'Title')(),
                          category_title)
        self.assertEqual(getattr(document, 'get' + base_accessor_id + 'Value')(),
                          category_document)
      set_accessor_list = 'set' + base_accessor_id + 'List'
      accessor_list = getattr(document, set_accessor_list)
      accessor_list(category_relative_url_list)
      self.assertEqual(getattr(document, 'get' + base_accessor_id + 'List')(),
                        category_relative_url_list)
      self.assertEqual(getattr(document, 'get' + base_accessor_id + 'TitleList')(),
                        category_title_list)
      self.assertEqual(getattr(document, 'get' + base_accessor_id + 'ValueList')(),
                        category_value_list)

  ##################################
  ##  Basic steps
  ##################################

  def stepCreateOrganisation(self, sequence=None, sequence_list=None, **kw):
    """
      Create an organisation.
    """
    portal_type = 'Organisation'
    organisation_module = self.portal.getDefaultModule(portal_type)
    organisation = organisation_module.newContent(portal_type=portal_type,
                                                  title='A new organisation')
    sequence.edit(organisation = organisation)

  def stepSetOrganisationCategories(self, sequence=None,
                                    sequence_list=None, **kw):
    """
      Set & Check default organisation categories
      (function, activity, site, group...).
    """
    organisation = sequence.get('organisation')

    tested_base_category_list = ('function', 'activity', 'group', 'role',
                                 'site', 'skill')
    self._checkCategoryAccessorList(organisation, tested_base_category_list)


  def stepResetOrganisationCategories(self, sequence=None,
                                      sequence_list=None, **kw):
    """
      Reset default organisation categories (function, activity, site, group...).
    """
    organisation = sequence.get('organisation')

    organisation.setFunction(None)
    organisation.setActivity(None)
    organisation.setGroup(None)
    organisation.setRole(None)
    organisation.setSite(None)
    organisation.setSkillList(None)

    self.assertEqual(organisation.getFunction()       , None)
    self.assertEqual(organisation.getActivity()       , None)
    self.assertEqual(organisation.getGroup()          , None)
    self.assertEqual(organisation.getRole()           , None)
    self.assertEqual(organisation.getSite()           , None)
    self.assertEqual(organisation.getSkillList(), [])

    self.assertEqual(organisation.getFunctionTitle()       , None)
    self.assertEqual(organisation.getActivityTitle()       , None)
    self.assertEqual(organisation.getGroupTitle()          , None)
    self.assertEqual(organisation.getRoleTitle()           , None)
    self.assertEqual(organisation.getSiteTitle()           , None)
    self.assertEqual(organisation.getSkillTitleList(), [])

    self.assertEqual(organisation.getFunctionValue()       , None)
    self.assertEqual(organisation.getActivityValue()       , None)
    self.assertEqual(organisation.getGroupValue()          , None)
    self.assertEqual(organisation.getRoleValue()           , None)
    self.assertEqual(organisation.getSiteValue()           , None)
    self.assertEqual(organisation.getSkillValueList(), [])


  def stepSetOrganisationAddress(self, sequence=None, sequence_list=None, **kw):
    """
      Set organisation address and test acquired properties and categories
      from the Address sub-object.
    """
    organisation = sequence.get('organisation')

    self.assertFalse(organisation.hasDefaultAddress())
    self.assertFalse(organisation.hasDefaultAddressCoordinateText())
    self.assertFalse(organisation.hasDefaultAddressRegion())
    self.assertFalse(organisation.hasDefaultAddressCity())

    self.assertFalse(organisation.hasDefaultTelephone())
    self.assertFalse(organisation.hasDefaultTelephoneCoordinateText())
    self.assertFalse(organisation.hasDefaultFax())
    self.assertFalse(organisation.hasDefaultFaxCoordinateText())

    self.assertFalse(organisation.hasDefaultEmail())
    self.assertFalse(organisation.hasDefaultEmailText())
    self.assertFalse(organisation.hasDefaultEmailCoordinateText())
    self.assertFalse(organisation.hasDefaultEmailUrlString())

    region = self.getCategoryDictList(base_category='region')[0]
    region_path   = region["category_relative_url"]
    region_title  = region["title"]
    region_object = self.portal_categories.resolveCategory('region/'+region_path)
    organisation.setDefaultAddressCity('Lille')
    organisation.setDefaultAddressRegion(region_path)
    organisation.setDefaultAddressZipCode('59000')
    organisation.setDefaultAddressStreetAddress('42, rue des gnous')
    organisation.setDefaultTelephoneText('+55(0)66-5555') # Phone follows default conventions
    organisation.setDefaultFaxText('+55(0)69-1337')
    organisation.setDefaultEmailText('kevin@truc-bidule.com')

    self.assertTrue('default_address' in organisation.contentIds())
    default_address = organisation.default_address
    self.assertEqual(default_address.getPortalType(), 'Address')
    self.assertEqual(organisation.getDefaultAddressValue(), default_address)

    self.assertEqual( organisation.getDefaultAddressCity()
                     , default_address.getCity()
                     )
    self.assertEqual( organisation.getDefaultAddressRegion()
                     , default_address.getRegion()
                     )
    self.assertEqual( organisation.getDefaultAddressRegionTitle()
                     , default_address.getRegionTitle()
                     )
    self.assertEqual( default_address.getRegionValue()
                     , region_object
                     )
    self.assertEqual( organisation.getDefaultAddressZipCode()
                     , default_address.getZipCode()
                     )
    self.assertEqual( organisation.getDefaultAddressStreetAddress()
                     , default_address.getStreetAddress()
                     )

    # Organisation's region is acquired from the Address object
    self.assertEqual( organisation.getRegion()
                     , default_address.getRegion()
                     )

    self.assertTrue('default_telephone' in organisation.contentIds())
    default_telephone = organisation.default_telephone
    self.assertEqual(default_telephone.getPortalType(), 'Telephone')
    self.assertEqual( organisation.getDefaultTelephoneText()
                     , default_telephone.asText()
                     )
    self.assertTrue(organisation.hasDefaultTelephone())
    self.assertTrue(organisation.hasDefaultTelephoneCoordinateText())

    self.assertTrue('default_fax' in organisation.contentIds())
    default_fax = organisation.default_fax
    self.assertEqual(default_fax.getPortalType(), 'Fax')
    self.assertEqual( organisation.getDefaultFaxText()
                     , default_fax.asText()
                     )
    self.assertTrue(organisation.hasDefaultFax())
    self.assertTrue(organisation.hasDefaultFaxCoordinateText())

    self.assertTrue('default_email' in organisation.contentIds())
    default_email = organisation.default_email
    self.assertEqual(default_email.getPortalType(), 'Email')
    self.assertEqual( organisation.getDefaultEmailText()
                     , default_email.asText()
                     )
    self.assertTrue(organisation.hasDefaultEmail())
    self.assertTrue(organisation.hasDefaultEmailText())
    self.assertTrue(organisation.hasDefaultEmailCoordinateText())
    self.assertTrue(organisation.hasDefaultEmailUrlString())

  def stepCreatePerson(self, sequence=None, sequence_list=None, **kw):
    """
      Create a person.
    """
    portal_type = 'Person'
    person_module = self.portal.getDefaultModule(portal_type)
    person = person_module.newContent( portal_type       = portal_type
                                     )
    sequence.edit(person = person)


  def stepSetPersonCareer(self, sequence=None, sequence_list=None, **kw):
    """
      Set & Check default person properties acquired through default career.
    """
    person = sequence.get('person')
    organisation = sequence.get('organisation')

    # Set subordination
    person.setCareerSubordinationValue(organisation)
    self.assertEqual(person.getCareerSubordinationValue(), organisation)

    # Set & Check simple properties with 'Career' prefix
    person.setCareerTitle('A brand new career step')
    person.setCareerDescription(
        'This career step correspond to my arrival at Nexedi as employee')
    self.assertEqual(person.getCareerTitle()      , 'A brand new career step')
    self.assertEqual(person.getCareerDescription(),
        'This career step correspond to my arrival at Nexedi as employee')

    dummy_date1 = self.datetime + 10
    dummy_date2 = self.datetime + 20
    person.setCareerStopDate(dummy_date2)
    person.setCareerStartDate(dummy_date1)
    person.setCareerSalaryCoefficient(1)
    person.setCareerCollectiveAgreementTitle('SYNTEC convention')
    person.setCareerActivity('software')
    person.setCareerReference('1234')
    self.assertEqual(person.getCareerStopDate()                , dummy_date2)
    self.assertEqual(person.getCareerStartDate()               , dummy_date1)
    self.assertEqual(person.getCareerSalaryCoefficient()       , 1)
    self.assertEqual(person.getCareerCollectiveAgreementTitle(), 'SYNTEC convention')
    self.assertEqual(person.getCareerActivityTitle(), 'Software')
    self.assertEqual(person.getCareerReference(), '1234')

    # activity must be acquired on person
    self.assertEqual(person.getActivity(), person.getCareerActivity())
    self.assertEqual('Software', person.getActivityTitle())

    tested_base_category_list = ('function', 'role', 'grade', 'salary_level',
                                 'skill')
    self._checkCategoryAccessorList(person, tested_base_category_list)

    # skill must be acquired on person
    self.tic()
    category_dict_list = self.getCategoryDictList('skill')
    skill_object_list = []
    for category_dict in category_dict_list:
      category_path = '%s/%s' % (category_dict['base_category'],
                                 category_dict['category_relative_url'])
      category_value = self.portal_categories.resolveCategory(category_path)
      skill_object_list.append(category_value)
    for skill_object in skill_object_list:
      self.assertTrue(person in skill_object.getSkillRelatedValueList())
    self.assertEqual(person.getSkillValue(), skill_object_list[0])

  def stepCheckPersonCareer(self, sequence=None, sequence_list=None, **kw):
    """
      Check the consistency of default_career properties with person
      getters (= check the acquisition).
    """
    person = sequence.get('person')

    # Check default career sub-object
    self.assertTrue('default_career' in person.contentIds())
    default_career = person.default_career
    self.assertEqual(default_career.getPortalType(), 'Career')

    # Test getter with 'Career' prefix
    self.assertEqual(person.getCareer()           , default_career.getRelativeUrl())
    self.assertEqual(person.getCareerTitle()      , default_career.getTitle())
    self.assertEqual(person.getCareerReference(), default_career.getReference())
    self.assertEqual(person.getCareerValue()      , default_career)
    self.assertEqual(person.getCareerDescription(), default_career.getDescription())

    self.assertEqual(person.getCareerFunction()     , default_career.getFunction())
    self.assertEqual(person.getCareerFunctionTitle(), default_career.getFunctionTitle())
    self.assertEqual(person.getCareerFunctionValue(), default_career.getFunctionValue())

    # Test getter with no prefix (aka 'transparent' getters) on simple properties
    #   then on category properties
    self.assertEqual(person.getCareerStopDate()                , default_career.getStopDate())
    self.assertEqual(person.getCareerStartDate()               , default_career.getStartDate())
    self.assertEqual(person.getCareerSalaryCoefficient()       , default_career.getSalaryCoefficient())
    self.assertEqual(person.getCareerCollectiveAgreementTitle(), default_career.getCollectiveAgreementTitle())

    self.assertEqual(person.getCareerRole()     , default_career.getRole())
    self.assertEqual(person.getCareerRoleTitle(), default_career.getRoleTitle())
    self.assertEqual(person.getCareerRoleValue(), default_career.getRoleValue())

    self.assertEqual(person.getCareerGrade()     , default_career.getGrade())
    self.assertEqual(person.getCareerGradeTitle(), default_career.getGradeTitle())
    self.assertEqual(person.getCareerGradeValue(), default_career.getGradeValue())

    self.assertEqual(person.getCareerActivity(),
                      default_career.getActivity())
    self.assertEqual(person.getCareerActivityTitle(),
                      default_career.getActivityTitle())
    self.assertEqual(person.getCareerActivityValue(),
                      default_career.getActivityValue())

    self.assertEqual(person.getCareerSalaryLevel()     , default_career.getSalaryLevel())
    self.assertEqual(person.getCareerSalaryLevelTitle(), default_career.getSalaryLevelTitle())
    self.assertEqual(person.getCareerSalaryLevelValue(), default_career.getSalaryLevelValue())

    self.assertEqual(person.getCareerSkillList()     , default_career.getSkillList())
    self.assertEqual(person.getCareerSkillTitleList(), default_career.getSkillTitleList())
    self.assertEqual(person.getCareerSkillValueList(), default_career.getSkillValueList())

    self.assertEqual(person.getCareerSubordination(), default_career.getSubordination())
    # Person's subordination is acquired from default career
    self.assertEqual(person.getSubordination(), default_career.getSubordination())

  def stepAddCareerStepInAnotherOrganisation(self, sequence=None, **kw) :
    """Adds another career step on the person."""
    person = sequence.get('person')
    other_organisation = self.getOrganisationModule().newContent(
                            portal_type = 'Organisation',
                            title = 'Another Organistion')
    new_career_title = 'new career title'
    # Create a new career step.
    person.Person_shiftDefaultCareer()
    self.assertEqual( 2,
          len(person.contentValues(filter={'portal_type':'Career'})))
    person.setCareerSubordination(other_organisation.getRelativeUrl())
    person.setCareerTitle(new_career_title)

    # Get the new and the old career, as Person_shiftDefaultCareer changes
    # objects id, this may be the only safe way ...
    old_career_step = None
    new_career_step = None
    for career in person.contentValues(filter={'portal_type':'Career'}):
      if career.getTitle() == new_career_title :
        new_career_step = career
      else :
        old_career_step = career
    self.assertNotEquals(new_career_step, None)
    self.assertNotEquals(old_career_step, None)

    sequence.edit( old_career_step = old_career_step,
                   new_career_step = new_career_step,
                   new_organisation = other_organisation,
                   old_organisation = sequence.get('organisation') )

  def stepCheckCareerSubordination (self, sequence=None, **kw) :
    """checks that setting subordination on a career does not conflict
        with acquisition."""
    person = sequence.get('person')
    old_career_step = sequence.get('old_career_step')
    new_career_step = sequence.get('new_career_step')
    new_organisation = sequence.get('new_organisation')
    old_organisation = sequence.get('old_organisation')
    new_organisation_title = new_organisation.getTitle()
    old_organisation_title = old_organisation.getTitle()

    self.assert_( "subordination/%s" % old_organisation.getRelativeUrl() in
                    old_career_step.getCategoryList(),
                '%s not in %s' % (old_organisation.getRelativeUrl(),
                                  old_career_step.getCategoryList()))
    self.assertEqual( old_career_step.getSubordination(),
                       old_organisation.getRelativeUrl() )
    self.assertEqual( old_career_step.getSubordinationTitle(),
                       old_organisation_title )

    self.assert_( "subordination/%s" % new_organisation.getRelativeUrl() in
                    new_career_step.getCategoryList(),
                '%s not in %s' % (new_organisation.getRelativeUrl(),
                                  new_career_step.getCategoryList()))
    self.assertEqual( new_career_step.getSubordination(),
                       new_organisation.getRelativeUrl() )
    self.assertEqual( new_career_step.getSubordinationTitle(),
                       new_organisation_title )

  def stepCheckChangePersonAddress(self, sequence=None, **kw) :
    """
    We must make sure that if we change the address of a person,
    then it will not change the address of the organisation.
    """
    person = sequence.get('person')
    organisation = sequence.get('organisation')
    self.assertEqual(organisation.getDefaultAddressCity(),'Lille')
    self.assertEqual(organisation.getDefaultAddressZipCode(), '59000')
    self.assertEqual(person.getDefaultAddressCity(),'Lille')
    self.assertEqual(person.getDefaultAddressZipCode(), '59000')

    # here, the parameters we pass to edit are the same as the one acquired
    # from the organisation, edit shouldn't do anything
    person.edit(
        default_address_city='Lille',
        default_address_zip_code='59000')

    self.assertEqual(person.getDefaultAddress(),
        organisation.getDefaultAddress())
    self.assertEqual(person.getDefaultAddressCity(),'Lille')
    self.assertEqual(person.getDefaultAddressZipCode(), '59000')

    # here, the first parameter we pass will trigger the creation of a
    # subobject on person, and we need to make sure that the second one gets
    # copied (when calling edit from the interface, all displayed fields are
    # passed to edit)
    person.edit(
        default_address_city='La Garnache',
        default_address_zip_code='59000')

    self.assertNotEquals(person.getDefaultAddress(),
        organisation.getDefaultAddress())
    self.assertEqual(person.getDefaultAddressCity(),'La Garnache')
    self.assertEqual(person.getDefaultAddressZipCode(), '59000')
    self.assertEqual(organisation.getDefaultAddressCity(),'Lille')
    self.assertEqual(organisation.getDefaultAddressZipCode(), '59000')

    # retry last action, inverting the modified property
    # XXX Whether this test is usefull or not completely depends on Python
    # implementation. Python currently does not guarantee the order of a dict,
    # so it might very well be that at some point, a change in the
    # implementation makes the test always succeed, where it would fail with
    # the curent implementation.
    person.manage_delObjects(['default_address'])

    person.edit(
        default_address_city='Lille',
        default_address_zip_code='69000')

    self.assertNotEquals(person.getDefaultAddress(),
        organisation.getDefaultAddress())
    self.assertEqual(person.getDefaultAddressCity(),'Lille')
    self.assertEqual(person.getDefaultAddressZipCode(), '69000')
    self.assertEqual(organisation.getDefaultAddressCity(),'Lille')
    self.assertEqual(organisation.getDefaultAddressZipCode(), '59000')

    # if the address of the person is the same of the organisation
    # there is no reason to create a subobject (default_address)
    person.manage_delObjects(['default_address'])
    person.edit(career_subordination_value=organisation)
    self.assertTrue('default_address' not in person.objectIds())
    self.assertEqual(person.getDefaultAddress(),
        organisation.getDefaultAddress())
    self.assertEqual(person.getDefaultAddressCity(),
        organisation.getDefaultAddressCity())
    self.assertEqual(person.getDefaultAddressZipCode(),
        organisation.getDefaultAddressZipCode())
    # if the address of the person is different then the subobject
    # (default_address) must be created.
    person.edit(default_address_city='La Garnache')
    self.assertTrue('default_address' in person.objectIds())
    self.assertNotEquals(person.getDefaultAddressCity(),
         organisation.getDefaultAddressCity())


  ##################################
  ##  Tests
  ##################################

  def test_Organisation(self):
    """
      Test basic behaviour of Organisation.
    """
    sequence_list = SequenceList()
    step_list = [ 'stepCreateOrganisation'
                , 'stepSetOrganisationCategories'
                , 'stepResetOrganisationCategories'
                , 'stepSetOrganisationAddress'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)


  def test_Person(self):
    """
      Test basic behaviour of Person.
    """
    sequence_list = SequenceList()
    step_list = [ 'stepCreatePerson'
                , 'stepCreateOrganisation'
                , 'stepSetPersonCareer'
                , 'stepCheckPersonCareer'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_Subordination(self):
    """
      Tests that career steps subordination properties behave correctly
    """
    sequence_list = SequenceList()
    step_list = [ 'stepCreatePerson'
                , 'stepCreateOrganisation'
                , 'stepSetPersonCareer'
                , 'stepAddCareerStepInAnotherOrganisation'
                , 'stepCheckCareerSubordination'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_SubordinationAndAddress(self):
    """
      Tests that career steps subordination properties behave correctly
    """
    sequence_list = SequenceList()
    step_list = [ 'stepCreatePerson'
                , 'stepCreateOrganisation'
                , 'stepSetOrganisationAddress'
                , 'stepSetPersonCareer'
                , 'stepCheckChangePersonAddress'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_SubordinationAcquisition(self):
    """
    Tests that persons acquire properties through subordination.
    """
    portal_categories = self.portal.portal_categories
    organisation = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            role_value=portal_categories.role.client,
                            activity_value=portal_categories.activity.software,
                            group_value=portal_categories.group.nexedi,)
    person = self.portal.person_module.newContent(
                            portal_type='Person',
                            career_subordination_value=organisation)
    self.assertEqual(portal_categories.role.client,
                      person.getRoleValue())
    self.assertEqual(portal_categories.activity.software,
                      person.getActivityValue())
    self.assertEqual(portal_categories.group.nexedi,
                      person.getGroupValue())


  # Dates
  def test_DatesOnPerson(self):
    """Tests dates on Person objects.
    """
    pers = self.getPersonModule().newContent(portal_type='Person')
    birthday = DateTime(1999, 01, 01)
    now = DateTime()
    pers.edit(birthday = birthday)
    self.assertEqual(birthday, pers.getBirthday())
    self.assertEqual(birthday, pers.getStartDate())

    for slot in ['year', 'month', 'day', 'hour', 'minute']:
      self.assertEqual(getattr(now, slot)(),
                        getattr(pers.getCreationDate(), slot)(),
                        'Wrong creation date %s' % pers.getCreationDate())

  def test_DatesOnOrganisation(self):
    """Tests dates on Organisation objects.
    """
    org = self.getOrganisationModule().newContent(portal_type='Organisation')
    start_date = DateTime(1999, 01, 01)
    now = DateTime()
    org.edit(start_date = start_date)
    self.assertEqual(start_date, org.getStartDate())

    for slot in ['year', 'month', 'day', 'hour', 'minute']:
      self.assertEqual(getattr(now, slot)(),
                        getattr(org.getCreationDate(), slot)(),
                        'Wrong creation date %s' % org.getCreationDate())

  def test_BirthplaceOnPerson(self):
    """Tests birthplace on Person objects.
    """
    pers = self.getPersonModule().newContent(portal_type='Person')
    pers.setDefaultBirthplaceAddressCity('Lille')
    self.assertEqual('Lille', pers.getDefaultBirthplaceAddressCity())

  def test_getTranslatedId(self):
    pers = self.getPersonModule().newContent(
                portal_type='Person', id='default_email')
    self.assertEqual(None, pers.getTranslatedId())
    pers.setDefaultEmailText('nobody@example.com')
    email = pers.getDefaultEmailValue()
    self.assertEqual('Default Email', str(email.getTranslatedId()))

  def test_SubordinationAcquisitionAndFunction(self):
    # function is acquired from the subordination, organisation function are
    # usually only nodes, and persons functions are leaves.
    function_node = self.portal.portal_categories.function.newContent(
         portal_type='Category', id='function_node', title='Function Node')
    function_leave = function_node.newContent(
         portal_type='Category', id='function_leave', title='Function Leave')
    self.portal.portal_caches.clearAllCache()
    organisation = self.getOrganisationModule().newContent(
                                  portal_type='Organisation',
                                  function_value=function_node)
    person = self.getPersonModule().newContent(portal_type='Person',
                            career_subordination_value=organisation)
    # on Organisation_view, the user usually select node for functions:
    self.assertEqual([['', ''], ['Function Node', 'function_node']],
      organisation.Organisation_view.my_function.get_value('items'))

    # on Person_view, the user select leaves for functions:
    field = person.Person_view.my_career_function
    self.assertTrue('function_node' not in [x[1] for x in
                          field.get_value('items')])
    self.assertTrue('function_node/function_leave' in [x[1] for x in
                          field.get_value('items')])
    # person acquire function from the organisation
    self.assertEqual(person.getFunctionValue(), function_node)
    # but the user interface does not show the acquired value in this case
    self.assertEqual('', field.get_value('default'))
    # (the field is working)
    person.setDefaultCareerFunctionValue(function_leave)
    self.assertEqual(person.getFunctionValue(), function_leave)
    self.assertEqual('function_node/function_leave',
                      field.get_value('default'))


  def test_CreateBankAccount(self):
    # We can add Bank Accounts inside Persons and Organisation
    for entity in (self.getPersonModule().newContent(portal_type='Person'),
        self.getOrganisationModule().newContent(portal_type='Organisation')):
      bank_account = entity.newContent(portal_type='Bank Account')
      self.assertEqual([], bank_account.checkConsistency())
      bank_account.newContent(portal_type='Agent')
      self.assertEqual([], bank_account.checkConsistency())
      self.portal.portal_workflow.doActionFor(bank_account, 'validate_action')
      self.assertEqual('validated', bank_account.getValidationState())

  def test_CreateImage(self):
    # We can add Images inside Persons and Organisation
    for entity in (self.getPersonModule().newContent(portal_type='Person'),
        self.getOrganisationModule().newContent(portal_type='Organisation')):
      image = entity.newContent(portal_type='Embedded File')
      self.assertEqual([], image.checkConsistency())
      image.view() # viewing the image does not cause error

  def test_ConvertImage(self):
    image = self.portal.newContent(portal_type='Image', id='test_image')
    image.edit(file=self.makeImageFileUpload('erp5_logo.png'))
    self.assertEqual('image/png', image.getContentType())
    self.assertEqual((320, 250), (image.getWidth(), image.getHeight()))

    from Products.ERP5Type.Document import newTempImage
    def convert(**kw):
      image_type, image_data = image.convert('jpg', display='thumbnail', **kw)
      self.assertEqual('image/jpeg', image_type)
      thumbnail = newTempImage(self.portal, 'thumbnail', data=image_data)
      self.assertEqual(image_type, thumbnail.getContentType())
      self.assertEqual((128, 100), (thumbnail.getWidth(),
                                    thumbnail.getHeight()))
      return thumbnail.getSize()
    self.assertTrue(convert() < convert(quality=100))

  def test_ConvertImagePdata(self):
    image = self.portal.newContent(portal_type='Image', id='test_image')
    image.edit(file=self.makeImageFileUpload('erp5_logo.bmp'))
    from OFS.Image import Pdata
    self.assertTrue(isinstance(image.data, Pdata))

    image_type, image_data = image.convert('jpg', display='thumbnail')
    self.assertEqual('image/jpeg', image_type)
    # magic
    self.assertEqual('\xff', image_data[0])
    self.assertEqual('\xd8', image_data[1])

  def test_ImageSize(self):
    image = self.portal.newContent(portal_type='Image', id='test_image')
    image.edit(file=self.makeImageFileUpload('erp5_logo.png'))
    self.assertEqual(320, image.getWidth())
    self.assertEqual(250, image.getHeight())
    image.edit(file=self.makeImageFileUpload('erp5_logo_small.png'))
    self.assertEqual(160, image.getWidth())
    self.assertEqual(125, image.getHeight())

  def test_Person_getCareerStartDate(self):
    # Person_getCareerStartDate scripts returns the date when an employee
    # started to work for an employer
    first_organisation = self.getOrganisationModule().newContent(
                                  portal_type='Organisation')
    second_organisation = self.getOrganisationModule().newContent(
                                  portal_type='Organisation')
    person = self.getPersonModule().newContent(
              portal_type='Person',
              default_career_subordination_value=first_organisation)
    current_career = person.getDefaultCareerValue()
    current_career.setStartDate(DateTime(2002, 1, 1))
    previous_career = person.newContent(
                              portal_type='Career',
                              subordination_value=first_organisation,
                              start_date=DateTime(2001, 1, 1))
    other_organisation_career= person.newContent(
                              portal_type='Career',
                              subordination_value=second_organisation,
                              start_date=DateTime(1999, 9, 9))
    self.assertEqual(DateTime(2001, 1, 1),
         person.Person_getCareerStartDate(
            subordination_relative_url=first_organisation.getRelativeUrl()))
    self.assertEqual(DateTime(1999, 9, 9),
         person.Person_getCareerStartDate(
            subordination_relative_url=second_organisation.getRelativeUrl()))

    # only validated careers are used (for conveniance, draft careers are
    # accepted as well)
    another_cancelled_career = person.newContent(
                              portal_type='Career',
                              subordination_value=first_organisation,
                              start_date=DateTime(1996, 9, 9))
    another_cancelled_career.cancel()
    self.assertEqual(DateTime(2001, 01, 01),
         person.Person_getCareerStartDate(
            subordination_relative_url=first_organisation.getRelativeUrl()))

  def test_Person_getAge(self):
    person = self.getPersonModule().newContent(
                                  portal_type='Person',
                                  start_date=DateTime(2001, 2, 3))

    self.assertEqual(1,
          person.Person_getAge(year=1, at_date=DateTime(2002, 2, 4)))
    self.assertTrue(person.Person_getAge(year=1) > 5)

    # if year is not passed, the script returns the age in a translated string.
    age_as_text = person.Person_getAge(at_date=DateTime(2002, 2, 4))
    self.assertEqual(age_as_text, "1 years old")

  def test_AssignmentWorkflow(self):
    person = self.getPersonModule().newContent(portal_type='Person',)
    assignment = person.newContent(portal_type='Assignment')
    self.assertEqual('draft', assignment.getValidationState())
    self.portal.portal_workflow.doActionFor(assignment, 'open_action')
    self.assertEqual('open', assignment.getValidationState())
    self.portal.portal_workflow.doActionFor(assignment, 'update_action')
    self.assertEqual('updated', assignment.getValidationState())
    self.portal.portal_workflow.doActionFor(assignment, 'open_action')
    self.assertEqual('open', assignment.getValidationState())
    # date is set automatically when closing
    self.assertEqual(None, assignment.getStopDate())
    self.portal.portal_workflow.doActionFor(assignment, 'close_action')
    self.assertEqual('closed', assignment.getValidationState())
    self.assertNotEquals(None, assignment.getStopDate())
    self.assertEqual(DateTime().day(), assignment.getStopDate().day())

  def test_ERP5Site_checkDataWithScript(self):
    # note the '/'.join(obj.getPhysicalPath()) idiom:

    # it's basically a obj.absolute_url(relative=1) without escaping:
    #  - getRelativeUrl() is not enough as it does not return a full
    #    path for portal_categories.action_type for instance
    #  - absolute_url escapes 'Foo Tool' into 'Foo%20Tool'
    test = 'test_ERP5Site_checkDataWithScript'
    createZODBPythonScript(self.getSkinsTool().custom, test, '',
                           'return "/".join(context.getPhysicalPath()),')

    organisation = self.getOrganisationModule() \
                       .newContent(portal_type='Organisation')
    organisation.setDefaultAddressCity('Lille')
    organisation.setDefaultAddressZipCode('59000')
    person = self.getPersonModule().newContent(portal_type='Person')
    person.setDefaultEmailText('nobody@example.com')

    portal_activities = self.getActivityTool()
    active_process = portal_activities.newActiveProcess()
    portal_activities.ERP5Site_checkDataWithScript(method_id=test, tag=test,
                                       active_process=active_process.getPath())
    self.tic()
    relative_url_list = sum((x.detail.split('\n')
                             for x in active_process.getResultList()), [])

    self.assertEqual(len(relative_url_list), len(set(relative_url_list)))
    for obj in organisation, person, person.getDefaultEmailValue():
      self.assertTrue('/'.join(obj.getPhysicalPath()) in relative_url_list)
    for relative_url in relative_url_list:
      self.assertTrue('/' in relative_url)
      self.assertNotEquals(None, self.portal.unrestrictedTraverse(relative_url))

  def test_standard_translated_related_keys(self):
    # make sure we can search by "translated_validation_state_title" and
    # "translated_portal_type"
    message_catalog = self.portal.Localizer.erp5_ui
    lang = 'fr'
    if lang not in [x['id'] for x in
        self.portal.Localizer.get_languages_map()]:
      self.portal.Localizer.manage_addLanguage(lang)

    message_catalog.gettext('Draft', add=1)
    message_catalog.gettext('Person', add=1)
    message_catalog.message_edit('Draft', lang, 'Brouillon', '')
    message_catalog.message_edit('Person', lang, 'Personne', '')

    self.portal.ERP5Site_updateTranslationTable()

    person_1 = self.portal.person_module.newContent(portal_type='Person')
    person_1.validate()
    person_2 = self.portal.person_module.newContent(portal_type='Person')
    organisation = self.portal.organisation_module.newContent(
                            portal_type='Organisation')
    self.tic()

    # patch the method, we'll abort later
    self.portal.Localizer.get_selected_language = lambda: lang

    self.assertEqual({person_1, person_2}, {x.getObject()
      for x in self.portal.portal_catalog(translated_portal_type='Personne')})
    self.assertEqual({person_2, organisation}, {x.getObject()
      for x in self.portal.portal_catalog(
        translated_validation_state_title='Brouillon',
        portal_type=('Person', 'Organisation'))})
    self.assertEqual([person_2],
        [x.getObject() for x in
          self.portal.portal_catalog(translated_validation_state_title='Brouillon',
                                     translated_portal_type='Personne')])
    self.abort()

  def test_Base_createCloneDocument(self):
    module = self.portal.person_module
    module.manage_permission('Add portal content', ['Member'], 0)
    self.login_as_auditor()
    person = module.newContent(portal_type='Person',)
    self.assertEqual(1, len(module))
    person.Base_createCloneDocument()
    self.assertEqual(2, len(module))

  def test_Base_createCloneDocument_document_in_document(self):
    module = self.portal.person_module
    module.manage_permission('Add portal content', ['Member'], 0)
    self.login_as_auditor()
    person = module.newContent(portal_type='Person',)
    # An address is a document, it cannot contain anything
    address = person.newContent(portal_type='Address')
    self.assertEqual(0, len(address.allowedContentTypes()))

    self.assertEqual(1, len(person))
    address.Base_createCloneDocument()
    self.assertEqual(2, len(person))

  def test_Base_createCloneDocument_folder_in_document(self):
    module = self.portal.person_module
    module.manage_permission('Add portal content', ['Member'], 0)
    self.login_as_auditor()
    person = module.newContent(portal_type='Person',)
    bank_account = person.newContent(portal_type='Bank Account')
    # A bank account is a folder, it can contain other documents
    self.assertNotEquals(0, len(bank_account.allowedContentTypes()))

    self.assertEqual(1, len(person))
    bank_account.Base_createCloneDocument()
    self.assertEqual(2, len(person))

  def getWorkflowHistory(self, document, workflow_id):
    return self.portal.portal_workflow.getInfoFor(ob=document, name='history',
        wf_id=workflow_id)

  def test_comment_edit_workflow(self):
    comment = 'some comment'
    person = self.portal.person_module.newContent(portal_type='Person')
    person.edit(comment = comment)
    workflow_history = self.getWorkflowHistory(person, 'edit_workflow')
    # person has property comment with value
    self.assertEqual(person.comment, comment)
    # workflow has no artificial comment
    self.assertFalse(comment in [q['comment'] for q in workflow_history ])

  def test_comment_edit_workflow_store_workflow(self):
    comment = 'some comment'
    person = self.portal.person_module.newContent(portal_type='Person')
    self.portal.portal_workflow.doActionFor(person, 'edit_action', comment=comment)
    workflow_history = self.getWorkflowHistory(person, 'edit_workflow')
    # person is not changed
    self.assertEqual(getattr(person, 'comment', None), None)
    # workflow is affected
    self.assertTrue(comment in [q['comment'] for q in workflow_history ])

  def test_comment_validation_workflow(self):
    comment = 'some comment'
    person = self.portal.person_module.newContent(portal_type='Person')
    person.validate(comment = comment)
    workflow_history = self.getWorkflowHistory(person, 'validation_workflow')
    # person is not changed
    self.assertEqual(getattr(person, 'comment', None), None)
    # workflow is affected
    self.assertTrue(comment in [q['comment'] for q in workflow_history])

  def test_user_creation(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    assignment = person.newContent(portal_type='Assignment',
                                   group='nexedi/storever')
    self.assertNotEquals(None, assignment.getGroupValue())
    assignment.open()
    self.portal.portal_workflow.doActionFor(person, 'create_user_action',
                  reference='user_login',
                  password='pass',
                  password_confirm='pass')
    self.tic()

    # a user is created
    user = self.portal.acl_users.getUser('user_login')
    self.assertNotEquals(None, user)

    # This user does not have a preference created automatically ...
    newSecurityManager(None, user.__of__(self.portal.acl_users))
    self.assertEquals(None,
        self.portal.portal_catalog.getResultValue(portal_type='Preference',
                                                  owner=user.getId()))
    # ... but only when `getActiveUserPreference`
    preference = self.portal.portal_preferences.getActiveUserPreference()
    self.assertNotEquals(None, preference)
    self.tic()
    self.assertNotEquals(None,
        self.portal.portal_catalog.getResultValue(portal_type='Preference',
                                                  owner=user.getId()))

    # for his assignment group
    self.assertEqual('group/nexedi/storever',
        self.portal.portal_preferences.getPreferredSectionCategory())

  def test_default_address_acquisition(self):
    # more complete version of test_04_SubordinationAndAddress
    organisation = \
      self.portal.organisation_module.newContent(portal_type='Organisation')
    self.assertEqual(None, organisation.getDefaultAddressStreetAddress())
    self.assertEqual(None, organisation.getDefaultAddressCity())
    self.assertEqual(None, organisation.getDefaultAddressZipCode())
    self.assertEqual(None, organisation.getDefaultAddressText())

    self.assertEqual(None, organisation.getDefaultAddressRegion())
    self.assertEqual(None, organisation.getRegion())

    organisation.setDefaultAddressRegion('europe/france')
    self.assertEqual('europe/france', organisation.getDefaultAddressRegion())
    # region is acquired from default address
    self.assertEqual('europe/france', organisation.getRegion())
    self.assertEqual(None, organisation.getDefaultAddressStreetAddress())
    self.assertEqual(None, organisation.getDefaultAddressCity())
    self.assertEqual(None, organisation.getDefaultAddressZipCode())

    organisation.setDefaultAddressStreetAddress('Street Address')
    organisation.setDefaultAddressCity('City')
    organisation.setDefaultAddressZipCode('Zip Code')

    self.assertEqual('Street Address', organisation.getDefaultAddressStreetAddress())
    self.assertEqual('City', organisation.getDefaultAddressCity())
    self.assertEqual('Zip Code', organisation.getDefaultAddressZipCode())

    person = self.portal.person_module.newContent(portal_type='Person')
    self.assertEqual(None, person.getDefaultAddressStreetAddress())
    self.assertEqual(None, person.getDefaultAddressCity())
    self.assertEqual(None, person.getDefaultAddressZipCode())
    self.assertEqual(None, person.getDefaultAddressText())
    self.assertEqual(None, person.getDefaultAddressRegion())
    self.assertEqual(None, person.getRegion())

    # On persons, Address is acquired from the default carreer
    person.setDefaultCareerSubordinationValue(organisation)

    self.assertEqual('Street Address', person.getDefaultAddressStreetAddress())
    self.assertEqual('City', person.getDefaultAddressCity())
    self.assertEqual('Zip Code', person.getDefaultAddressZipCode())
    self.assertEqual('europe/france', person.getDefaultAddressRegion())
    # region is acquired from default address
    self.assertEqual('europe/france', person.getRegion())

    # we can set different values on the person address without modifying
    # organisation address
    person.setDefaultAddressStreetAddress('Person Street Address')
    person.setDefaultAddressCity('Person City')
    person.setDefaultAddressZipCode('Person Zip Code')
    self.assertEqual('Person Street Address', person.getDefaultAddressStreetAddress())
    self.assertEqual('Person City', person.getDefaultAddressCity())
    self.assertEqual('Person Zip Code', person.getDefaultAddressZipCode())
    self.assertEqual('Street Address', organisation.getDefaultAddressStreetAddress())
    self.assertEqual('City', organisation.getDefaultAddressCity())
    self.assertEqual('Zip Code', organisation.getDefaultAddressZipCode())

  def test_default_telephone_acquisition(self):
    organisation = \
      self.portal.organisation_module.newContent(portal_type='Organisation')
    self.assertEqual(None, organisation.getDefaultTelephoneCoordinateText())
    # There is no problem if this organisation has a region (this use to be a
    # problem)
    organisation.setDefaultAddressRegion('europe/france')
    self.assertEqual(None, organisation.getDefaultTelephoneCoordinateText())

    organisation.setDefaultTelephoneText("12345")
    self.assertEqual('12345', organisation.getDefaultTelephoneCoordinateText())

    person = self.portal.person_module.newContent(portal_type='Person')
    self.assertEqual(None, person.getDefaultTelephoneCoordinateText())

    # On persons, Telephone is acquired from the default carreer
    person.setDefaultCareerSubordinationValue(organisation)
    self.assertEqual('12345', person.getDefaultTelephoneCoordinateText())

    # we can set different values on the person address without modifying
    # organisation address
    person.setDefaultTelephoneText('54321')
    self.assertEqual('54321', person.getDefaultTelephoneCoordinateText())
    self.assertEqual('12345', organisation.getDefaultTelephoneCoordinateText())

  def test_mobile_telephone_acquisition(self):
    organisation = \
      self.portal.organisation_module.newContent(portal_type='Organisation')
    self.assertEqual(None, organisation.getMobileTelephoneCoordinateText())
    # There is no problem if this organisation has a region (this use to be a
    # problem)
    organisation.setDefaultAddressRegion('europe/france')
    self.assertEqual(None, organisation.getMobileTelephoneCoordinateText())

    organisation.setMobileTelephoneText("12345")
    self.assertEqual('12345', organisation.getMobileTelephoneCoordinateText())

    person = self.portal.person_module.newContent(portal_type='Person')
    self.assertEqual(None, person.getMobileTelephoneCoordinateText())

    # On persons, Telephone is acquired from the default carreer
    person.setDefaultCareerSubordinationValue(organisation)
    self.assertEqual('12345', person.getMobileTelephoneCoordinateText())

    # we can set different values on the person address without modifying
    # organisation address
    person.setMobileTelephoneText('54321')
    self.assertEqual('54321', person.getMobileTelephoneCoordinateText())
    self.assertEqual('12345', organisation.getMobileTelephoneCoordinateText())

  def test_default_fax_acquisition(self):
    organisation = \
      self.portal.organisation_module.newContent(portal_type='Organisation')
    self.assertEqual(None, organisation.getDefaultTelephoneCoordinateText())
    # There is no problem if this organisation has a region (this use to be a
    # problem)
    organisation.setDefaultAddressRegion('europe/france')
    self.assertEqual(None, organisation.getDefaultFaxCoordinateText())

    organisation.setDefaultFaxText("12345")
    self.assertEqual('12345', organisation.getDefaultFaxCoordinateText())

    person = self.portal.person_module.newContent(portal_type='Person')
    self.assertEqual(None, person.getDefaultFaxCoordinateText())

    # On persons, Fax is acquired from the default carreer
    person.setDefaultCareerSubordinationValue(organisation)
    self.assertEqual('12345', person.getDefaultFaxCoordinateText())

    # we can set different values on the person address without modifying
    # organisation address
    person.setDefaultFaxText('54321')
    self.assertEqual('54321', person.getDefaultFaxCoordinateText())
    self.assertEqual('12345', organisation.getDefaultFaxCoordinateText())

  def test_default_email_acquisition(self):
    organisation = \
      self.portal.organisation_module.newContent(portal_type='Organisation')
    self.assertEqual(None, organisation.getDefaultTelephoneCoordinateText())
    # There is no problem if this organisation has a region (this use to be a
    # problem)
    organisation.setDefaultAddressRegion('europe/france')
    self.assertEqual(None, organisation.getDefaultEmailCoordinateText())

    organisation.setDefaultEmailText("organisation@example.com")
    self.assertEqual('organisation@example.com',
      organisation.getDefaultEmailCoordinateText())

    person = self.portal.person_module.newContent(portal_type='Person')
    self.assertEqual(None, person.getDefaultEmailCoordinateText())
    self.assertFalse(person.hasDefaultEmailCoordinateText())

    # On persons, Email is acquired from the default carreer
    person.setDefaultCareerSubordinationValue(organisation)
    self.assertEqual('organisation@example.com',
      person.getDefaultEmailCoordinateText())
    self.assertFalse(person.hasDefaultEmailCoordinateText())

    # we can set different values on the person address without modifying
    # organisation address
    person.setDefaultEmailText('person@example.com')
    self.assertEqual('person@example.com', person.getDefaultEmailCoordinateText())
    self.assertEqual('organisation@example.com',
      organisation.getDefaultEmailCoordinateText())
    self.assertTrue(person.hasDefaultEmailCoordinateText())

  def test_alternate_email_acquisition(self):
    organisation = \
      self.portal.organisation_module.newContent(portal_type='Organisation')
    self.assertEqual(None, organisation.getAlternateEmailCoordinateText())
    # There is no problem if this organisation has a region (this use to be a
    # problem)
    organisation.setDefaultAddressRegion('europe/france')
    self.assertEqual(None, organisation.getAlternateEmailCoordinateText())

    organisation.setAlternateEmailText("organisation@example.com")
    self.assertEqual('organisation@example.com',
      organisation.getAlternateEmailCoordinateText())

    person = self.portal.person_module.newContent(portal_type='Person')
    self.assertEqual(None, person.getAlternateEmailCoordinateText())

    # On persons, Email is acquired from the default carreer
    person.setDefaultCareerSubordinationValue(organisation)
    self.assertEqual('organisation@example.com',
      person.getAlternateEmailCoordinateText())

    # we can set different values on the person address without modifying
    # organisation address
    person.setAlternateEmailText('person@example.com')
    self.assertEqual('person@example.com', person.getAlternateEmailCoordinateText())
    self.assertEqual('organisation@example.com',
      organisation.getAlternateEmailCoordinateText())

  def test_content_type_local_property(self):
    portal_type = 'Person'
    person_module = self.portal.getDefaultModule(portal_type)
    person = person_module.newContent(portal_type=portal_type)

    # assert that test has a sense
    self.assertEqual(getattr(person, 'getContentType', None), None)

    # edit content_type on document which has no content_type property configured
    person.edit(content_type='text/xml')

  def test_EmbeddedFile_content_type(self):
    embedded_file = self.portal.person_module.newContent(
        portal_type='Person'
    ).newContent(
        portal_type='Embedded File'
    )

    self.assertFalse(embedded_file.hasContentType())
    self.assertEqual('text/plain', embedded_file.getContentType('text/plain'))

    embedded_file.edit(content_type='text/xml')
    self.assertEqual('text/xml', embedded_file.getContentType())
    self.assertEqual('text/xml', embedded_file.getProperty('content_type'))

  def test_BankAccount_validateIBAN(self):
    self.assertTrue(
        self.portal.BankAccount_validateIBAN(
        'GR1601101250000000012300695', request=None))
    # spaces are allowed
    self.assertTrue(
        self.portal.BankAccount_validateIBAN(
        'GR16 0110 1250 0000 0001 2300 695', request=None))
    self.assertFalse(
        self.portal.BankAccount_validateIBAN(
        'GR16 0110 1250 0000 0001 2300 696', request=None))
    self.assertFalse(
        self.portal.BankAccount_validateIBAN(
        '12345', request=None))

  def test_BankAccount_validateBIC(self):
    self.assertTrue(
        self.portal.BankAccount_validateBIC(
        'DEUTDEFF', request=None))
    self.assertTrue(
        self.portal.BankAccount_validateBIC(
        'NEDSZAJJ', request=None))
    self.assertFalse(
        self.portal.BankAccount_validateBIC(
        'X', request=None))

  def test_user_title(self):
    newContent = self.portal.person_module.newContent
    login = super(TestERP5Base, self).login
    # User 1 and 2 have the same title (picked from user 1's user id),
    # hopefully not shared with other users.
    # User 3 has a different title, also hopefully not shared.
    user_1 = newContent(portal_type='Person')
    common_user_title = user_1.Person_getUserId()
    user_1.setTitle(common_user_title)
    user_2 = newContent(portal_type='Person')
    user_2.setTitle(common_user_title)
    user_3 = newContent(portal_type='Person')
    user_3.setTitle(user_3.Person_getUserId())
    # any member can add persons
    self.portal.person_module.manage_permission(
      'Add portal content',
      roles=['Member', 'Manager'],
      acquire=0,
    )
    self.tic()
    # Create whatever documents.
    must_find_path_list = []
    login(user_1.Person_getUserId())
    must_find_path_list.append(newContent(portal_type='Person', title='Owned by user_1').getPath())
    login(user_2.Person_getUserId())
    must_find_path_list.append(newContent(portal_type='Person', title='Owned by user_2').getPath())
    login(user_3.Person_getUserId())
    newContent(portal_type='Person', title='Owned by user_3')
    login()
    self.tic()
    self.assertItemsEqual(
      must_find_path_list,
      [
        x.path
        for x in self.portal.portal_catalog(
          owner_title=common_user_title,
          portal_type='Person',
        )
      ],
    )

  def test_CoordinateReachability(self):
    '''
      Check the reachability_workflow and coordinate_interaction_workflow
      for Coordinates.
      Test also checks accessors like getDefaultEmailValidationState.
    '''
    portal_type = 'Person'
    person_module = self.portal.getDefaultModule(portal_type)
    person = person_module.newContent(portal_type=portal_type)
    # Address
    address = person.newContent(portal_type='Address')
    self.assertEqual(address.getValidationState(), 'reachable')
    address.declareUnreachable()
    self.assertEqual(address.getValidationState(), 'unreachable')
    address.setStreetAddress('Rue Nationale')
    self.assertEqual(address.getValidationState(), 'reachable')
    self.tic()
    address.declareUnreachable()
    self.assertEqual(address.getValidationState(), 'unreachable')
    address.setZipCode('59000')
    self.assertEqual(address.getValidationState(), 'reachable')
    self.tic()
    address.declareUnreachable()
    self.assertEqual(address.getValidationState(), 'unreachable')
    address.setCity('Lille')
    self.assertEqual(address.getValidationState(), 'reachable')
    self.tic()
    address.declareUnreachable()
    self.assertEqual(address.getValidationState(), 'unreachable')
    address.setRegionValue(self.portal.portal_categories.region.europe.france)
    self.assertEqual(address.getValidationState(), 'reachable')
    self.tic()
    address.declareUnreachable()
    self.assertEqual(address.getValidationState(), 'unreachable')
    address.edit(zip_code='59160', street_address='Rue Victor Hugo')
    self.assertEqual(address.getValidationState(), 'reachable')
    # this address is not default coordinate, in deletion id should remain as is
    address_id = address.getId()
    address.delete()
    self.assertEqual(address.getValidationState(), 'deleted')
    self.tic()
    self.assertEqual(address.getId(), address_id)
    # Telephone
    person.setMobileTelephoneCoordinateText('+12345')
    telephone = person.mobile_telephone
    self.assertEqual(person.getMobileTelephoneValidationState(), 'reachable')
    self.tic()
    telephone.declareUnreachable()
    self.assertEqual(person.getMobileTelephoneValidationState(), 'unreachable')
    telephone.setTelephoneCountry('33')
    self.assertEqual(person.getMobileTelephoneValidationState(), 'reachable')
    self.tic()
    telephone.declareUnreachable()
    self.assertEqual(person.getMobileTelephoneValidationState(), 'unreachable')
    telephone.setTelephoneArea('0')
    self.assertEqual(person.getMobileTelephoneValidationState(), 'reachable')
    self.tic()
    telephone.declareUnreachable()
    self.assertEqual(person.getMobileTelephoneValidationState(), 'unreachable')
    telephone.setTelephoneCity('07')
    self.assertEqual(person.getMobileTelephoneValidationState(), 'reachable')
    self.tic()
    telephone.declareUnreachable()
    self.assertEqual(person.getMobileTelephoneValidationState(), 'unreachable')
    telephone.setTelephoneNumber('12345678')
    self.assertEqual(person.getMobileTelephoneValidationState(), 'reachable')
    self.tic()
    telephone.declareUnreachable()
    self.assertEqual(person.getMobileTelephoneValidationState(), 'unreachable')
    telephone.setTelephoneExtension('0')
    self.assertEqual(person.getMobileTelephoneValidationState(), 'reachable')
    self.tic()
    telephone.declareUnreachable()
    self.assertEqual(person.getMobileTelephoneValidationState(), 'unreachable')
    telephone.edit(telephone_country='30', telephone_number='12345670')
    self.assertEqual(person.getMobileTelephoneValidationState(), 'reachable')
    self.tic()
    telephone.declareUnreachable()
    telephone.setCoordinateText('+33-123.456.789')
    self.assertEqual(person.getMobileTelephoneValidationState(), 'reachable')
    self.tic()
    telephone.declareUnreachable()
    telephone.setMobileTelephoneCoordinateText('+33-123.456.780')
    self.assertEqual(person.getMobileTelephoneValidationState(), 'reachable')
    self.tic()
    telephone.declareUnreachable()
    telephone.edit(coordinate_text='+33-789 456 123 ')
    self.assertEqual(person.getMobileTelephoneValidationState(), 'reachable')
    # Check also that id we change a non-coordinate nothing happens
    self.tic()
    telephone.declareUnreachable()
    telephone.edit(description="This must be old number", title="telephone")
    self.assertEqual(person.getMobileTelephoneValidationState(), 'unreachable')
    # this telephone is default coordinate, in deletion id should chenge
    telephone.delete()
    self.assertEqual(telephone.getValidationState(), 'deleted')
    self.assertNotEqual(telephone.getId(), 'mobile_telephone')
    # Fax
    person.setFaxCoordinateText('+12345')
    fax = person.default_fax
    self.assertEqual(person.getDefaultFaxValidationState(), 'reachable')
    self.tic()
    fax.declareUnreachable()
    self.assertEqual(person.getDefaultFaxValidationState(), 'unreachable')
    fax.setTelephoneCountry('33')
    self.assertEqual(person.getDefaultFaxValidationState(), 'reachable')
    self.tic()
    fax.declareUnreachable()
    self.assertEqual(person.getDefaultFaxValidationState(), 'unreachable')
    fax.setTelephoneArea('0')
    self.assertEqual(person.getDefaultFaxValidationState(), 'reachable')
    self.tic()
    fax.declareUnreachable()
    self.assertEqual(person.getDefaultFaxValidationState(), 'unreachable')
    fax.setTelephoneCity('07')
    self.assertEqual(person.getDefaultFaxValidationState(), 'reachable')
    self.tic()
    fax.declareUnreachable()
    self.assertEqual(person.getDefaultFaxValidationState(), 'unreachable')
    fax.setTelephoneNumber('12345678')
    self.assertEqual(person.getDefaultFaxValidationState(), 'reachable')
    self.tic()
    fax.declareUnreachable()
    self.assertEqual(person.getDefaultFaxValidationState(), 'unreachable')
    fax.setTelephoneExtension('0')
    self.assertEqual(person.getDefaultFaxValidationState(), 'reachable')
    self.tic()
    fax.declareUnreachable()
    self.assertEqual(person.getDefaultFaxValidationState(), 'unreachable')
    fax.setDefaultFaxTelephoneExtension('0')
    self.assertEqual(person.getDefaultFaxValidationState(), 'reachable')
    # this fax is default coordinate, in deletion id should chenge
    fax.delete()
    self.assertEqual(fax.getValidationState(), 'deleted')
    self.assertNotEqual(fax.getId(), 'default_fax')
    # Email
    person.setDefaultEmailCoordinateText('test@mail1.com')
    email = person.default_email
    self.assertEqual(person.getDefaultEmailValidationState(), 'reachable')
    self.tic()
    email.declareUnreachable()
    self.assertEqual(person.getDefaultEmailValidationState(), 'unreachable')
    email.setCoordinateText('test@mail2.com')
    self.assertEqual(person.getDefaultEmailValidationState(), 'reachable')
    self.tic()
    email.declareUnreachable()
    self.assertEqual(person.getDefaultEmailValidationState(), 'unreachable')
    person.setDefaultEmailCoordinateText('test@mail3.com')
    self.assertEqual(person.getDefaultEmailValidationState(), 'reachable')
    # this email is default coordinate, in deletion id should chenge
    email.delete()
    self.assertEqual(email.getValidationState(), 'deleted')
    self.assertNotEqual(email.getId(), 'default_email')
    # External Identifier
    external_identifier = person.newContent(portal_type='External Identifier')
    self.assertEqual(external_identifier.getValidationState(), 'reachable')
    self.tic()
    external_identifier.declareUnreachable()
    self.assertEqual(external_identifier.getValidationState(), 'unreachable')
    external_identifier.setCoordinateText('test')
    self.assertEqual(external_identifier.getValidationState(), 'reachable')
    # this external_identifier is not default coordinate, in deletion id should remain as is
    external_identifier_id = external_identifier.getId()
    external_identifier.delete()
    self.assertEqual(external_identifier.getValidationState(), 'deleted')
    self.tic()
    self.assertEqual(external_identifier.getId(), external_identifier_id)
    # Link
    link = person.newContent(portal_type='Link')
    self.assertEqual(link.getValidationState(), 'reachable')
    self.tic()
    link.declareUnreachable()
    self.assertEqual(link.getValidationState(), 'unreachable')
    link.setUrlString('www.dummy-link.com')
    self.assertEqual(link.getValidationState(), 'reachable')
    # this link is not default coordinate, in deletion id should remain as is
    link_id = link.getId()
    link.delete()
    self.assertEqual(link.getValidationState(), 'deleted')
    self.tic()
    self.assertEqual(link.getId(), link_id)
    # Chat Address
    chat_address = person.newContent(portal_type='Chat Address')
    self.assertEqual(chat_address.getValidationState(), 'reachable')
    self.tic()
    chat_address.declareUnreachable()
    self.assertEqual(chat_address.getValidationState(), 'unreachable')
    chat_address.setUrlString('www.dummy-chat.com')
    self.assertEqual(chat_address.getValidationState(), 'reachable')
    # this link is not default coordinate, in deletion id should remain as is
    chat_address_id = chat_address.getId()
    chat_address.delete()
    self.assertEqual(chat_address.getValidationState(), 'deleted')
    self.tic()
    self.assertEqual(chat_address.getId(), chat_address_id)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Base))
  return suite
