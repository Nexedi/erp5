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
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from subprocess import Popen, PIPE
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import addUserToDeveloperRole
from Products.CMFCore.utils import getToolByName
from zLOG import LOG
# You can invoke same tests in your favourite collection of business templates
# by using TestXHTMLMixin like the following :
#
# from Products.ERP5.tests.testERP5XHTML import TestXHTMLMixin
# class TestMyXHTML(TestXHTMLMixin):
#   def getBusinessTemplateList(self):
#     return (...)

class TestXHTMLMixin(ERP5TypeTestCase):

  # some forms have intentionally empty listbox selections like RSS generators
  FORM_LISTBOX_EMPTY_SELECTION_PATH_LIST = ['erp5_web_widget_library/WebSection_viewContentListAsRSS',
                                            'erp5_core/Base_viewHistoricalComparisonDiff',
                                            'erp5_diff/ERP5Site_viewDiffTwoObjectDialog',]
  JSL_IGNORE_FILE_LIST = (
        'diff2html.js',
        'diff2html-ui.js',
        'dream_graph_editor/lib/handlebars.min.js',
        'dream_graph_editor/lib/jquery-ui.js',
        'dream_graph_editor/lib/jquery.js',
        'dream_graph_editor/lib/jquery.jsplumb.js',
        'dream_graph_editor/lib/jquery.simulate.js',
        'dream_graph_editor/lib/qunit.js',
        'dream_graph_editor/lib/springy.js',
        'handlebars.js',
        'jio.js',
        'jslint.js',
        'pdf_js/build/pdf.js',
        'pdf_js/build/pdf.worker.js',
        'pdf_js/compatibility.js',
        'pdf_js/debugger.js',
        'pdf_js/l10n.js',
        'pdf_js/viewer.js',
        'renderjs.js',
        'require.js',
        'require.min.js',
        'rsvp.js',
        'wz_dragdrop.js',
        )
  JSL_IGNORE_SKIN_LIST = (
        'erp5_code_mirror',
        'erp5_fckeditor',
        'erp5_ckeditor',
        'erp5_jquery',
        'erp5_jquery_ui',
        'erp5_pivot_table',
        'erp5_sql_browser',
        'erp5_dhtmlx_scheduler',
        'erp5_svg_editor',
        )

  HTML_IGNORE_FILE_LIST = (
        'gadget_erp5_side_by_side_diff.html',
        )
  # NOTE: Here the difference between the JSL_IGNORE_SKIN_LIST is that we also
  # consider the folders inside the skin. In this way, we can include multiple
  # HTML files at once which are inside some folder in any skin folder.
  HTML_IGNORE_SKIN_FOLDER_LIST = (
        'erp5_jquery',
        'erp5_fckeditor',
        'erp5_ckeditor',
        'erp5_svg_editor',
        'erp5_jquery_ui',
        'erp5_dms/pdf_js',
        'erp5_test_result/test_result_js',
        )

  def changeSkin(self, skin_name):
    """
      Change current Skin
    """
    request = self.app.REQUEST
    self.getPortal().portal_skins.changeSkin(skin_name)
    request.set('portal_skin', skin_name)

  def getFieldList(self, form, form_path):
    try:
      for field in form.get_fields(include_disabled=1):
        if field.getTemplateField() is not None:
          try:
            if field.get_value('enabled'):
              yield field
          except Exception:
            yield field
    except AttributeError, e:
      ZopeTestCase._print("%s is broken: %s" % (form_path, e))

  def test_deadProxyFields(self):
    # check that all proxy fields defined in business templates have a valid
    # target
    skins_tool = self.portal.portal_skins
    error_list = []

    for skin_name, skin_folder_string in skins_tool.getSkinPaths():
      skin_folder_id_list = skin_folder_string.split(',')
      self.changeSkin(skin_name)

      for skin_folder_id in skin_folder_id_list:
        for field_path, field in skins_tool[skin_folder_id].ZopeFind(
                  skins_tool[skin_folder_id],
                  obj_metatypes=['ProxyField'], search_sub=1):
          template_field = field.getTemplateField(cache=False)
          if template_field is None:
            # Base_viewRelatedObjectList (used for proxy listbox ids on
            # relation fields) is an exception, the proxy field has no target
            # by default.
            if field_path != 'Base_viewRelatedObjectList/listbox':
              error_list.append((skin_name, field_path, field.get_value('form_id'),
                                 field.get_value('field_id')))

    if error_list:
      message = '\nDead proxy field list%s\n' \
                    % '\n\t'.join(str(e) for e in error_list)
      self.fail(message)

  def test_configurationOfFieldLibrary(self):
    error_list = []
    for business_template in self.portal.portal_templates.searchFolder(
          title=['erp5_trade']):
      # XXX Impossible to filter by installation state, as it is not catalogued
      business_template = business_template.getObject()
      for modifiable_field in business_template.BusinessTemplate_getModifiableFieldList():
        # Do not consider 'Check delegated values' as an error
        if modifiable_field.choice_item_list[0][1] not in \
            ("0_check_delegated_value", "0_keep_non_proxy_field"):
          error_list.append((modifiable_field.object_id,
                            modifiable_field.choice_item_list[0][0]))
    if error_list:
      message = '%s fields to modify' % len(error_list)
      message += '\n\t' + '\n\t'.join(fieldname + ": " + message
                                       for fieldname, message in error_list)
      self.fail(message)

  def test_portalTypesDomainTranslation(self):
    # according to bt5-Module.Creation.Guidelines document, module
    # portal_types should be translated using erp5_ui, and normal ones, using
    # erp5_content
    error_list = []
    portal_types_module = self.portal.portal_types
    for portal_type in portal_types_module.contentValues(portal_type=\
        'Base Type'):
      if portal_type.getId().endswith('Module'):
        for k, v in portal_type.getPropertyTranslationDomainDict().items():
          if k in ('title', 'short_title') and v.getDomainName() != 'erp5_ui':
            error_list.append('"%s" should use erp5_ui for %s' % \
                (portal_type.getId(), k))
    if error_list:
      message = '\nBad portal_type domain translation list%s\n' \
                    % '\n\t'.join(error_list)
      self.fail(message)

  def test_emptySelectionNameInListbox(self):
    # check all empty selection name in listboxes
    skins_tool = self.portal.portal_skins
    error_list = []
    for form_path, form in skins_tool.ZopeFind(
              skins_tool, obj_metatypes=['ERP5 Form'], search_sub=1):
      for field in self.getFieldList(form, form_path):
        if field.getRecursiveTemplateField().meta_type == 'ListBox':
          selection_name = field.get_value("selection_name")
          if selection_name in ("",None) and \
            form_path not in self.FORM_LISTBOX_EMPTY_SELECTION_PATH_LIST:
            error_list.append(form_path)
    self.assertEqual(error_list, [])

  def test_duplicatingSelectionNameInListbox(self):
    """
    Check for duplicating selection name in listboxes.
    Usually we should not have duplicates except in some rare cases
    described in SkinsTool_getDuplicateSelectionNameDict
    """
    portal_skins = self.portal.portal_skins
    duplicating_selection_name_dict = portal_skins.SkinsTool_getDuplicateSelectionNameDict()
    self.assertFalse(duplicating_selection_name_dict,
                     "Repeated listbox selection names:\n" +
                     portal_skins.SkinsTool_checkDuplicateSelectionName())

  def test_javascript_lint(self):
    skins_tool = self.portal.portal_skins
    path_list = []
    for script_path, script in skins_tool.ZopeFind(skins_tool,
        obj_metatypes=('File','DTML Method','DTML Document'), search_sub=1):
      if script_path.endswith('.js'):
        x = script_path.split('/', 1)
        if not (x[0] in self.JSL_IGNORE_SKIN_LIST or
                x[1] in self.JSL_IGNORE_FILE_LIST):
          path_list.append(script_path)
    portal_skins_path = self.portal.getId() + '/portal_skins/'
    args = ('jsl', '-stdin', '-nologo', '-nosummary', '-conf',
            os.path.join(os.path.dirname(__file__), 'jsl.conf'))
    error_list = []
    for path in path_list:
      check_path = portal_skins_path + path
      body = self.publish(check_path).getBody()
      try:
        stdout, stderr = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                               close_fds=True).communicate(body)
      except OSError, e:
        raise OSError, '%r\n%r' % (os.environ, e)
      if stdout:
        error_list.append((check_path, stdout))
    if error_list:
      message = '\n'.join(["%s\n%s\n" % error for error in error_list])
      self.fail(message)

  def test_html_file(self):
    skins_tool = self.portal.portal_skins
    path_list = []
    for script_path, script in skins_tool.ZopeFind(
              skins_tool, obj_metatypes=['File'], search_sub=1):
      if script_path.endswith('.html'):
        x = script_path.split('/', 1)
        if not x[1] in self.HTML_IGNORE_FILE_LIST:
          is_required_check_path = False
        for ignore_folder_name in self.HTML_IGNORE_SKIN_FOLDER_LIST:
          if  script_path.startswith(ignore_folder_name):
            is_required_check_path = False
            break;
        if is_required_check_path:
          path_list.append(script_path)

    def validate_html_file(source_path):
      message = ['Using %s validator to parse the file "%s"'
                 ' with warnings%sdisplayed :'
                % (validator.name, source_path,
                   validator.show_warnings and ' ' or ' NOT ')]
      source = self.publish(source_path).getBody()
      result_list_list = validator.getErrorAndWarningList(source)
      severity_list = ['Error']
      if validator.show_warnings:
        severity_list.append('Warning')
      for i, severity in enumerate(severity_list):
        for line, column, msg in result_list_list[i]:
          if line is None and column is None:
            message.append('%s: %s' % (severity, msg))
          else:
            message.append('%s: line %s column %s : %s' %
                           (severity, line, column, msg))
      return len(message) == 1, '\n'.join(message)

    def html_file(check_path):
      self.assert_(*validate_html_file(source_path=check_path))

    portal_skins_path = '%s/portal_skins' % self.portal.getId()
    for path in path_list:
      check_path = '%s/%s' % (portal_skins_path, path)
      html_file(check_path)

  def test_PythonScriptSyntax(self):
    """
    Check that Python Scripts syntax is correct.
    """
    for tool in (self.portal.portal_skins, self.portal.portal_workflow):
      for script_path, script in tool.ZopeFind(
                tool, obj_metatypes=['Script (Python)'], search_sub=1):
        if script.errors!=():
          # we need to add script id as well in test failure
          self.assertEqual('%s : %s' %(script_path, script.errors), ())

  def test_SkinItemId(self):
    """
    Check that skin item id is acquiring is correct.
    """
    skins_tool = self.portal.portal_skins
    for skin_folder in skins_tool.objectValues('Folder'):
      for skin_item in skin_folder.objectValues():
        if skin_item.meta_type not in ('File', 'Image', 'DTML Document', 'DTML Method',):
          skin_item_id = skin_item.id
          self.assertEqual(skin_item_id, skin_folder[skin_item_id].id)

  def test_callableListMethodInListbox(self):
    # check all list_method in listboxes
    skins_tool = self.portal.portal_skins
    error_list = []
    for form_path, form in skins_tool.ZopeFind(
              skins_tool, obj_metatypes=['ERP5 Form'], search_sub=1):
      for field in self.getFieldList(form, form_path):
        if field.getRecursiveTemplateField().meta_type == 'ListBox':
          list_method = field.get_value("list_method")
          if list_method:
            if isinstance(list_method, str):
              method = getattr(self.portal, list_method, None)
            else:
              method = list_method
            if not callable(method):
              error_list.append((form_path, list_method))
    self.assertEqual(error_list, [])

  def test_callableCountMethodInListbox(self):
    # check all count_method in listboxes
    skins_tool = self.portal.portal_skins
    error_list = []
    for form_path, form in skins_tool.ZopeFind(
              skins_tool, obj_metatypes=['ERP5 Form'], search_sub=1):
      for field in self.getFieldList(form, form_path):
        if field.getRecursiveTemplateField().meta_type == 'ListBox':
          count_method = field.get_value("count_method")
          if count_method:
            if isinstance(count_method, str):
              method = getattr(self.portal, count_method, None)
            else:
              method = count_method
            if not callable(method):
              error_list.append((form_path, count_method))
    self.assertEqual(error_list, [])

  def test_listActionInListbox(self):
    # check all list_action in listboxes
    skins_tool = self.portal.portal_skins
    error_list = []
    for form_path, form in skins_tool.ZopeFind(
              skins_tool, obj_metatypes=['ERP5 Form'], search_sub=1):
      for field in self.getFieldList(form, form_path):
        if field.getRecursiveTemplateField().meta_type == 'ListBox':
          list_action = field.get_value("list_action")
          if list_action and list_action != 'list': # We assume that 'list'
                                                    # list_action exists
            if isinstance(list_action, str):
              # list_action can be a fully qualified URL, we care for last part of it
              list_action = list_action.split('/')[-1].split('?')[0]
              try:
                method = self.portal.restrictedTraverse(list_action)
              except KeyError:
                method = None
              if method is None:
                # list_action can actually exists but not in current skin, check if it can be found in portal_skins
                found_list_action_list = skins_tool.ZopeFind(skins_tool, obj_ids=[list_action], search_sub=1)
                if found_list_action_list:
                  method = found_list_action_list[0][1]
                  ZopeTestCase._print("List action %s for %s is not part of current skin but do exists in another skin folder.\n" % (list_action, form_path))
            else:
              method = list_action
            if not callable(method):
              error_list.append('Form %s/%s : list_action "%s" is not callable.'\
                  % (form_path, field.id, list_action))
    self.assert_(not len(error_list), '\n'.join(error_list))

  def test_moduleListMethod(self):
    """Make sure that module's list method works."""
    error_list = []
    for document in self.portal.contentValues():
      if document.portal_type.endswith(' Module'):
        if document.getTranslatedTitle() not in document.list(reset=1):
          error_list.append(document.id)
    self.assertEqual([], error_list)

  def test_preferenceViewDuplication(self):
    """Make sure that preference view is not duplicated."""
    preference_view_id_dict = {}
    def addPreferenceView(folder_id, view_id):
      preference_view_id_dict.setdefault(view_id, []).append('%s.%s' % (folder_id, view_id))
    error_list = []
    for skin_folder in self.portal.portal_skins.objectValues():
      if skin_folder.isPrincipiaFolderish:
        for id_ in skin_folder.objectIds():
          if id_.startswith('Preference_view'):
            addPreferenceView(skin_folder.id, id_)
    for view_id, location_list in preference_view_id_dict.items():
      if len(location_list) > 1:
        error_list.extend(location_list)
    self.assertEqual(error_list, [])

