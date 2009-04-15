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
    # self.login_as_member()

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

  def login_as_member(self):
    """Create a new member user and login.
    """
    user_name = 'member_user'
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser(user_name, '', ['Member', 'Author', 'Assignor'], [])
    user = user_folder.getUserById(user_name).__of__(user_folder)
    newSecurityManager(None, user)

  def createCategories(self):
    """
      Create some categories for testing.
    """
    self.category_list = [
                         # Grade categories
                           {'path' : 'grade/director'
                           ,'title': 'Director'
                           }
                         , {'path' : 'grade/engineer'
                           ,'title': 'Engineer'
                           }

                         # Function categories
                         , {'path' : 'function/hq'
                           ,'title': 'Headquarters'
                           }
                         , {'path' : 'function/warehouse'
                           ,'title': 'Warehouse'
                           }
                         , {'path' : 'function/research_center'
                           ,'title': 'Research Center'
                           }

                         # Activity categories
                         , {'path' : 'activity/media'
                           ,'title': 'Media'
                           }
                         , {'path' : 'activity/software'
                           ,'title': 'Software'
                           }
                         , {'path' : 'activity/mechanics'
                           ,'title': 'Mechanics'
                           }
                         , {'path' : 'activity/mechanics/aerospace'
                           ,'title': 'Aerospace'
                           }
                         , {'path' : 'activity/mechanics/automotive'
                           ,'title': 'Automotive'
                           }

                         # Group categories
                         , {'path' : 'group/nexedi'
                           ,'title': 'Nexedi'
                           }
                         , {'path' : 'group/nexedi/storever'
                           ,'title': 'Storever'
                           }
                         , {'path' : 'group/nexedi/rentalinux'
                           ,'title': 'Rentalinux'
                           }

                         # Role categories
                         , {'path' : 'role/client'
                           ,'title': 'Client'
                           }
                         , {'path' : 'role/supplier'
                           ,'title': 'Supplier'
                           }
                         , {'path' : 'role/internal'
                           ,'title': 'Internal'
                           }

                         # Site categories
                         , {'path' : 'site/production/madrid'
                           ,'title': 'Madrid Production Site'
                           }
                         , {'path' : 'site/distibution/paris'
                           ,'title': 'Paris Distribution Site'
                           }
                         , {'path' : 'site/distibution/tokyo'
                           ,'title': 'Tokyo Distribution Site'
                           }
                         , {'path' : 'site/distibution/new_york'
                           ,'title': 'New York Distribution Site'
                           }

                         # Skill categories
                         , {'path' : 'skill/design/graphic'
                           ,'title': 'Graphic'
                           }
                         , {'path' : 'skill/design/sound'
                           ,'title': 'Sound'
                           }
                         , {'path' : 'skill/it/consulting'
                           ,'title': 'Consulting'
                           }
                         , {'path' : 'skill/it/programming'
                           ,'title': 'Programming'
                           }

                         # Region categories
                         , {'path' : 'region/europe/france'
                           ,'title': 'France'
                           }
                         , {'path' : 'region/europe/germany'
                           ,'title': 'Germany'
                           }
                         , {'path' : 'region/america/canada'
                           ,'title': 'Canada'
                           }
                         , {'path' : 'region/america/brazil'
                           ,'title': 'Brazil'
                           }

                         # Salary Level categories
                         , {'path' : 'salary_level/france/1/A'
                           ,'title': '1.A'
                           }
                         , {'path' : 'salary_level/france/1/B'
                           ,'title': '1.B'
                           }
                         , {'path' : 'salary_level/france/1/C'
                           ,'title': '1.C'
                           }
                         , {'path' : 'salary_level/france/2'
                           ,'title': '2'
                           }
                         ]

    # Create categories
    # Note : this code was taken from the CategoryTool_importCategoryFile python
    #        script (packaged in erp5_core).
    for category in self.category_list:
      keys = category.keys()
      if 'path' in keys:
        base_path_obj = self.portal_categories
        is_base_category = True
        for category_id in category['path'].split('/'):
          # The current category is not existing
          if category_id not in base_path_obj.contentIds():
            # Create the category
            if is_base_category:
              category_type = 'Base Category'
            else:
              category_type = 'Category'
            base_path_obj.newContent( portal_type       = category_type
                                    , id                = category_id
                                    )
          base_path_obj = base_path_obj[category_id]
          is_base_category = False
        new_category = base_path_obj

        # Set the category properties
        for key in keys:
          if key != 'path':
            method_id = "set" + convertToUpperCase(key)
            value = category[key]
            if value not in ('', None):
              if hasattr(new_category, method_id):
                method = getattr(new_category, method_id)
                method(value.encode('UTF-8'))


  def getCategoryList(self, base_category=None):
    """
      Get a list of categories with same base categories.
    """
    categories = []
    if base_category != None:
      for category in self.category_list:
        if category["path"].split('/')[0] == base_category:
          categories.append(category)
    return categories



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

    # Set & Check function
    function_categories = self.getCategoryList(base_category='function')
    function_path   = function_categories[0]['path']
    function_title  = function_categories[0]['title']
    function_object = self.portal_categories.resolveCategory(function_path)
    organisation.setFunction(function_path)
    self.assertEquals(organisation.getFunction()     , function_path)
    self.assertEquals(organisation.getFunctionTitle(), function_title)
    self.assertEquals(organisation.getFunctionValue(), function_object)

    # Set & Check activity
    activity_categories = self.getCategoryList(base_category='activity')
    activity_path   = activity_categories[0]['path']
    activity_title  = activity_categories[0]['title']
    activity_object = self.portal_categories.resolveCategory(activity_path)
    organisation.setActivity(activity_path)
    self.assertEquals(organisation.getActivity()     , activity_path)
    self.assertEquals(organisation.getActivityTitle(), activity_title)
    self.assertEquals(organisation.getActivityValue(), activity_object)

    # Set & Check group
    group_categories = self.getCategoryList(base_category='group')
    group_path   = group_categories[0]['path']
    group_title  = group_categories[0]['title']
    group_object = self.portal_categories.resolveCategory(group_path)
    organisation.setGroup(group_path)
    self.assertEquals(organisation.getGroup()     , group_path)
    self.assertEquals(organisation.getGroupTitle(), group_title)
    self.assertEquals(organisation.getGroupValue(), group_object)

    # Set & Check role
    role_categories = self.getCategoryList(base_category='role')
    role_path   = role_categories[0]['path']
    role_title  = role_categories[0]['title']
    role_object = self.portal_categories.resolveCategory(role_path)
    organisation.setRole(role_path)
    self.assertEquals(organisation.getRole()     , role_path)
    self.assertEquals(organisation.getRoleTitle(), role_title)
    self.assertEquals(organisation.getRoleValue(), role_object)

    # Set & Check site
    site_categories = self.getCategoryList(base_category='site')
    site_path   = site_categories[0]['path']
    site_title  = site_categories[0]['title']
    site_object = self.portal_categories.resolveCategory(site_path)
    organisation.setSite(site_path)
    self.assertEquals(organisation.getSite()     , site_path)
    self.assertEquals(organisation.getSiteTitle(), site_title)
    self.assertEquals(organisation.getSiteValue(), site_object)

    # Set & Check skills
    skill_categories = self.getCategoryList(base_category='skill')
    skill_path_list   = []
    skill_title_list  = []
    skill_object_list = []
    for skill in skill_categories[:2]:
      skill_path   = skill['path']
      skill_title  = skill['title']
      skill_object = self.portal_categories.resolveCategory(skill_path)
      skill_path_list.append(skill_path)
      skill_title_list.append(skill_title)
      skill_object_list.append(skill_object)
    organisation.setSkillList(skill_path_list)
    self.assertEquals(organisation.getSkillList()     , skill_path_list)
    self.assertEquals(organisation.getSkillTitleList(), skill_title_list)
    self.assertEquals(organisation.getSkillValueList(), skill_object_list)


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

    region = self.getCategoryList(base_category='region')[0]
    region_path   = region["path"]
    region_title  = region["title"]
    region_object = self.portal_categories.resolveCategory(region_path)
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

    # Set & Check function
    function_categories = self.getCategoryList(base_category='function')
    function_path   = function_categories[1]['path']
    function_title  = function_categories[1]['title']
    function_object = self.portal_categories.resolveCategory(function_path)
    person.setCareerFunction(function_path)
    self.assertEquals(person.getCareerFunction()     , function_path)
    self.assertEquals(person.getCareerFunctionTitle(), function_title)
    self.assertEquals(person.getCareerFunctionValue(), function_object)
    # function must be acquired on person
    person.reindexObject(); get_transaction().commit(); self.tic()
    self.failUnless(person in function_object.getFunctionRelatedValueList())

    # Set & Check role
    role_categories = self.getCategoryList(base_category='role')
    role_path   = role_categories[1]['path']
    role_title  = role_categories[1]['title']
    role_object = self.portal_categories.resolveCategory(role_path)
    person.setCareerRole(role_path)
    self.assertEquals(person.getCareerRole()     , role_path)
    self.assertEquals(person.getCareerRoleTitle(), role_title)
    self.assertEquals(person.getCareerRoleValue(), role_object)
    # role must be acquired on person
    person.reindexObject(); get_transaction().commit(); self.tic()
    self.failUnless(person in role_object.getRoleRelatedValueList())

    # Set & Check grade
    grade_categories = self.getCategoryList(base_category='grade')
    grade_path   = grade_categories[1]['path']
    grade_title  = grade_categories[1]['title']
    grade_object = self.portal_categories.resolveCategory(grade_path)
    person.setCareerGrade(grade_path)
    self.assertEquals(person.getCareerGrade()     , grade_path)
    self.assertEquals(person.getCareerGradeTitle(), grade_title)
    self.assertEquals(person.getCareerGradeValue(), grade_object)
    # grade must be acquired on person 
    person.reindexObject(); get_transaction().commit(); self.tic()
    self.failUnless(person in grade_object.getGradeRelatedValueList())

    # Set & Check salary level
    salary_level_categories = self.getCategoryList(
                                base_category='salary_level')
    salary_level_path   = salary_level_categories[1]['path']
    salary_level_title  = salary_level_categories[1]['title']
    salary_level_object = self.portal_categories.resolveCategory(
                          salary_level_path)
    person.setCareerSalaryLevel(salary_level_path)
    self.assertEquals(person.getCareerSalaryLevel()     , salary_level_path)
    self.assertEquals(person.getCareerSalaryLevelTitle(), salary_level_title)
    self.assertEquals(person.getCareerSalaryLevelValue(), salary_level_object)
    # salary_level must be acquired on person 
    person.reindexObject(); get_transaction().commit(); self.tic()
    self.failUnless(person in
                   salary_level_object.getSalaryLevelRelatedValueList())

    # Set & Check skills
    skill_categories = self.getCategoryList(base_category='skill')
    skill_path_list   = []
    skill_title_list  = []
    skill_object_list = []
    for skill in skill_categories[1:3]:
      skill_path   = skill['path']
      skill_title  = skill['title']
      skill_object = self.portal_categories.resolveCategory(skill_path)
      skill_path_list.append(skill_path)
      skill_title_list.append(skill_title)
      skill_object_list.append(skill_object)
    person.setCareerSkillList(skill_path_list)
    self.assertEquals(person.getCareerSkillList()     , skill_path_list)
    self.assertEquals(person.getCareerSkillTitleList(), skill_title_list)
    self.assertEquals(person.getCareerSkillValueList(), skill_object_list)
    self.assertEquals(person.getCareerSkillTitle(), skill_title_list[0])
    self.assertEquals(person.getCareerSkillValue(), skill_object_list[0])
    # skill must be acquired on person 
    person.reindexObject(); get_transaction().commit(); self.tic()
    for skill_object in skill_object_list:
      self.failUnless(person in skill_object.getSkillRelatedValueList())
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

  def test_TelephoneAsText(self):
    # Test asText method
    pers = self.getPersonModule().newContent(portal_type='Person')
    tel = pers.newContent(portal_type='Telephone')
    tel.setTelephoneCountry(33)
    tel.setTelephoneArea(2)
    tel.setTelephoneNumber(12345678)
    tel.setTelephoneExtension(999)
    self.assertEquals('+33(0)2-12345678/999', tel.asText())

  def test_TelephonePreference(self):
    pers = self.getPersonModule().newContent(portal_type='Person')
    tel = pers.newContent(portal_type='Telephone')
    pref = self.portal_preferences.default_site_preference
    pref.setPreferredTelephoneDefaultCountryNumber('33')
    pref.setPreferredTelephoneDefaultAreaNumber('2')
    pref.enable()
    tel.fromText(coordinate_text='11111111')
    self.assertEquals('+33(0)2-11111111',tel.asText())

  def test_TelephoneCountryAndAreaCodeRemains(self):
    pers = self.getPersonModule().newContent(portal_type='Person')
    tel = pers.newContent(portal_type='Telephone')
    pref = self.portal_preferences.default_site_preference
    pref.setPreferredTelephoneDefaultCountryNumber('')
    pref.setPreferredTelephoneDefaultAreaNumber('')
    pref.enable()
    tel.fromText(coordinate_text='+11 1 11111111')
    tel.fromText(coordinate_text='+22333445555')
    self.assertEquals('+(0)-22333445555',tel.asText())

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
      self.assertEquals(i[1],tel.asText())

  def test_TelephoneWhenTheDefaultCountryAndAreaPreferenceIsBlank(self):
    pers = self.getPersonModule().newContent(portal_type='Person')
    tel = pers.newContent(portal_type='Telephone')
    pref = self.portal_preferences.default_site_preference
    pref.setPreferredTelephoneDefaultCountryNumber('')
    pref.setPreferredTelephoneDefaultAreaNumber('')
    pref.enable()
    tel.fromText(coordinate_text='12345678')
    self.assertEquals('+(0)-12345678',tel.asText())

  def test_TelephoneAsTextBlankNumber(self):
    # Test asText method with blank number
    pers = self.getPersonModule().newContent(portal_type='Person')
    tel = pers.newContent(portal_type='Telephone')
    self.assertEquals('', tel.asText())

  def test_TelephoneUrl(self):
    # http://www.rfc-editor.org/rfc/rfc3966.txt
    pers = self.getPersonModule().newContent(portal_type='Person')
    tel = pers.newContent(portal_type='Telephone')
    tel.setTelephoneCountry(33)
    tel.setTelephoneNumber(123456789)
    self.assertEquals('tel:+33123456789', tel.asURL())
    
    tel.setTelephoneCountry(None)
    tel.setTelephoneNumber(123456789)
    self.assertEquals('tel:0123456789', tel.asURL())


  def test_EmptyTelephoneAsText(self):
    # asText method returns an empty string for empty telephones
    pers = self.getPersonModule().newContent(portal_type='Person')
    self.assertEquals('', pers.newContent(portal_type='Telephone').asText())


  def test_EmptyFaxAsText(self):
    # asText method returns an empty string for empty faxes
    pers = self.getPersonModule().newContent(portal_type='Person')
    self.assertEquals('', pers.newContent(portal_type='Fax').asText())


  def test_EmailAsURL(self):
    # asURL method works on email
    pers = self.getPersonModule().newContent(portal_type='Person')
    pers.setDefaultEmailText('nobody@example.com')
    email = pers.getDefaultEmailValue()
    self.assertEquals('mailto:nobody@example.com', email.asURL())
    self.assertEquals('mailto:nobody@example.com',
                      pers.Entity_getDefaultEmailAsURL())

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
      image = entity.newContent(portal_type='Image')
      self.assertEquals([], image.checkConsistency())
      image.view() # viewing the image does not cause error

  def test_ConvertImage(self):
    image = self.portal.newContent(portal_type='Image', id='test_image')
    image.edit(file=self.makeImageFileUpload('erp5_logo.png'))
    image_type, image_data = image.convert('jpg', display='thumbnail')
    self.assertEquals('image/jpeg', image_type)
    # magic
    self.assertEquals('\xff', image_data[0])
    self.assertEquals('\xd8', image_data[1])
  
  def test_ConvertImageQuality(self):
    image = self.portal.newContent(portal_type='Image', id='test_image')
    image.edit(file=self.makeImageFileUpload('erp5_logo.png'))
    image_type, image_data = image.convert('jpg', display='thumbnail',
                                           quality=100)
    self.assertEquals('image/jpeg', image_type)
    # magic
    self.assertEquals('\xff', image_data[0])
    self.assertEquals('\xd8', image_data[1])
  
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
    test = 'test_ERP5Site_checkDataWithScript'
    createZODBPythonScript(self.getSkinsTool().custom, test, '',
                           'return context.absolute_url(relative=1),')

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
      self.assertTrue(obj.absolute_url(relative=1) in relative_url_list)
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


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Base))
  return suite
