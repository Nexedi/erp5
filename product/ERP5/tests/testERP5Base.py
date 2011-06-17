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
import transaction

from DateTime import DateTime
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import createZODBPythonScript, FileUpload
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.backportUnittest import expectedFailure

class TestERP5Base(ERP5TypeTestCase):
  """ERP5 Base tests.

  Those are tests for erp5_base business template.
  """

  # pseudo constants
  RUN_ALL_TEST = 1
  QUIET = 1


  ##################################
  ##  ZopeTestCase Skeleton
  ##################################

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "ERP5 Base"


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
    transaction.abort()
    for module in ( self.portal.person_module,
                    self.portal.organisation_module, ):
      module.manage_delObjects(list(module.objectIds()))
    transaction.commit()
    self.tic()

  ##################################
  ##  Usefull methods
  ##################################

  def makeImageFileUpload(self, filename):
    return FileUpload(
            os.path.join(os.path.dirname(__file__),
            'test_data', 'images', filename), 'rb')

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
        self.assertEquals(getattr(document, 'get' + base_accessor_id)(),
                          category_relative_url)
        self.assertEquals(getattr(document, 'get' + base_accessor_id + 'Title')(),
                          category_title)
        self.assertEquals(getattr(document, 'get' + base_accessor_id + 'Value')(),
                          category_document)
      set_accessor_list = 'set' + base_accessor_id + 'List'
      accessor_list = getattr(document, set_accessor_list)
      accessor_list(category_relative_url_list)
      self.assertEquals(getattr(document, 'get' + base_accessor_id + 'List')(),
                        category_relative_url_list)
      self.assertEquals(getattr(document, 'get' + base_accessor_id + 'TitleList')(),
                        category_title_list)
      self.assertEquals(getattr(document, 'get' + base_accessor_id + 'ValueList')(),
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

    self.assertEquals(organisation.getFunction()       , None)
    self.assertEquals(organisation.getActivity()       , None)
    self.assertEquals(organisation.getGroup()          , None)
    self.assertEquals(organisation.getRole()           , None)
    self.assertEquals(organisation.getSite()           , None)
    self.assertEquals(organisation.getSkillList(), [])

    self.assertEquals(organisation.getFunctionTitle()       , None)
    self.assertEquals(organisation.getActivityTitle()       , None)
    self.assertEquals(organisation.getGroupTitle()          , None)
    self.assertEquals(organisation.getRoleTitle()           , None)
    self.assertEquals(organisation.getSiteTitle()           , None)
    self.assertEquals(organisation.getSkillTitleList(), [])

    self.assertEquals(organisation.getFunctionValue()       , None)
    self.assertEquals(organisation.getActivityValue()       , None)
    self.assertEquals(organisation.getGroupValue()          , None)
    self.assertEquals(organisation.getRoleValue()           , None)
    self.assertEquals(organisation.getSiteValue()           , None)
    self.assertEquals(organisation.getSkillValueList(), [])


  def stepSetOrganisationAddress(self, sequence=None, sequence_list=None, **kw):
    """
      Set organisation address and test acquired properties and categories
      from the Address sub-object.
    """
    organisation = sequence.get('organisation')

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

    self.failUnless('default_address' in organisation.contentIds())
    default_address = organisation.default_address
    self.assertEquals(default_address.getPortalType(), 'Address')
    self.assertEquals(organisation.getDefaultAddressValue(), default_address)

    self.assertEquals( organisation.getDefaultAddressCity()
                     , default_address.getCity()
                     )
    self.assertEquals( organisation.getDefaultAddressRegion()
                     , default_address.getRegion()
                     )
    self.assertEquals( organisation.getDefaultAddressRegionTitle()
                     , default_address.getRegionTitle()
                     )
    self.assertEquals( default_address.getRegionValue()
                     , region_object
                     )
    self.assertEquals( organisation.getDefaultAddressZipCode()
                     , default_address.getZipCode()
                     )
    self.assertEquals( organisation.getDefaultAddressStreetAddress()
                     , default_address.getStreetAddress()
                     )
    
    # Organisation's region is acquired from the Address object
    self.assertEquals( organisation.getRegion()
                     , default_address.getRegion()
                     )
    
    self.failUnless('default_telephone' in organisation.contentIds())
    default_telephone = organisation.default_telephone
    self.assertEquals(default_telephone.getPortalType(), 'Telephone')
    self.assertEquals( organisation.getDefaultTelephoneText()
                     , default_telephone.asText()
                     )
                     
    self.failUnless('default_fax' in organisation.contentIds())
    default_fax = organisation.default_fax
    self.assertEquals(default_fax.getPortalType(), 'Fax')
    self.assertEquals( organisation.getDefaultFaxText()
                     , default_fax.asText()
                     )
    
    self.failUnless('default_email' in organisation.contentIds())
    default_email = organisation.default_email
    self.assertEquals(default_email.getPortalType(), 'Email')
    self.assertEquals( organisation.getDefaultEmailText()
                     , default_email.asText()
                     )

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
    self.assertEquals(person.getCareerSubordinationValue(), organisation)
    
    # Set & Check simple properties with 'Career' prefix
    person.setCareerTitle('A brand new career step')
    person.setCareerDescription(
        'This career step correspond to my arrival at Nexedi as employee')
    self.assertEquals(person.getCareerTitle()      , 'A brand new career step')
    self.assertEquals(person.getCareerDescription(),
        'This career step correspond to my arrival at Nexedi as employee')

    dummy_date1 = self.datetime + 10
    dummy_date2 = self.datetime + 20
    person.setCareerStopDate(dummy_date2)
    person.setCareerStartDate(dummy_date1)
    person.setCareerSalaryCoefficient(1)
    person.setCareerCollectiveAgreementTitle('SYNTEC convention')
    person.setCareerActivity('software')
    person.setCareerReference('1234')
    self.assertEquals(person.getCareerStopDate()                , dummy_date2)
    self.assertEquals(person.getCareerStartDate()               , dummy_date1)
    self.assertEquals(person.getCareerSalaryCoefficient()       , 1)
    self.assertEquals(person.getCareerCollectiveAgreementTitle(), 'SYNTEC convention')
    self.assertEquals(person.getCareerActivityTitle(), 'Software')
    self.assertEquals(person.getCareerReference(), '1234')

    # activity must be acquired on person
    self.assertEquals(person.getActivity(), person.getCareerActivity())
    self.assertEquals('Software', person.getActivityTitle())

    tested_base_category_list = ('function', 'role', 'grade', 'salary_level',
                                 'skill')
    self._checkCategoryAccessorList(person, tested_base_category_list)

    # skill must be acquired on person 
    transaction.commit()
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
    self.assertEquals(person.getSkillValue(), skill_object_list[0])

  def stepCheckPersonCareer(self, sequence=None, sequence_list=None, **kw):
    """
      Check the consistency of default_career properties with person
      getters (= check the acquisition).
    """
    person = sequence.get('person')

    # Check default career sub-object
    self.failUnless('default_career' in person.contentIds())
    default_career = person.default_career
    self.assertEquals(default_career.getPortalType(), 'Career')

    # Test getter with 'Career' prefix
    self.assertEquals(person.getCareer()           , default_career.getRelativeUrl())
    self.assertEquals(person.getCareerTitle()      , default_career.getTitle())
    self.assertEquals(person.getCareerReference(), default_career.getReference())
    self.assertEquals(person.getCareerValue()      , default_career)
    self.assertEquals(person.getCareerDescription(), default_career.getDescription())

    self.assertEquals(person.getCareerFunction()     , default_career.getFunction())
    self.assertEquals(person.getCareerFunctionTitle(), default_career.getFunctionTitle())
    self.assertEquals(person.getCareerFunctionValue(), default_career.getFunctionValue())

    # Test getter with no prefix (aka 'transparent' getters) on simple properties
    #   then on category properties
    self.assertEquals(person.getCareerStopDate()                , default_career.getStopDate())
    self.assertEquals(person.getCareerStartDate()               , default_career.getStartDate())
    self.assertEquals(person.getCareerSalaryCoefficient()       , default_career.getSalaryCoefficient())
    self.assertEquals(person.getCareerCollectiveAgreementTitle(), default_career.getCollectiveAgreementTitle())

    self.assertEquals(person.getCareerRole()     , default_career.getRole())
    self.assertEquals(person.getCareerRoleTitle(), default_career.getRoleTitle())
    self.assertEquals(person.getCareerRoleValue(), default_career.getRoleValue())

    self.assertEquals(person.getCareerGrade()     , default_career.getGrade())
    self.assertEquals(person.getCareerGradeTitle(), default_career.getGradeTitle())
    self.assertEquals(person.getCareerGradeValue(), default_career.getGradeValue())
    
    self.assertEquals(person.getCareerActivity(),
                      default_career.getActivity())
    self.assertEquals(person.getCareerActivityTitle(),
                      default_career.getActivityTitle())
    self.assertEquals(person.getCareerActivityValue(),
                      default_career.getActivityValue())

    self.assertEquals(person.getCareerSalaryLevel()     , default_career.getSalaryLevel())
    self.assertEquals(person.getCareerSalaryLevelTitle(), default_career.getSalaryLevelTitle())
    self.assertEquals(person.getCareerSalaryLevelValue(), default_career.getSalaryLevelValue())

    self.assertEquals(person.getCareerSkillList()     , default_career.getSkillList())
    self.assertEquals(person.getCareerSkillTitleList(), default_career.getSkillTitleList())
    self.assertEquals(person.getCareerSkillValueList(), default_career.getSkillValueList())

    self.assertEquals(person.getCareerSubordination(), default_career.getSubordination())
    # Person's subordination is acquired from default career
    self.assertEquals(person.getSubordination(), default_career.getSubordination())
    
  def stepAddCareerStepInAnotherOrganisation(self, sequence=None, **kw) :
    """Adds another career step on the person."""
    person = sequence.get('person')
    other_organisation = self.getOrganisationModule().newContent(
                            portal_type = 'Organisation',
                            title = 'Another Organistion')
    new_career_title = 'new career title'
    # Create a new career step.
    person.Person_shiftDefaultCareer()
    self.assertEquals( 2,
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
    self.assertEquals( old_career_step.getSubordination(),
                       old_organisation.getRelativeUrl() )
    self.assertEquals( old_career_step.getSubordinationTitle(),
                       old_organisation_title )
  
    self.assert_( "subordination/%s" % new_organisation.getRelativeUrl() in
                    new_career_step.getCategoryList(),
                '%s not in %s' % (new_organisation.getRelativeUrl(),
                                  new_career_step.getCategoryList()))
    self.assertEquals( new_career_step.getSubordination(),
                       new_organisation.getRelativeUrl() )
    self.assertEquals( new_career_step.getSubordinationTitle(),
                       new_organisation_title )

  def stepCheckChangePersonAddress(self, sequence=None, **kw) :
    """
    We must make sure that if we change the address of a person,
    then it will not change the address of the organisation.
    """
    person = sequence.get('person')
    organisation = sequence.get('organisation')
    self.assertEquals(organisation.getDefaultAddressCity(),'Lille')
    self.assertEquals(organisation.getDefaultAddressZipCode(), '59000')
    self.assertEquals(person.getDefaultAddressCity(),'Lille')
    self.assertEquals(person.getDefaultAddressZipCode(), '59000')

    # here, the parameters we pass to edit are the same as the one acquired
    # from the organisation, edit shouldn't do anything
    person.edit(
        default_address_city='Lille',
        default_address_zip_code='59000')

    self.assertEquals(person.getDefaultAddress(),
        organisation.getDefaultAddress())
    self.assertEquals(person.getDefaultAddressCity(),'Lille')
    self.assertEquals(person.getDefaultAddressZipCode(), '59000')

    # here, the first parameter we pass will trigger the creation of a
    # subobject on person, and we need to make sure that the second one gets
    # copied (when calling edit from the interface, all displayed fields are
    # passed to edit)
    person.edit(
        default_address_city='La Garnache',
        default_address_zip_code='59000')

    self.assertNotEquals(person.getDefaultAddress(),
        organisation.getDefaultAddress())
    self.assertEquals(person.getDefaultAddressCity(),'La Garnache')
    self.assertEquals(person.getDefaultAddressZipCode(), '59000')
    self.assertEquals(organisation.getDefaultAddressCity(),'Lille')
    self.assertEquals(organisation.getDefaultAddressZipCode(), '59000')

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
    self.assertEquals(person.getDefaultAddressCity(),'Lille')
    self.assertEquals(person.getDefaultAddressZipCode(), '69000')
    self.assertEquals(organisation.getDefaultAddressCity(),'Lille')
    self.assertEquals(organisation.getDefaultAddressZipCode(), '59000')

    # if the address of the person is the same of the organisation
    # there is no reason to create a subobject (default_address)
    person.manage_delObjects(['default_address'])
    person.edit(career_subordination_value=organisation)
    self.assertTrue('default_address' not in person.objectIds())
    self.assertEquals(person.getDefaultAddress(),
        organisation.getDefaultAddress())
    self.assertEquals(person.getDefaultAddressCity(),
        organisation.getDefaultAddressCity())
    self.assertEquals(person.getDefaultAddressZipCode(),
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

  def test_01_Organisation(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test basic behaviour of Organisation.
    """
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepCreateOrganisation'
                , 'stepSetOrganisationCategories'
                , 'stepResetOrganisationCategories'
                , 'stepSetOrganisationAddress'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


  def test_02_Person(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test basic behaviour of Person.
    """
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepCreatePerson'
                , 'stepCreateOrganisation'
                , 'stepSetPersonCareer'
                , 'stepCheckPersonCareer'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_03_Subordination(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Tests that career steps subordination properties behave correctly
    """
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepCreatePerson'
                , 'stepCreateOrganisation'
                , 'stepSetPersonCareer'
                , 'stepAddCareerStepInAnotherOrganisation'
                , 'stepCheckCareerSubordination'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_04_SubordinationAndAddress(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Tests that career steps subordination properties behave correctly
    """
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepCreatePerson'
                , 'stepCreateOrganisation'
                , 'stepSetOrganisationAddress'
                , 'stepSetPersonCareer'
                , 'stepCheckChangePersonAddress'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

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
    self.assertEquals(portal_categories.role.client,
                      person.getRoleValue())
    self.assertEquals(portal_categories.activity.software,
                      person.getActivityValue())
    self.assertEquals(portal_categories.group.nexedi,
                      person.getGroupValue())


  # Dates
  def test_05_DatesOnPerson(self, quiet=QUIET, run=RUN_ALL_TEST):
    """Tests dates on Person objects.
    """
    pers = self.getPersonModule().newContent(portal_type='Person')
    birthday = DateTime(1999, 01, 01)
    now = DateTime()
    pers.edit(birthday = birthday)
    self.assertEquals(birthday, pers.getBirthday())
    self.assertEquals(birthday, pers.getStartDate())
    
    for slot in ['year', 'month', 'day', 'hour', 'minute']:
      self.assertEquals(getattr(now, slot)(),
                        getattr(pers.getCreationDate(), slot)(),
                        'Wrong creation date %s' % pers.getCreationDate())
  
  def test_06_DatesOnOrganisation(self, quiet=QUIET, run=RUN_ALL_TEST):
    """Tests dates on Organisation objects.
    """
    org = self.getOrganisationModule().newContent(portal_type='Organisation')
    start_date = DateTime(1999, 01, 01)
    now = DateTime()
    org.edit(start_date = start_date)
    self.assertEquals(start_date, org.getStartDate())
    
    for slot in ['year', 'month', 'day', 'hour', 'minute']:
      self.assertEquals(getattr(now, slot)(),
                        getattr(org.getCreationDate(), slot)(),
                        'Wrong creation date %s' % org.getCreationDate())

  def test_07_BirthplaceOnPerson(self, quiet=QUIET, run=RUN_ALL_TEST):
    """Tests birthplace on Person objects.
    """
    pers = self.getPersonModule().newContent(portal_type='Person')
    pers.setDefaultBirthplaceAddressCity('Lille')
    self.assertEquals('Lille', pers.getDefaultBirthplaceAddressCity())

  def test_getTranslatedId(self):
    pers = self.getPersonModule().newContent(
                portal_type='Person', id='default_email')
    self.assertEquals(None, pers.getTranslatedId())
    pers.setDefaultEmailText('nobody@example.com')
    email = pers.getDefaultEmailValue()
    self.assertEquals('Default Email', str(email.getTranslatedId()))
    
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
    self.assertEquals([['', ''], ['Function Node', 'function_node']],
      organisation.Organisation_view.my_function.get_value('items'))
    
    # on Person_view, the user select leaves for functions:
    field = person.Person_view.my_career_function
    self.assertTrue('function_node' not in [x[1] for x in
                          field.get_value('items')])
    self.assertTrue('function_node/function_leave' in [x[1] for x in
                          field.get_value('items')])
    # person acquire function from the organisation
    self.assertEquals(person.getFunctionValue(), function_node)
    # but the user interface does not show the acquired value in this case
    self.assertEquals('', field.get_value('default'))
    # (the field is working)
    person.setDefaultCareerFunctionValue(function_leave)
    self.assertEquals(person.getFunctionValue(), function_leave)
    self.assertEquals('function_node/function_leave',
                      field.get_value('default'))


  def test_CreateBankAccount(self):
    # We can add Bank Accounts inside Persons and Organisation
    for entity in (self.getPersonModule().newContent(portal_type='Person'),
        self.getOrganisationModule().newContent(portal_type='Organisation')):
      bank_account = entity.newContent(portal_type='Bank Account')
      self.assertEquals([], bank_account.checkConsistency())
      bank_account.newContent(portal_type='Agent')
      self.assertEquals([], bank_account.checkConsistency())
      self.portal.portal_workflow.doActionFor(bank_account, 'validate_action')
      self.assertEquals('validated', bank_account.getValidationState())

  def test_CreateImage(self):
    # We can add Images inside Persons and Organisation
    for entity in (self.getPersonModule().newContent(portal_type='Person'),
        self.getOrganisationModule().newContent(portal_type='Organisation')):
      image = entity.newContent(portal_type='Embedded File')
      self.assertEquals([], image.checkConsistency())
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
    self.assertEquals('image/jpeg', image_type)
    # magic
    self.assertEquals('\xff', image_data[0])
    self.assertEquals('\xd8', image_data[1])

  def test_ImageSize(self):
    image = self.portal.newContent(portal_type='Image', id='test_image')
    image.edit(file=self.makeImageFileUpload('erp5_logo.png'))
    self.assertEquals(320, image.getWidth())
    self.assertEquals(250, image.getHeight())
    image.edit(file=self.makeImageFileUpload('erp5_logo_small.png'))
    self.assertEquals(160, image.getWidth())
    self.assertEquals(125, image.getHeight())

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
    self.assertEquals(DateTime(2001, 1, 1),
         person.Person_getCareerStartDate(
            subordination_relative_url=first_organisation.getRelativeUrl()))
    self.assertEquals(DateTime(1999, 9, 9),
         person.Person_getCareerStartDate(
            subordination_relative_url=second_organisation.getRelativeUrl()))

    # only validated careers are used (for conveniance, draft careers are
    # accepted as well)
    another_cancelled_career = person.newContent(
                              portal_type='Career',
                              subordination_value=first_organisation,
                              start_date=DateTime(1996, 9, 9))
    another_cancelled_career.cancel()
    self.assertEquals(DateTime(2001, 01, 01),
         person.Person_getCareerStartDate(
            subordination_relative_url=first_organisation.getRelativeUrl()))

  def test_Person_getAge(self):
    person = self.getPersonModule().newContent(
                                  portal_type='Person',
                                  start_date=DateTime(2001, 2, 3))

    self.assertEquals(1,
          person.Person_getAge(year=1, at_date=DateTime(2002, 2, 4)))
    self.assertTrue(person.Person_getAge(year=1) > 5)

    # if year is not passed, the script returns the age in a translated string.
    age_as_text = person.Person_getAge(at_date=DateTime(2002, 2, 4))
    self.assertEquals(age_as_text, "1 years old")

  def test_AssignmentWorkflow(self):
    person = self.getPersonModule().newContent(portal_type='Person',)
    assignment = person.newContent(portal_type='Assignment')
    self.assertEquals('draft', assignment.getValidationState())
    self.portal.portal_workflow.doActionFor(assignment, 'open_action')
    self.assertEquals('open', assignment.getValidationState())
    self.portal.portal_workflow.doActionFor(assignment, 'update_action')
    self.assertEquals('updated', assignment.getValidationState())
    self.portal.portal_workflow.doActionFor(assignment, 'open_action')
    self.assertEquals('open', assignment.getValidationState())
    # date is set automatically when closing
    self.assertEquals(None, assignment.getStopDate())
    self.portal.portal_workflow.doActionFor(assignment, 'close_action')
    self.assertEquals('closed', assignment.getValidationState())
    self.assertNotEquals(None, assignment.getStopDate())
    self.assertEquals(DateTime().day(), assignment.getStopDate().day())

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
    transaction.commit()
    self.tic()
    relative_url_list = sum((x.detail.split('\n')
                             for x in active_process.getResultList()), [])

    self.assertEquals(len(relative_url_list), len(set(relative_url_list)))
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
    transaction.commit()
    self.tic()

    # patch the method, we'll abort later
    self.portal.Localizer.get_selected_language = lambda: lang

    self.assertEquals(set([person_1, person_2]),
        set([x.getObject() for x in
          self.portal.portal_catalog(translated_portal_type='Personne')]))
    self.assertEquals(set([person_2, organisation]),
        set([x.getObject() for x in
          self.portal.portal_catalog(translated_validation_state_title='Brouillon',
                                     portal_type=('Person', 'Organisation'))]))
    self.assertEquals([person_2],
        [x.getObject() for x in
          self.portal.portal_catalog(translated_validation_state_title='Brouillon',
                                     translated_portal_type='Personne')])
    transaction.abort()

  def test_Base_createCloneDocument(self):
    module = self.portal.person_module
    module.manage_permission('Add portal content', ['Member'], 0)
    self.login_as_auditor()
    person = module.newContent(portal_type='Person',)
    self.assertEquals(1, len(module))
    person.Base_createCloneDocument()
    self.assertEquals(2, len(module))

  def test_Base_createCloneDocument_document_in_document(self):
    module = self.portal.person_module
    module.manage_permission('Add portal content', ['Member'], 0)
    self.login_as_auditor()
    person = module.newContent(portal_type='Person',)
    # An address is a document, it cannot contain anything
    address = person.newContent(portal_type='Address')
    self.assertEquals(0, len(address.allowedContentTypes()))

    self.assertEquals(1, len(person))
    address.Base_createCloneDocument()
    self.assertEquals(2, len(person))

  def test_Base_createCloneDocument_folder_in_document(self):
    module = self.portal.person_module
    module.manage_permission('Add portal content', ['Member'], 0)
    self.login_as_auditor()
    person = module.newContent(portal_type='Person',)
    bank_account = person.newContent(portal_type='Bank Account')
    # A bank account is a folder, it can contain other documents
    self.assertNotEquals(0, len(bank_account.allowedContentTypes()))

    self.assertEquals(1, len(person))
    bank_account.Base_createCloneDocument()
    self.assertEquals(2, len(person))

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
                                   group='nexedi')
    self.assertNotEquals(None, assignment.getGroupValue())
    assignment.open()
    self.portal.portal_workflow.doActionFor(person, 'create_user_action',
                  reference='user_login',
                  password='pass',
                  password_confirm='pass')
    transaction.commit()
    self.tic()

    # a user is created
    user = self.portal.acl_users.getUserById('user_login')
    self.assertNotEquals(None, user)

    # and this user has a preference created
    newSecurityManager(None, user.__of__(self.portal.acl_users))
    self.assertNotEquals(None,
        self.portal.portal_catalog.getResultValue(portal_type='Preference',
                                                  owner='user_login'))
    # for his assignent group
    self.assertEquals('group/nexedi',
        self.portal.portal_preferences.getPreferredSectionCategory())

  # Marked as expectedFailure as it shall be never possible to use edit method to set
  # local property which would override existing method
  @expectedFailure
  def test_content_type_property(self):
    portal_type = 'Person'
    person_module = self.portal.getDefaultModule(portal_type)
    person = person_module.newContent(portal_type=portal_type)

    # assert that test has a sense
    self.assertEqual(getattr(person, 'getContentType', None), None)

    # edit content_type on document which has no content_type property configured
    person.edit(content_type='text/xml')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Base))
  return suite