class TestXHTML(TestXHTMLMixin):

  run_all_test = 1

  def getTitle(self):
    return "XHTML Test"

  @staticmethod
  def getBusinessTemplateList():
    """  """
    return ( # dependency order
      'erp5_core_proxy_field_legacy',
      'erp5_base',
      'erp5_simulation',
      'erp5_pdm',
      'erp5_trade',

      'erp5_pdf_editor',
      'erp5_accounting',
      'erp5_invoicing',

      'erp5_apparel',

##    'erp5_banking_core',
##    'erp5_banking_cash',
##    'erp5_banking_check',
##    'erp5_banking_inventory',

      'erp5_budget',
      'erp5_public_accounting_budget',

      'erp5_consulting',

      'erp5_ingestion',
      'erp5_ingestion_mysql_innodb_catalog',
      'erp5_crm',
      'erp5_interface_post',

      'erp5_jquery',
      'erp5_jquery_ui',
      'erp5_web',
      'erp5_dms',
      'erp5_email_reader',
      'erp5_commerce',
      'erp5_credential',
      'erp5_web_service',
      'erp5_test_result',

      'erp5_forge',

      'erp5_immobilisation',

      'erp5_item',

      'erp5_mrp',

      'erp5_payroll',

      'erp5_project',

      'erp5_calendar',

      'erp5_advanced_invoicing',

      'erp5_odt_style',

      'erp5_administration',

      'erp5_knowledge_pad',
      'erp5_knowledge_pad_ui_test',
      'erp5_km',
      'erp5_ui_test',
      'erp5_dms_ui_test',

      'erp5_trade_proxy_field_legacy', # it is necessary until all bt are well
                                       # reviewed. Many bt like erp5_project are
                                       # using obsolete field library of trade
      'erp5_xhtml_style',
      'erp5_dhtml_style',
      'erp5_jquery_plugin_svg_editor',
      'erp5_jquery_plugin_spinbtn',
      'erp5_jquery_plugin_jquerybbq',
      'erp5_jquery_plugin_svgicon',
      'erp5_jquery_plugin_jgraduate',
      'erp5_jquery_plugin_hotkey',
      'erp5_jquery_plugin_elastic',
      'erp5_jquery_plugin_colorpicker',
      'erp5_jquery_plugin_jqchart',
      'erp5_jquery_plugin_sheet',
      'erp5_jquery_plugin_mbmenu',
      'erp5_jquery_plugin_wdcalendar',
      'erp5_svg_editor',
      'erp5_jquery_sheet_editor',
      'erp5_graph_editor',
      'erp5_ui_test',
      'erp5_l10n_fr', # install at least one localization business template
                      # because some language switching widgets are only
                      # present if there is more than one available language.
    )

  def afterSetUp(self):
    self.portal = self.getPortal()

    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])

    self.loginByUserName('seb')
    addUserToDeveloperRole('seb') # required to create content in portal_components
    self.enableDefaultSitePreference()

  def enableDefaultSitePreference(self):
    portal_preferences = getToolByName(self.portal, 'portal_preferences')
    default_site_preference = portal_preferences.default_site_preference
    if self.portal.portal_workflow.isTransitionPossible(default_site_preference, 'enable'):
      default_site_preference.enable()


