##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#          Yoshinori Okuji <yo@nexedi.com>
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

import transaction
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Testing import ZopeTestCase
from Products.ERP5Type.Globals import get_request
from Products.ERP5Type.tests.utils import createZODBPythonScript
from ZPublisher.HTTPRequest import FileUpload
from StringIO import StringIO
from Products.ERP5Form.Selection import Selection
from Products.ERP5Form.Form import ERP5Form


class DummyFieldStorage:
  """A dummy FieldStorage to be wrapped in a FileUpload object.
  """
  def __init__(self):
    self.file = StringIO()
    self.filename = '<dummy field storage>'
    self.headers = {}

class TestListBox(ERP5TypeTestCase):
  """
    Test the API of ListBox. The user-visible aspect is tested
    by functional testing.
  """
  quiet = 1
  run_all_test = 1

  def getBusinessTemplateList(self):
    # Use the same framework as the functional testing for convenience.
    # This adds some specific portal types and skins.
    return ('erp5_ui_test',)

  def getTitle(self):
    return "ListBox"

  def afterSetUp(self):
    self.login()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def stepTic(self,**kw):
    self.tic()

  def stepCreateObjects(self, sequence = None, sequence_list = None, **kw):
    # Make sure that the status is clean.
    portal = self.getPortal()
    portal.ListBoxZuite_reset()

    message = portal.foo_module.FooModule_createObjects()
    self.failUnless('Created Successfully' in message)

  def stepModifyListBoxForStat(self, sequence = None, sequence_list = None, **kw):
    portal = self.getPortal()
    listbox = portal.FooModule_viewFooList.listbox
    message = listbox.ListBox_setPropertyList(
      field_stat_columns = 'id|FooModule_statId\ntitle|FooModule_statTitle',
      field_stat_method = 'portal_catalog')
    self.failUnless('Set Successfully' in message)

  def stepRenderList(self, sequence = None, sequence_list = None, **kw):
    portal = self.getPortal()
    listbox = portal.FooModule_viewFooList.listbox
    request = get_request()
    request['here'] = portal.foo_module
    listboxline_list = listbox.get_value('default', render_format = 'list',
                                         REQUEST = request)
    sequence.edit(listboxline_list = listboxline_list)

  def stepCheckListBoxLineListWithStat(self, sequence = None, sequence_list = None, **kw):
    line_list = sequence.get('listboxline_list')
    self.assertEqual(len(line_list), 12)

    title_line = line_list[0]
    self.failUnless(title_line.isTitleLine())
    self.assertEqual(len(title_line.getColumnItemList()), 3)
    result = (('id', 'ID'), ('title', 'Title'), ('getQuantity', 'Quantity'))
    for i, (key, value) in enumerate(title_line.getColumnItemList()):
      self.assertEqual(key, result[i][0])
      self.assertEqual(value, result[i][1])

    for n, data_line in enumerate(line_list[1:-1]):
      self.failUnless(data_line.isDataLine())
      self.assertEqual(len(data_line.getColumnItemList()), 3)
      result = (('id', str(n)), ('title', 'Title %d' % n), ('getQuantity', str(10.0 - n)))
      for i, (key, value) in enumerate(data_line.getColumnItemList()):
        self.assertEqual(key, result[i][0])
        self.assertEqual(str(value).strip(), result[i][1])

    stat_line = line_list[-1]
    self.failUnless(stat_line.isStatLine())
    self.assertEqual(len(stat_line.getColumnItemList()), 3)
    result = (('id', 'foo_module'), ('title', 'Foos'), ('getQuantity', 'None'))
    for i, (key, value) in enumerate(stat_line.getColumnItemList()):
      self.assertEqual(key, result[i][0])
      self.assertEqual(str(value).strip(), result[i][1])

  def test_01_CheckListBoxLinesWithStat(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test ListBoxLines With Statistics'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateObjects \
                       Tic \
                       ModifyListBoxForStat \
                       RenderList \
                       CheckListBoxLineListWithStat \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_02_DefaultSort(self, quiet=quiet, run=run_all_test):
    """Defaults sort parameters must be passed to the list method, under the
    'sort_on' key.
    """
    portal = self.getPortal()
    portal.ListBoxZuite_reset()

    # We create a script to use as a list method, in this script, we will check
    # the sort_on parameter.
    list_method_id = 'ListBox_checkSortOnListMethod'
    createZODBPythonScript(
        portal.portal_skins.custom,
        list_method_id,
        'selection=None, sort_on=None, **kw',
r"""
if sort_on != [('title', 'ASC'), ('uid', 'ASC')]:
  raise AssertionError('sort_on is %r' % sort_on)
return []
""")
 
    # set the listbox to use this as list method
    listbox = portal.FooModule_viewFooList.listbox
    listbox.ListBox_setPropertyList(
      field_list_method = list_method_id,
      field_count_method = '',
      field_sort = 'title | ASC\n'
                   'uid | ASC',)
    
    # render the listbox, checks are done by list method itself
    request = get_request()
    request['here'] = portal.foo_module
    listbox.get_value('default', render_format='list', REQUEST=request)

  def test_03_DefaultParameters(self, quiet=quiet, run=run_all_test):
    """Defaults parameters are passed as keyword arguments to the list method
    """
    portal = self.getPortal()
    portal.ListBoxZuite_reset()

    # We create a script to use as a list method, in this script, we will check
    # the default parameter.
    list_method_id = 'ListBox_checkDefaultParametersListMethod'
    createZODBPythonScript(
        portal.portal_skins.custom,
        list_method_id,
        'selection=None, dummy_default_param=None, **kw',
"""
if dummy_default_param != 'dummy value':
  raise AssertionError('recieved wrong arguments: %s instead of "dummy value"'
                        % dummy_default_param )
return []
""")
 
    # set the listbox to use this as list method
    listbox = portal.FooModule_viewFooList.listbox
    listbox.ListBox_setPropertyList(
      field_list_method = list_method_id,
      field_count_method = '',
      field_default_params = 'dummy_default_param | dummy value',)
    
    # render the listbox, checks are done by list method itself
    request = get_request()
    request['here'] = portal.foo_module
    listbox.get_value('default', render_format='list', REQUEST=request)

  def test_04_UnicodeParameters(self, quiet=0, run=run_all_test):
    """Unicode properties are handled. 
    """
    portal = self.getPortal()
    portal.ListBoxZuite_reset()
    
    # We create a script to use as a list method
    list_method_id = 'ListBox_ParametersListMethod'
    createZODBPythonScript(
        portal.portal_skins.custom,
        list_method_id,
        'selection=None, **kw',
        """return [context.asContext(alternate_title = u'\xe9lisa')]""")
 
    # set the listbox to use this as list method
    listbox = portal.FooModule_viewFooList.listbox
    listbox.ListBox_setPropertyList(
      field_list_method = list_method_id,
      field_count_method = '',
      field_columns = ['alternate_title | Alternate Title',],)
    
    request = get_request()
    request['here'] = portal.foo_module
    try:
      listbox.get_value('default', render_format='list', REQUEST=request)
    except UnicodeError, e:
      self.fail('Rendering failed: %s' % e)

  def test_05_EditSelectionWithFileUpload(self, quiet=quiet, run=run_all_test):
    """Listbox edits selection with request parameters. Special care must be
    taken for FileUpload objects that cannot be pickled, thus cannot be stored
    in the ZODB.
    """
    portal = self.getPortal()
    portal.ListBoxZuite_reset()
    listbox = portal.FooModule_viewFooList.listbox
    # XXX isn't Selection automatically created ?
    portal.portal_selections.setSelectionFor(
          listbox.get_value('selection_name'), Selection())

    request = get_request()
    request['here'] = portal.foo_module
    request.form['my_file_upload'] = FileUpload(DummyFieldStorage())
    listbox.get_value('default', render_format='list', REQUEST=request)
    try:
      transaction.commit()
    except TypeError, e:
      self.fail('Unable to commit transaction: %s' % e)

  def test_06_LineFields(self, quiet=0, run=run_all_test):
    """
       Line Fields are able to render a list parameter in the form
       of lines. The same behaviour is expected for Line Fields used
       in ListBox objects.
    """
    portal = self.getPortal()
    portal.ListBoxZuite_reset()

    # Reset listbox properties
    listbox = portal.FooModule_viewFooList.listbox
    listbox.ListBox_setPropertyList(
      field_list_method = 'portal_catalog',
      field_columns = ['subject_list | Subjects',],
      field_editable_columns = ['subject_list | Subjects',],
    )

    # Create an new empty object with a list property
    foo_module = portal.foo_module
    word = 'averycomplexwordwhichhaslittlechancetoexistinhtml'
    o = foo_module.newContent(subject_list = [word])

    # Make sure that word is the subject list
    self.assertEqual(word in o.getSubjectList(), True)

    # Reindex
    o.immediateReindexObject()

    # Render the module in html
    request = get_request()
    request['here'] = portal.foo_module
    rendered_listbox = listbox.render(REQUEST=request)

    # Make sure that word is there
    self.assertEqual(rendered_listbox.find(word) > 0, True)

  def test_ObjectSupport(self):
    # make sure listbox supports rendering of simple objects
    # the only requirement is that objects have a `uid` attribute which is a
    # string starting by new_ (a convention to prevent indexing of objects).
    portal = self.getPortal()
    list_method_id = 'DummyListMethodId'
    portal.ListBoxZuite_reset()
    form = portal.FooModule_viewFooList
    listbox = form.listbox
    listbox.ListBox_setPropertyList(
      field_list_method = list_method_id,
      field_count_method = '',
      field_editable_columns = ['title | title'],
      field_columns = ['title | Title',],)
    form.manage_addField('listbox_title', 'Title', 'StringField')
    
    createZODBPythonScript(
        portal.portal_skins.custom,
        list_method_id,
        'selection=None, **kw',
        "from Products.PythonScripts.standard import Object\n"
        "return [Object(uid='new_', title='Object Title')]")
    
    request = get_request()
    request['here'] = portal.foo_module
    line_list = [l for l in listbox.get_value('default',
                               render_format='list',
                               REQUEST=request) if l.isDataLine()]
    self.assertEquals(1, len(line_list))
    self.assertEquals('Object Title', line_list[0].getColumnProperty('title'))
    html = listbox.render(REQUEST=request)
    self.failUnless('Object Title' in html, html)

  def test_ProxyFieldRenderFormatLines(self):
    # tests that listbox default value in render_format=list mode is
    # compatible with proxy field.
    portal = self.getPortal()
    portal.ListBoxZuite_reset()
    form = portal.FooModule_viewFooList
    listbox = form.listbox
    listbox.ListBox_setPropertyList(
      field_list_method='contentValues',
      field_columns=['listbox_value | Title',],)
    
    # create a form, to store our proxy field inside
    portal._setObject('Test_view',
                      ERP5Form('Test_view', 'View'))
    portal.Test_view.manage_addField('listbox', 'listbox', 'ProxyField')
    proxy_field = portal.Test_view.listbox
    proxy_field.manage_edit_xmlrpc(dict(
            form_id=form.getId(), field_id='listbox',
            columns=[('proxy_value', 'Proxy')]))

    # this proxy field will not delegate its "columns" value
    proxy_field._surcharged_edit(dict(columns=[('proxy_value', 'Proxy')]),
                                ['columns'])
    
    request = get_request()
    request['here'] = portal.foo_module
    line_list = proxy_field.get_value('default',
                      render_format='list', REQUEST=request)
    self.failUnless(isinstance(line_list, list))

    title_line = line_list[0]
    self.failUnless(title_line.isTitleLine())

    # title of columns is the value overloaded by the proxy field.
    self.assertEquals([('proxy_value', 'Proxy')],
                      title_line.getColumnItemList())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestListBox))
  return suite

