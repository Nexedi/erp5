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


from Products.ERP5.Document.Person import Person
from Products.ERP5.Document.Organisation import Organisation



class TestHR(ERP5TypeTestCase):
  """
    ERP5 Human Ressources related tests. Actually every HR related features are
    in Person and Organisation module, packaged in the erp5_core business
    template.
  """

  # pseudo constants
  RUN_ALL_TEST = 1
  QUIET = 0



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
    return ()


  def afterSetUp(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Initialize the ERP5 site.
    """
    self.login()
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
      Create an organisation
    """
    portal_type = 'Organisation'
    organisation_module = self.portal.getDefaultModule(portal_type)
    self.organisation = organisation_module.newContent( portal_type       = portal_type
                                                      , immediate_reindex = 1
                                                      )


  def stepSetOrganisationCategories(self, sequence=None, sequence_list=None, **kw):
    """
      Set & Check default organisation categories (function, activity, site, group...)
    """
    # Set & Check function
    function_categories = self.getCategoryList(base_category='function')
    function_path   = function_categories[0]['path']
    function_title  = function_categories[0]['title']
    function_object = self.portal_categories.resolveCategory(function_path)
    self.organisation.setFunction(function_path)
    self.assertEquals(self.organisation.getFunction()     , function_path)
    self.assertEquals(self.organisation.getFunctionTitle(), function_title)
    self.assertEquals(self.organisation.getFunctionValue(), function_object)
    # Set & Check activity
    activity_categories = self.getCategoryList(base_category='activity')
    activity_path   = activity_categories[0]['path']
    activity_title  = activity_categories[0]['title']
    activity_object = self.portal_categories.resolveCategory(activity_path)
    self.organisation.setActivity(activity_path)
    self.assertEquals(self.organisation.getActivity()     , activity_path)
    self.assertEquals(self.organisation.getActivityTitle(), activity_title)
    self.assertEquals(self.organisation.getActivityValue(), activity_object)
    # Set & Check group
    group_categories = self.getCategoryList(base_category='group')
    group_path   = group_categories[0]['path']
    group_title  = group_categories[0]['title']
    group_object = self.portal_categories.resolveCategory(group_path)
    self.organisation.setGroup(group_path)
    self.assertEquals(self.organisation.getGroup()     , group_path)
    self.assertEquals(self.organisation.getGroupTitle(), group_title)
    self.assertEquals(self.organisation.getGroupValue(), group_object)
    # Set & Check role
    role_categories = self.getCategoryList(base_category='role')
    role_path   = role_categories[0]['path']
    role_title  = role_categories[0]['title']
    role_object = self.portal_categories.resolveCategory(role_path)
    self.organisation.setRole(role_path)
    self.assertEquals(self.organisation.getRole()     , role_path)
    self.assertEquals(self.organisation.getRoleTitle(), role_title)
    self.assertEquals(self.organisation.getRoleValue(), role_object)
    # Set & Check site
    site_categories = self.getCategoryList(base_category='site')
    site_path   = site_categories[0]['path']
    site_title  = site_categories[0]['title']
    site_object = self.portal_categories.resolveCategory(site_path)
    self.organisation.setSite(site_path)
    self.assertEquals(self.organisation.getSite()     , site_path)
    self.assertEquals(self.organisation.getSiteTitle(), site_title)
    self.assertEquals(self.organisation.getSiteValue(), site_object)
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
    self.organisation.setSkillList(skill_path_list)
    self.assertEquals(self.organisation.getSkillList()     , skill_path_list)
    self.assertEquals(self.organisation.getSkillTitleList(), skill_title_list)
    self.assertEquals(self.organisation.getSkillValueList(), skill_object_list)


  def stepResetOrganisationCategories(self, sequence=None, sequence_list=None, **kw):
    """
      Reset default organisation categories (function, activity, site, group...)
    """
    self.organisation.setFunction(None)
    self.organisation.setActivity(None)
    self.organisation.setGroup(None)
    self.organisation.setRole(None)
    self.organisation.setSite(None)
    self.organisation.setSkillList(None)
    self.assertEquals(self.organisation.getFunction() , None)
    self.assertEquals(self.organisation.getActivity() , None)
    self.assertEquals(self.organisation.getGroup()    , None)
    self.assertEquals(self.organisation.getRole()     , None)
    self.assertEquals(self.organisation.getSite()     , None)
    self.assertEquals(self.organisation.getSkillList(), [])
    self.assertEquals(self.organisation.getFunctionTitle() , None)
    self.assertEquals(self.organisation.getActivityTitle() , None)
    self.assertEquals(self.organisation.getGroupTitle()    , None)
    self.assertEquals(self.organisation.getRoleTitle()     , None)
    self.assertEquals(self.organisation.getSiteTitle()     , None)
    self.assertEquals(self.organisation.getSkillTitleList(), [])
    self.assertEquals(self.organisation.getFunctionValue() , None)
    self.assertEquals(self.organisation.getActivityValue() , None)
    self.assertEquals(self.organisation.getGroupValue()    , None)
    self.assertEquals(self.organisation.getRoleValue()     , None)
    self.assertEquals(self.organisation.getSiteValue()     , None)
    self.assertEquals(self.organisation.getSkillValueList(), [])



  ##################################
  ##  Tests
  ##################################

  def test_01_Organisation_basic_categories(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test basic categories on Organisation
    """
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'CreateOrganisation'
                , 'SetOrganisationCategories'
                , 'ResetOrganisationCategories'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)



if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHR))
    return suite