class NuValidator(object):

  def __init__(self, show_warnings, validator_url='https://validator.erp5.net/'):
    self.show_warnings = show_warnings
    self.name = 'nu'
    self.validator_url = validator_url
    self.validator_session = requests.Session()
    # retries HTTP 502 errors which sometimes happen with validator.erp5.net
    self.validator_session.mount(
        self.validator_url,
        requests.adapters.HTTPAdapter(
            max_retries=Retry(
                total=3,
                read=3,
                connect=3,
                backoff_factor=.5,
                status_forcelist=(502, ))))

  def _parse_validation_results(self, response):
    """
    parses the validation results, returns a list of tuples:
    line_number, col_number, error description
    """
    if response.status_code != 200:
      return [
        [(None, None,
          'Contacting the external validator %s failed with status: %i' %
            (self.validator_url, response.status_code))],
        []
      ]

    content_type = response.headers.get('Content-Type', None)
    if content_type != 'application/json;charset=utf-8':
      return [[(None, None, 'Unsupported validator response content type %s' %
                            content_type)], []]

    result = response.json()

    error_list = []
    warning_list = []
    for message in result['messages']:
      if message['type'] == 'info':
        severity_list = warning_list
      else:
        severity_list = error_list
      txt = message['message'].encode('UTF-8')
      if 'extract' in message:
        txt += ': %s' % message['extract'].encode('UTF-8')
      severity_list.append([message['lastLine'], message['lastColumn'], txt])
    return [error_list, warning_list]

  def getErrorAndWarningList(self, page_source):
    '''
      retrun two list : a list of errors and an other for warnings
    '''
    response = self.validator_session.post(self.validator_url,
                             data=page_source.encode('UTF-8'),
                             params={'out': 'json'},
                             headers={
                               'Content-Type': 'text/html; charset=UTF-8'
                             })
    return self._parse_validation_results(response)


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
          message = data[1].split(': ')[1]
          error_list.append((line, column, message))
        elif data[1].startswith('Warning: '):
          location_list = data[0].split(' ')
          line = location_list[1]
          column = location_list[3]
          message = data[1].split(': ')[1]
          warning_list.append((line, column, message))
    return (error_list, warning_list)

  def getErrorAndWarningList(self, page_source):
    '''
      retrun two list : a list of errors and an other for warnings
    '''
    stdout, stderr = Popen('%s -e -q -utf8' % self.validator_path,
            stdin=PIPE, stdout=PIPE, stderr=PIPE,
            close_fds=True).communicate(page_source)
    return self._parse_validation_results(stderr)


