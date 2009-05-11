# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#               Fabien Morin <fabien@nexedi.com
#               Jacek Medrzycki <jacek@erp5.pl>
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
import os
import popen2
import urllib

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from xml.dom import minidom

from glob import glob

try:
  from transaction import get as get_transaction
except ImportError:
  pass

#
# Test Setting
#
INSTANCE_HOME = os.environ['INSTANCE_HOME']
bt5_base_path = os.environ.get('erp5_tests_bt5_path',
                               os.path.join(INSTANCE_HOME, 'bt5'))
bootstrap_base_path = os.path.join(INSTANCE_HOME, 'Products', 'ERP5', 'bootstrap')

# dependency order
target_business_templates = (
  'erp5_base',
  'erp5_trade',

  'erp5_pdf_editor',
  'erp5_pdf_style',
  'erp5_pdm',
  'erp5_accounting',
  'erp5_invoicing',

  'erp5_apparel',

##   'erp5_banking_core',
##   'erp5_banking_cash',
##   'erp5_banking_check',
##   'erp5_banking_inventory',

  'erp5_budget',
  'erp5_public_accounting_budget',

  'erp5_commerce',

  'erp5_consulting',

  'erp5_ingestion',
  'erp5_ingestion_mysql_innodb_catalog',
  'erp5_crm',

  'erp5_web',
  'erp5_dms',

  'erp5_forge',

  'erp5_immobilisation',

  'erp5_item',

  'erp5_mrp',

  'erp5_payroll',

  'erp5_project',

  'erp5_calendar',
)


class TestXHTML(ERP5TypeTestCase):

  run_all_test = 1

  def getTitle(self):
    return "XHTML Test"

  def getBusinessTemplateList(self):
    """  """
    return target_business_templates

  def afterSetUp(self):
    self.portal = self.getPortal()
    self.login()
    self.enableDefaultSitePreference()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def enableDefaultSitePreference(self):
    portal_preferences = getToolByName(self.portal, 'portal_preferences')
    portal_workflow = getToolByName(self.portal, 'portal_workflow')
    default_site_preference = portal_preferences.default_site_preference
    portal_workflow.doActionFor(default_site_preference, 'enable_action')

  def test_deadProxyFields(self):
    # check that all proxy fields defined in business templates have a valid
    # target
    skins_tool = self.portal.portal_skins
    error_list = []
    for field_path, field in skins_tool.ZopeFind(
              skins_tool, obj_metatypes=['ProxyField'], search_sub=1):
      template_field = field.getTemplateField()
      if template_field is None:
        error_list.append((field_path, field.get_value('form_id'),
                           field.get_value('field_id')))
    self.assertEquals(error_list, [])
    
  def test_emptySelectionNameInListbox(self):
    # check all empty selection name in listboxes
    skins_tool = self.portal.portal_skins
    error_list = []
    for form_path, form in skins_tool.ZopeFind(
              skins_tool, obj_metatypes=['ERP5 Form'], search_sub=1):
      try:
       fields = form.get_fields()
      except AttributeError, e:
        print "%s is broken: %s" % (form_path, e)
      for field in fields:
        if field.meta_type =='ListBox':
          selection_name = field.get_value("selection_name")
          if selection_name in ("",None):
            error_list.append(form_path)
    self.assertEquals(error_list, [])

  def test_callableListMethodInListbox(self):
    # check all list_method in listboxes
    skins_tool = self.portal.portal_skins
    error_list = []
    for form_path, form in skins_tool.ZopeFind(
              skins_tool, obj_metatypes=['ERP5 Form'], search_sub=1):
      try:
       fields = form.get_fields()
      except AttributeError, e:
        print "%s is broken: %s" % (form_path, e)
      for field in fields:
        if field.meta_type == 'ListBox':
          list_method = field.get_value("list_method")
          if list_method:
            if isinstance(list_method, str):
              method = getattr(self.portal, list_method)
            else:
              method = list_method
            if not callable(method):
              error_list.append(form_path)
    self.assertEquals(error_list, [])

class W3Validator(object):

  def __init__(self, validator_path, show_warnings):
    self.validator_path = validator_path
    self.show_warnings = show_warnings
    self.name = 'w3c'

  def _parse_validation_results(self, result):
    """
    parses the validation results, returns a list of tuples:
    line_number, col_number, error description
    """
    error_list=[]
    warning_list=[]
    xml_doc = minidom.parseString(result)
    for error in xml_doc.getElementsByTagName('m:error'):
      error_line = error.getElementsByTagName('m:line')[0].firstChild.nodeValue
      error_col = error.getElementsByTagName('m:col')[0].firstChild.nodeValue
      error_message = error.getElementsByTagName('m:message')[0].firstChild.nodeValue
      error_list.append((error_line,error_col,error_message))
    for warning in xml_doc.getElementsByTagName('m:warning'):
      warning_line = warning.getElementsByTagName('m:line')[0].firstChild.nodeValue
      warning_col = warning.getElementsByTagName('m:col')[0].firstChild.nodeValue
      warning_message = warning.getElementsByTagName('m:message')[0].firstChild.nodeValue
      warning_list.append((warning_line, warning_col, warning_message))
    return error_list, warning_list

  def getErrorAndWarningList(self, page_source):
    '''
      retrun two list : a list of errors and an other for warnings
    '''
    source = 'fragment=%s&output=soap12' % urllib.quote_plus(page_source)
    os.environ['CONTENT_LENGTH'] = str(len(source))
    os.environ['REQUEST_METHOD'] = 'POST'
    stdout, stdin, stderr = popen2.popen3(self.validator_path)
    stdin.write(source)
    stdin.close()
    while stdout.readline() != '\n':
      pass
    result = stdout.read()
    return self._parse_validation_results(result)


