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
from zLOG import LOG
from Testing import ZopeTestCase
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from AccessControl.SecurityManagement import newSecurityManager


if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'



class TestHR(ERP5TypeTestCase):
  """
    ERP5 Human Ressources related tests. 
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
    return "ERP5 HR"


  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_base',)


  def afterSetUp(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Initialize the ERP5 site.
    """
    self.login()
    self.datetime          = DateTime()
    self.portal            = self.getPortal()
    self.portal_categories = self.getCategoryTool()
    self.portal_catalog    = self.getCatalogTool()
    self.createCategories()



  ##################################
  ##  Usefull methods
  ##################################

  def login(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Create a new manager user and login.
    """
    user_name = 'kevin'
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser(user_name, '', ['Manager', 'Owner', 'Assignor'], [])
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
                                    , immediate_reindex = 1
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
                                                  immediate_reindex=1,
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
    self.failIfDifferentSet(organisation.getSkillList()     , skill_path_list)
    self.failIfDifferentSet(organisation.getSkillTitleList(), skill_title_list)
    self.failIfDifferentSet(organisation.getSkillValueList(), skill_object_list)


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
    self.failIfDifferentSet(organisation.getSkillList(), [])

    self.assertEquals(organisation.getFunctionTitle()       , None)
    self.assertEquals(organisation.getActivityTitle()       , None)
    self.assertEquals(organisation.getGroupTitle()          , None)
    self.assertEquals(organisation.getRoleTitle()           , None)
    self.assertEquals(organisation.getSiteTitle()           , None)
    self.failIfDifferentSet(organisation.getSkillTitleList(), [])

    self.assertEquals(organisation.getFunctionValue()       , None)
    self.assertEquals(organisation.getActivityValue()       , None)
    self.assertEquals(organisation.getGroupValue()          , None)
    self.assertEquals(organisation.getRoleValue()           , None)
    self.assertEquals(organisation.getSiteValue()           , None)
    self.failIfDifferentSet(organisation.getSkillValueList(), [])


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
#     self.assertEquals( organisation.getDefaultAddressRegionTitle() # XXX Why ?
#                      , default_address.getRegionTitle()
#                      )
#     self.assertEquals( organisation.getDefaultAddressRegionValue()
#                      , region_object
#                      )
#     self.assertEquals( default_address.getRegionValue()
#                      , region_object
#                      )
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
                                     , immediate_reindex = 1
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
    self.assertEquals(person.getCareerStopDate()                , dummy_date2)
    self.assertEquals(person.getCareerStartDate()               , dummy_date1)
    self.assertEquals(person.getCareerSalaryCoefficient()       , 1)
    self.assertEquals(person.getCareerCollectiveAgreementTitle(), 'SYNTEC convention')

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
    self.failIfDifferentSet(person.getCareerSkillList()     , skill_path_list)
    self.failIfDifferentSet(person.getCareerSkillTitleList(), skill_title_list)
    self.failIfDifferentSet(person.getCareerSkillValueList(), skill_object_list)
    # skill must be acquired on person 
    person.reindexObject(); get_transaction().commit(); self.tic()
    for skill_object in skill_object_list:
      self.failUnless(person in skill_object.getSkillRelatedValueList())

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

    self.assertEquals(person.getCareerSalaryLevel()     , default_career.getSalaryLevel())
    self.assertEquals(person.getCareerSalaryLevelTitle(), default_career.getSalaryLevelTitle())
    self.assertEquals(person.getCareerSalaryLevelValue(), default_career.getSalaryLevelValue())

    self.failIfDifferentSet(person.getCareerSkillList()     , default_career.getSkillList())
    self.failIfDifferentSet(person.getCareerSkillTitleList(), default_career.getSkillTitleList())
    self.failIfDifferentSet(person.getCareerSkillValueList(), default_career.getSkillValueList())

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

if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHR))
    return suite