def validate_xhtml(validator, source, view_name, bt_name):
  '''
    validate_xhtml return True if there is no error on the page, False else.
    Now it's possible to show warnings, so, if the option is set to True on the
    validator object, and there is some warning on the page, the function
    return False, even if there is no error.
  '''
  # display some information when test faild to facilitate debugging
  message = ['Using %s validator to parse the view "%s" (from %s bt)'
             ' with warnings%sdisplayed :'
             % (validator.name, view_name, bt_name,
                validator.show_warnings and ' ' or ' NOT ')]

  result_list_list = validator.getErrorAndWarningList(source)

  severity_list = ['Error']
  if validator.show_warnings:
    severity_list.append('Warning')

  for i, severity in enumerate(severity_list):
    for line, column, msg in result_list_list[i]:
      if line is None and column is None:
        message.append('%s: %s' % (severity, msg))
      else:
        message.append('%s: line %s column %s : %s' %
                       (severity, line, column, msg))

  return len(message) == 1, '\n'.join(message)


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
    portal_type_list = portal_type.split('/')
    if module_id:
      module = getattr(self.portal, module_id)
    else:
      # when module_id is not provided, we assume it's a tool and
      # look dynamically.
      module_list = self.portal.contentValues(
        filter={'portal_type': portal_type_list[0]})
      if not module_list:
        self.fail('Could not find a %s in portal' % portal_type_list[0])
      module = module_list[0]
      portal_type_list = portal_type_list[1:]

    document = createSubContent(module, portal_type_list)
    view = getattr(document, view_name)
    self.assert_(*validate_xhtml( validator=validator,
                                  source=view(),
                                  view_name=view_name,
                                  bt_name=bt_name))
  return testMethod