class TidyValidator(object):

  def __init__(self, validator_path, show_warnings):
    self.validator_path = validator_path
    self.show_warnings = show_warnings
    self.name = 'tidy'

  def _parse_validation_results(self, result):
    """
    parses the validation results, returns a list of tuples:
    line_number, col_number, error description
    """
    error_list=[]
    warning_list=[]

    for i in result:
      data = i.split(' - ')
      if len(data) >= 2:
        data[1] = data[1].replace('\n','')
        if data[1].startswith('Error: '):
          location_list = data[0].split(' ')
          line = location_list[1]
          column = location_list[3]
          error = True
          message = data[1].split(': ')[1]
          error_list.append((line, column, message))
        elif data[1].startswith('Warning: '):
          location_list = data[0].split(' ')
          line = location_list[1]
          column = location_list[3]
          warning = True
          message = data[1].split(': ')[1]
          warning_list.append((line, column, message))
    return (error_list, warning_list)

  def getErrorAndWarningList(self, page_source):
    '''
      retrun two list : a list of errors and an other for warnings
    '''
    stdout, stdin, stderr = popen2.popen3('%s -e -q -utf8' % self.validator_path)
    stdin.write(page_source)
    stdin.close()
    return self._parse_validation_results(stderr)


def validate_xhtml(validator, source, view_name, bt_name):
  '''
    validate_xhtml return True if there is no error on the page, False else.
    Now it's possible to show warnings, so, if the option is set to True on the
    validator object, and there is some warning on the page, the function 
    return False, even if there is no error.
  '''

  # display some information when test faild to facilitate debugging
  message = []
  message.append('Using %s validator to parse the view "%s" (from %s bt) with warning %sdisplayed :' %\
      (validator.name, view_name, bt_name, 
        validator.show_warnings and ' ' or 'NOT '))

  error_list, warning_list = validator.getErrorAndWarningList(source)

  if error_list:
    # build error message
    for error in error_list:
      message.append('Error: line %s column %s : %s' % error)

  if warning_list and validator.show_warnings:
    # build error message
    for warning in warning_list:
      message.append('Warning: line %s column %s : %s' % warning)

  message = '\n'.join(message)
  if validator.show_warnings:
    return ((not (len(error_list) or len(warning_list))), message)
  return ((not len(error_list)), message)


def makeTestMethod(validator, module_id, portal_type, view_name, bt_name):

  def createSubContent(content, portal_type_list):
    if not portal_type_list:
      return content
    if portal_type_list == [content.getPortalType()]:
      return content
    return createSubContent(
               content.newContent(portal_type=portal_type_list[0]),
               portal_type_list[1:])

  def testMethod(self):
    module = getattr(self.portal, module_id)
    portal_type_list = portal_type.split('/')

    object = createSubContent(module, portal_type_list)
    view = getattr(object, view_name)
    self.assert_(*validate_xhtml( validator=validator, 
                                  source=view(), 
                                  view_name=view_name, 
                                  bt_name=bt_name))
  return testMethod