def testPortalTypeViewRecursivly(test_class, validator, module_id,
    business_template_info, business_template_info_list, portal_type_list,
    portal_type_path_dict, base_path, tested_portal_type_list):
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
      for business_template_info in business_template_info_list:
        if portal_type not in business_template_info.actions:
          continue
        for action_information in business_template_info.actions[portal_type]:
          if (action_information['category'] in ('object_view', 'object_list') and
              action_information['visible']==1 and
              action_information['action'].startswith('string:${object_url}/') and
              len(action_information['action'].split('/'))==2):
            view_name = action_information['action'].split('/')[-1].split('?')[0]
            method = makeTestMethod(validator,
                                    module_id,
                                    portal_path,
                                    view_name,
                                    business_template_info.title)
            method_name = ('test_%s_%s_%s' %
                          (business_template_info.title,
                            str(portal_type).replace(' ','_'), # can be unicode
                            view_name))
            method.__name__ = method_name
            setattr(test_class, method_name, method)
            module_id = backuped_module_id

      # add the portal_type to the tested portal_types. This avoid to test many
      # times a Portal Type wich is many bt.
      tested_portal_type_list.append(portal_type)

      new_portal_type_list = []
      for tmp_business_template_info in business_template_info_list:
        new_portal_type_list.extend(tmp_business_template_info.allowed_content_types.get(portal_type, ()))
      new_portal_type_path_dict = {}

      if base_path != '':
        next_base_path = '%s/%s' % (base_path, portal_type)
      # Module portal_type not to have been added to the path because
      # this portal type object already existing
      elif not portal_type.endswith(' Module'):
        next_base_path = portal_type
      else:
        next_base_path = ''

      for pt in new_portal_type_list:
        if next_base_path != '' and not pt.endswith(' Module'):
          new_portal_type_path_dict[pt] = '%s/%s' % (next_base_path, pt)
        else:
          new_portal_type_path_dict[pt] = pt
      testPortalTypeViewRecursivly(test_class=test_class,
                       validator=validator,
                       module_id=module_id,
                       business_template_info=backuped_business_template_info,
                       business_template_info_list=business_template_info_list,
                       portal_type_list=new_portal_type_list,
                       portal_type_path_dict=new_portal_type_path_dict,
                       base_path=next_base_path,
                       tested_portal_type_list=tested_portal_type_list)

def addTestMethodDynamically(test_class, validator, target_business_templates):
  from Products.ERP5.tests.utils import BusinessTemplateInfoTar
  from Products.ERP5.tests.utils import BusinessTemplateInfoDir
  business_template_info_list = []

  for url, _ in ERP5TypeTestCase._getBTPathAndIdList(target_business_templates):
    if os.path.isdir(url):
      business_template_info = BusinessTemplateInfoDir(url)
    else:
      business_template_info = BusinessTemplateInfoTar(url)
    business_template_info_list.append(business_template_info)

  # The portal types from this set of business template
  business_template_portal_type_set = set([])
  for business_template_info in business_template_info_list:
    business_template_portal_type_set.update(business_template_info.allowed_content_types.keys())
    for allowed_content_type_list in business_template_info.allowed_content_types.values():
      business_template_portal_type_set.update(allowed_content_type_list)

  # The already tested portal types
  tested_portal_type_list = []

  # Documents can be contained in modules or in tools.
  # First try all portal types in modules context.
  for business_template_info in business_template_info_list:
    for module_id, module_portal_type in business_template_info.modules.items():
      portal_type_list = [module_portal_type, ] + \
            business_template_info.allowed_content_types.get(module_portal_type, [])
      portal_type_path_dict = dict(zip(portal_type_list, portal_type_list))
      testPortalTypeViewRecursivly(test_class=test_class,
                       validator=validator,
                       module_id=module_id,
                       business_template_info=business_template_info,
                       business_template_info_list=business_template_info_list,
                       portal_type_list=portal_type_list,
                       portal_type_path_dict=portal_type_path_dict,
                       base_path = '',
                       tested_portal_type_list=tested_portal_type_list)

  # For the remaining portal types, we don't have modules, we'll try to find their containers at runtime.
  business_template_portal_type_set = business_template_portal_type_set.difference(tested_portal_type_list)
  for business_template_info in business_template_info_list:
    for portal_type in sorted(business_template_portal_type_set, key=lambda pt: 'Tool' not in pt):
      portal_type_list = [portal_type, ] + \
            business_template_info.allowed_content_types.get(portal_type, [])
      portal_type_path_dict = dict(zip(portal_type_list, portal_type_list))
      testPortalTypeViewRecursivly(test_class=test_class,
                      validator=validator,
                      module_id=None,
                      business_template_info=business_template_info,
                      business_template_info_list=business_template_info_list,
                      portal_type_list=portal_type_list,
                      portal_type_path_dict=portal_type_path_dict,
                      base_path = '',
                      tested_portal_type_list=tested_portal_type_list)

  # Still not found, issue a warning.
  not_tested_portal_type = business_template_portal_type_set.difference(tested_portal_type_list)
  if not_tested_portal_type:
    # this may happen when some portal types does not have views (like Simulation Movement for example)
    ZopeTestCase._print(
        "Could not generate test methods for the following portal types: %s\n"
        % (', '.join(not_tested_portal_type)))

# Two validators are available : nu and tidy
# It's hightly recommanded to use the nu validator which validates html5
validator_to_use = 'nu'
show_warnings = True

validator = None

# tidy may not be installed in livecd. Then we will skip xhtml validation tests.
# create the validator object
if validator_to_use == 'tidy':
  error = False
  warning = False
  validator_path = '/usr/bin/tidy'
  if not os.path.exists(validator_path):
    print 'tidy is not installed at %s' % validator_path
  else:
    validator = TidyValidator(validator_path, show_warnings)

elif validator_to_use == 'nu':
  validator = NuValidator(show_warnings)

def test_suite():
  # add the tests
  if validator is not None:
    # add erp5_core to the list here to not return it
    # on getBusinessTemplateList call
    addTestMethodDynamically(TestXHTML, validator,
      ('erp5_core',) + TestXHTML.getBusinessTemplateList())
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestXHTML))
  return suite