def testPortalTypeViewRecursivly(validator, module_id, business_template_info, 
    business_template_info_list, portal_type_list, portal_type_path_dict, 
    base_path, tested_portal_type_list):
  '''
  This function go on all portal_type recursivly if the portal_type could 
  contain other portal_types and make a test for all view that have action
  '''
  # iteration over all allowed portal_types inside the module/portal_type
  for portal_type in portal_type_list:
    portal_path = portal_type_path_dict[portal_type]
    if portal_type not in tested_portal_type_list:
      # this portal type haven't been tested yet

      backuped_module_id = module_id 
      backuped_business_template_info = business_template_info

      if not business_template_info.actions.has_key(portal_type):
        # search in other bt :
        business_template_info = None
        for bt_info in business_template_info_list:
          if bt_info.actions.has_key(portal_type):
            business_template_info = bt_info
            break
        if not business_template_info:
          LOG("Can't find the action :", 0, portal_type)
          break
        # create the object in portal_trash module
        module_id = 'portal_trash'

      for action_information in business_template_info.actions[portal_type]:
        if (action_information['category'] in ('object_view', 'object_list') and
            action_information['visible']==1 and
            action_information['text'].startswith('string:${object_url}/') and
            len(action_information['text'].split('/'))==2):
          view_name = action_information['text'].split('/')[-1].split('?')[0]
          method = makeTestMethod(validator,
                                  module_id, 
                                  portal_path,
                                  view_name, 
                                  business_template_info.title)
          method_name = 'test.%s.%s.%s' % (business_template_info.title, portal_type, view_name)
          setattr(TestXHTML, method_name, method)
          module_id = backuped_module_id
          business_template_info = backuped_business_template_info

      # add the portal_type to the tested portal_types. This avoid to test many
      # times a Portal Type wich is many bt.
      tested_portal_type_list.append(portal_type)

      new_portal_type_list = business_template_info.allowed_content_types.get(portal_type, ())
      new_portal_type_path_dict = {}

      if base_path != '':
        next_base_path = '%s/%s' % (base_path, portal_type)
      # Module portal_type not to have been added to the path because
      # this portal type object already existing
      elif 'Module' not in portal_type:
        next_base_path = portal_type
      else:
        next_base_path = ''

      for pt in new_portal_type_list:
        if next_base_path != '' and 'Module' not in pt:
          new_portal_type_path_dict[pt] = '%s/%s' % (next_base_path, pt)
        else:
          new_portal_type_path_dict[pt] = pt 
      testPortalTypeViewRecursivly(validator=validator,
                       module_id=module_id, 
                       business_template_info=backuped_business_template_info, 
                       business_template_info_list=business_template_info_list,
                       portal_type_list=new_portal_type_list, 
                       portal_type_path_dict=new_portal_type_path_dict,
                       base_path=next_base_path,
                       tested_portal_type_list=tested_portal_type_list)


def addTestMethodDynamically(validator):
  from Products.ERP5.tests.utils import BusinessTemplateInfoTar
  from Products.ERP5.tests.utils import BusinessTemplateInfoDir
  business_template_info_list = []

  # add erp5_core to the list here but not in the target_business_templates 
  # list to not return it on getBusinessTemplateList call 
  for i in ('erp5_core',) + target_business_templates:
    business_template = os.path.join(bt5_base_path, i)

    # Look for business templates, they can be:
    #  .bt5 files in $INSTANCE_HOME/bt5/
    #  directories in $INSTANCE_HOME/
    #  directories in $INSTANCE_HOME/bt5/*/
    #  directories in $INSTANCE_HOME/Products/ERP5/bootstrap/
    if not ( os.path.exists(business_template) or
        os.path.exists('%s.bt5' % business_template)):
      # try in $INSTANCE_HOME/bt5/*/
      business_template_glob_list = glob('%s/*/%s' % (bt5_base_path, i))
      if business_template_glob_list:
        business_template = business_template_glob_list[0]
      else:
        # try in $INSTANCE_HOME/Products/ERP5/bootstrap
        business_template = os.path.join(bootstrap_base_path,i) 

    if os.path.isdir(business_template):
      business_template_info = BusinessTemplateInfoDir(business_template)
    elif os.path.isfile(business_template+'.bt5'):
      business_template_info = BusinessTemplateInfoTar(business_template+'.bt5')
    else:
      raise KeyError, "Can't find the business template: %s" % i
    business_template_info_list.append(business_template_info)

  tested_portal_type_list = []
  for business_template_info in business_template_info_list:
    for module_id, module_portal_type in business_template_info.modules.items():
      portal_type_list = [module_portal_type, ] + \
            business_template_info.allowed_content_types.get(module_portal_type, [])
      portal_type_path_dict = {}
      portal_type_path_dict = dict(map(None,portal_type_list,portal_type_list))
      testPortalTypeViewRecursivly(validator=validator,
                       module_id=module_id, 
                       business_template_info=business_template_info, 
                       business_template_info_list=business_template_info_list,
                       portal_type_list=portal_type_list, 
                       portal_type_path_dict=portal_type_path_dict,
                       base_path = '',
                       tested_portal_type_list=tested_portal_type_list)


# Two validators are available : tidy and the w3c validator
# It's hightly recommanded to use the w3c validator because tidy dont show
# all errors and show more warnings that there is.
validator_to_use = 'w3c'
show_warnings = True

validator = None

# tidy or w3c may not be installed in livecd. Then we will skip xhtml validation tests.
# create the validator object
if validator_to_use == 'w3c':
  validator_path = '/usr/share/w3c-markup-validator/cgi-bin/check'
  if not os.path.exists(validator_path):
    print 'w3c validator is not installed at %s' % validator_path
  else:
    validator = W3Validator(validator_path, show_warnings)

elif validator_to_use == 'tidy':
  error = False
  warning = False
  validator_path = '/usr/bin/tidy'
  if not os.path.exists(validator_path):
    print 'tidy is not installed at %s' % validator_path
  else:
    validator = TidyValidator(validator_path, show_warnings)

# add the tests
if validator is not None:
  addTestMethodDynamically(validator)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestXHTML))
  return suite
