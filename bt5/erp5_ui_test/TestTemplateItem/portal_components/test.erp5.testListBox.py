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
from lxml import etree
import textwrap

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Testing import ZopeTestCase
from Products.ERP5Type.Globals import get_request
from Products.ERP5Type.tests.utils import createZODBPythonScript
from ZPublisher.HTTPRequest import FileUpload
from StringIO import StringIO
from Products.ERP5Form.Selection import Selection
from Products.Formulator.TALESField import TALESMethod
from Products.ERP5Form.ListBox import ListBoxHTMLRenderer


class DummyFieldStorage:
  """A dummy FieldStorage to be wrapped in a FileUpload object.
  """
  def __init__(self):
    self.file = StringIO()
    self.filename = '<dummy field storage>'
    self.headers = {}
    self.name = "Dummy Field Storage"

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
    return ('erp5_core_proxy_field_legacy', 'erp5_ui_test',)

  def getTitle(self):
    return "ListBox"

  def stepCreateObjects(self, sequence = None, sequence_list = None, **kw):
    # Make sure that the status is clean.
    portal = self.getPortal()
    portal.ListBoxZuite_reset()

    message = portal.foo_module.FooModule_createObjects()
    self.assertIn('Created Successfully', message)

  def stepModifyListBoxForStat(self, sequence = None, sequence_list = None, **kw):
    portal = self.getPortal()
    listbox = portal.FooModule_viewFooList.listbox
    message = listbox.ListBox_setPropertyList(
      field_stat_columns = 'id|FooModule_statId\ntitle|FooModule_statTitle',
      field_stat_method = 'portal_catalog')
    self.assertIn('Set Successfully', message)

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
    self.assertTrue(title_line.isTitleLine())
    self.assertEqual(len(title_line.getColumnItemList()), 3)
    result = (('id', 'ID'), ('title', 'Title'), ('getQuantity', 'Quantity'))
    for i, (key, value) in enumerate(title_line.getColumnItemList()):
      self.assertEqual(key, result[i][0])
      self.assertEqual(value, result[i][1])

    for n, data_line in enumerate(line_list[1:-1]):
      self.assertTrue(data_line.isDataLine())
      self.assertEqual(len(data_line.getColumnItemList()), 3)
      result = (('id', str(n)), ('title', 'Title %d' % n), ('getQuantity', str(10.0 - n)))
      for i, (key, value) in enumerate(data_line.getColumnItemList()):
        self.assertEqual(key, result[i][0])
        self.assertEqual(str(value).strip(), result[i][1])

    stat_line = line_list[-1]
    self.assertTrue(stat_line.isStatLine())
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
        textwrap.dedent(r"""
        if sort_on != [('title', 'ASC'), ('uid', 'ASC')]:
          raise AssertionError('sort_on is %r' % sort_on)
        return []
        """))

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
        textwrap.dedent(
        """
        if dummy_default_param != 'dummy value':
          raise AssertionError('recieved wrong arguments: %s instead of "dummy value"'
                                % dummy_default_param )
        return []
        """))

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
    except UnicodeError as e:
      self.fail('Rendering failed: %s' % e)
    self.assertIn(u"\xe9lisa", listbox.render(REQUEST=request))

  def test_UTF8Parameters(self, quiet=0, run=run_all_test):
    """UTF8 encoded string properties are also handled
    """
    portal = self.getPortal()
    portal.ListBoxZuite_reset()

    # We create a script to use as a list method
    list_method_id = 'ListBox_ParametersListMethod'
    createZODBPythonScript(
        portal.portal_skins.custom,
        list_method_id,
        'selection=None, **kw',
        """return [context.asContext(alternate_title = u'\xe9lisa'.encode('utf8'))]""")

    # set the listbox to use this as list method
    listbox = portal.FooModule_viewFooList.listbox
    listbox.ListBox_setPropertyList(
      field_list_method = list_method_id,
      field_count_method = '',
      field_columns = ['alternate_title | Alternate Title',],
      field_url_columns = ['alternate_title | alternate_title',],)

    request = get_request()
    request['here'] = portal.foo_module
    try:
      listbox.get_value('default', render_format='list', REQUEST=request)
    except UnicodeError as e:
      self.fail('Rendering failed: %s' % e)
    self.assertIn(u"\xe9lisa", listbox.render(REQUEST=request))

  def test_UnicodeURLColumns(self, quiet=0, run=run_all_test):
    """URL column script can return unicode
    """
    portal = self.getPortal()
    portal.ListBoxZuite_reset()

    # We create a script to use as a url column method
    url_column_method_id = 'Base_get%sUrlColumnMethod' % self.id()
    createZODBPythonScript(
        portal.portal_skins.custom,
        url_column_method_id,
        'selection=None, **kw',
        """return u'http://example.com/?\xe9lisa'""")

    listbox = portal.FooModule_viewFooList.listbox
    # here we cover two cases, id has an editable field, title has not
    listbox.ListBox_setPropertyList(
      field_url_columns = [
        'title | %s' % url_column_method_id,
        'id | %s' % url_column_method_id,
        ],)

    foo_module = portal.foo_module
    foo_module.newContent(title=u'\xe9lisa')
    self.tic()

    request = get_request()
    request['here'] = portal.foo_module
    try:
      listbox.get_value('default', render_format='list', REQUEST=request)
    except UnicodeError as e:
      self.fail('Rendering failed: %s' % e)
    self.assertIn(u"http://example.com/?\xe9lisa", listbox.render(REQUEST=request))

  def test_UTF8URLColumns(self, quiet=0, run=run_all_test):
    """URL column script can return UTF8 encoded string
    """
    portal = self.getPortal()
    portal.ListBoxZuite_reset()

    # We create a script to use as a url column method
    url_column_method_id = 'Base_get%sUrlColumnMethod' % self.id()
    createZODBPythonScript(
        portal.portal_skins.custom,
        url_column_method_id,
        'selection=None, **kw',
        """return u'http://example.com/?\xe9lisa'.encode('utf8')""")

    listbox = portal.FooModule_viewFooList.listbox
    # here we cover two cases, id has an editable field, title has not
    listbox.ListBox_setPropertyList(
      field_url_columns = [
        'title | %s' % url_column_method_id,
        'id | %s' % url_column_method_id,
        ],)

    foo_module = portal.foo_module
    foo_module.newContent(title=u'\xe9lisa')
    self.tic()

    request = get_request()
    request['here'] = portal.foo_module
    try:
      listbox.get_value('default', render_format='list', REQUEST=request)
    except UnicodeError as e:
      self.fail('Rendering failed: %s' % e)
    self.assertIn(u"http://example.com/?\xe9lisa", listbox.render(REQUEST=request))

  def test_05_EditSelectionWithFileUpload(self, quiet=quiet, run=run_all_test):
    """Listbox edits selection with request parameters. Special care must be
    taken for FileUpload objects that cannot be pickled, thus cannot be stored
    in the ZODB.
    """
    portal = self.getPortal()
    portal.ListBoxZuite_reset()
    listbox = portal.FooModule_viewFooList.listbox
    # XXX isn't Selection automatically created ?
    name = listbox.get_value('selection_name')
    portal.portal_selections.setSelectionFor(name, Selection(name))

    request = get_request()
    request['here'] = portal.foo_module
    request.form['my_file_upload'] = FileUpload(DummyFieldStorage())
    listbox.get_value('default', render_format='list', REQUEST=request)
    try:
      self.commit()
    except TypeError as e:
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
    self.tic()

    # Render the module in html
    request = get_request()
    request['here'] = portal.foo_module
    rendered_listbox = listbox.render(REQUEST=request)

    # Make sure that word is there
    self.assertEqual(rendered_listbox.find(word) > 0, True)

  def testCellKeywordInProxifiedListboxColumn(self):
    """
    Test that cell keyword is correctly interpreted when used in TALES
    to render a cell of a ListBox.
    First use cell in the ProxyField context, then use it in the listbox_xxx
    context
    """
    portal = self.getPortal()
    portal.ListBoxZuite_reset()

    form = portal.Foo_viewListBoxProxyField
    portal.foo_module.FooModule_createObjects()
    here = portal.foo_module['0']
    here.Foo_createObjects()

    request = get_request()
    request['here'] = here

    self.commit()

    listbox_title_column = form.listbox_title

    self.assertTrue(listbox_title_column.is_delegated('default'))
    self.assertEqual(listbox_title_column.get_recursive_tales('default')._text,
                      'python: cell.getTitle()')
    listboxline_list = form.listbox.get_value('default', render_format = 'list',
                                              REQUEST = request)
    first_item = dict(listboxline_list[1].getColumnItemList())
    self.assertEqual(first_item['title'], 'Title 0')

    # Use "cell" locally
    listbox_title_column.manage_tales_surcharged_xmlrpc(
        dict(default=TALESMethod('python: cell.getTitle() + " local"')))

    listboxline_list = form.listbox.get_value('default', render_format = 'list',
                                              REQUEST = request)
    first_item = dict(listboxline_list[1].getColumnItemList())
    self.assertEqual(first_item['title'], 'Title 0 local')

  def _helperExtraAndCssInListboxLine(self, field_type, editable):
    """
    Create a listbox_xxx field, in the hidden group, that defines
    identifiable CSS classes and extra properties.
      - field_type: type of the field which is created
      - editable: boolean, defines if the field should be defined as editable

    Render the field in the listbox, and check that CSS and extra are
    present in the rendered HTML

    Field names and Ids are generated to be unique for each
    (field_type, editable) entry.
    """
    portal = self.getPortal()
    portal.ListBoxZuite_reset()

    field_name = field_type.lower()
    if editable:
      field_name += '_editable'
    field_id = 'listbox_' + field_name

    # Reset listbox properties
    listbox = portal.FooModule_viewFooList.listbox
    listbox.ListBox_setPropertyList(
      field_list_method = 'portal_catalog',
      field_columns = ['%s | Check extra' % field_name,],
    )

    form = portal.FooModule_viewFooList
    form.manage_addField(field_id, field_name, field_type)
    field = getattr(form, field_id)

    word = '%s_dummy_%%s_to_check_for_in_listbox_test' % field_name
    extra = word % 'extra'
    css_class = word % 'css_class'
    field.values['extra'] = "alt='%s'" % extra
    field.values['css_class'] = css_class
    field.values['default'] = '42'
    field.values['editable'] = editable
    form.groups['bottom'].remove(field_id)
    form.groups['hidden'].append(field_id)

    # Create an new empty object with a list property
    foo_module = portal.foo_module
    foo_module.newContent()

    # Reindex
    self.tic()

    # Render the module in html
    request = get_request()
    request['here'] = portal.foo_module
    rendered_listbox = listbox.render(REQUEST=request)

    if editable:
      editable_text = 'An editable'
    else:
      editable_text = 'A non-editable'
    error_msg = "%s %s used as a listbox cell does not render properly the " \
        "'%%s' property" % (editable_text, field_type)

    # Make sure that the extras and css_classes are rendered
    self.assertTrue(extra in rendered_listbox, error_msg % 'extra')
    self.assertTrue(css_class in rendered_listbox, error_msg % 'css_class')

  def test_07_ExtraAndCssFieldsInIntegerField(self, quiet=0, run=run_all_test):
    """
      Check that css_class and extra fields are rendered when used in a
      listbox_xxx line, using IntegerField for the check.
    """
    self._helperExtraAndCssInListboxLine("IntegerField", True)
    self._helperExtraAndCssInListboxLine("IntegerField", False)

  def test_08_ExtraAndCssFieldsInLinesField(self, quiet=0, run=run_all_test):
    """
      Check that css_class and extra fields are rendered when used in a
      listbox_xxx line, using LinesField for the check.
    """
    self._helperExtraAndCssInListboxLine("LinesField", True)
    self._helperExtraAndCssInListboxLine("LinesField", False)

  def test_09_editablePropertyConfiguration(self):
    """
      Test editable behavior of delegated columns.
      A column is editable if and only if listbox_foo is editable AND foo is
      in the editable columns of the listbox.

      For example, if listbox_foo is defined as editable, without
      having column "foo" listed as editable in the listbox, the field should
      not be rendered as editable
    """
    self._helperEditableColumn(True, True, True)
    self._helperEditableColumn(False, False, False)
    self._helperEditableColumn(True, False, False)
    self._helperEditableColumn(False, True, False)

  def _helperEditableColumn(self, editable_in_listbox, editable_in_line,
      expected_editable):
    portal = self.getPortal()
    portal.ListBoxZuite_reset()

    field_name = 'editableproperty_%s_%s' \
                    % (editable_in_listbox, editable_in_line)
    field_name = field_name.lower()
    field_id = 'listbox_%s' % field_name

    # Reset listbox properties
    listbox = portal.FooModule_viewFooList.listbox
    kw = dict(
      field_list_method = 'portal_catalog',
      field_columns = ['%s | Check extra' % field_name,],
    )
    if editable_in_listbox:
      kw['field_editable_columns'] = '%s | Check extra' % field_name

    listbox.ListBox_setPropertyList(**kw)


    form = portal.FooModule_viewFooList
    form.manage_addField(field_id, field_name, "StringField")
    field = getattr(form, field_id)

    field.values['default'] = '42'
    field.values['editable'] = editable_in_line
    form.groups['bottom'].remove(field_id)
    form.groups['hidden'].append(field_id)

    # Create an new empty object with a list property
    foo_module = portal.foo_module
    foo_module.newContent()

    # Reindex
    self.tic()

    # Render the module in html
    request = get_request()
    request['here'] = portal.foo_module
    rendered_listbox = listbox.render(REQUEST=request)

    html = etree.HTML(rendered_listbox)
    # When a StringField is editable, it is rendered as an input
    # with name: "field_%(field_id)s_%(object_id)s"
    editable_field_list = html.xpath(
                            '//input[starts-with(@name, $name)]',
                            name='field_%s_' % field_id,
                          )

    msg = "editable_in_listbox: %s, editable_in_line: %s" \
            % (editable_in_listbox, editable_in_line)
    self.assertEqual(len(editable_field_list) == 1, expected_editable, msg)

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
    self.assertEqual(1, len(line_list))
    self.assertEqual('Object Title', line_list[0].getColumnProperty('title'))
    html = listbox.render(REQUEST=request)
    self.assertTrue('Object Title' in html, html)

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
    portal.manage_addProduct['ERP5Form'].addERP5Form('Test_view', 'View')
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
    self.assertTrue(isinstance(line_list, list))

    title_line = line_list[0]
    self.assertTrue(title_line.isTitleLine())

    # title of columns is the value overloaded by the proxy field.
    self.assertEqual([('proxy_value', 'Proxy')],
                      title_line.getColumnItemList())

  def test_ListStyleColumnsSelections(self):
    """
      Test list style columns selections.
    """
    def getListBoxRenderer(listbox):
      return ListBoxHTMLRenderer(self, listbox, request)

    portal = self.getPortal()
    portal.ListBoxZuite_reset()
    listbox = portal.FooModule_viewFooList.listbox
    listbox.ListBox_setPropertyList(
      field_style_columns=['title | thumbnail_Title',
                           'thumbnail | thumbnail_Thumbnail',
                           'getIconAsHTML | search_Icon',
                           'getSummaryAsHTML | search_Summary',
                           'B | rss_title',
                           'C | rss_description'],)
    request = get_request()

    # explicitly setting (dynamically) renderer columns list
    renderer = getListBoxRenderer(listbox)
    renderer.setDisplayedColumnIdList(['title', 'id'])
    self.assertSameSet([('title', u'Title'), ('id', u'ID')],
                       renderer.getSelectedColumnList())

    # default(no list_style)
    self.assertEqual(getListBoxRenderer(listbox).getDefaultDisplayStyle(),
      getListBoxRenderer(listbox).getListboxDisplayStyle())
    self.assertSameSet([('id', u'ID'), ('title', u'Title'), ('getQuantity', u'Quantity')],
                         getListBoxRenderer(listbox).getSelectedColumnList())

    request.set('list_style', 'search')
    self.assertEqual('search', getListBoxRenderer(listbox).getListboxDisplayStyle())
    self.assertSameSet([('getIconAsHTML', 'Icon'), ('getSummaryAsHTML', 'Summary')],
                         getListBoxRenderer(listbox).getSelectedColumnList())

    request.set('list_style', 'thumbnail')
    self.assertEqual('thumbnail', getListBoxRenderer(listbox).getListboxDisplayStyle())
    self.assertSameSet([('title', 'Title'), ('thumbnail', 'Thumbnail')],
                         getListBoxRenderer(listbox).getSelectedColumnList())

    # set different than 'table' listbox default mode and check variations
    listbox.ListBox_setPropertyList(
             field_default_display_style='search',
             field_style_columns=['title | thumbnail_Title',
                                  'thumbnail | thumbnail_Thumbnail',
                                  'getIconAsHTML | search_Icon',
                                  'getSummaryAsHTML | search_Summary',
                                  'B | rss_title',
                                  'C | rss_description'],)
    request.set('list_style', 'search')
    self.assertEqual('search', getListBoxRenderer(listbox).getListboxDisplayStyle())
    self.assertSameSet([('getIconAsHTML', 'Icon'), ('getSummaryAsHTML', 'Summary')],
                         getListBoxRenderer(listbox).getSelectedColumnList())

    request.set('list_style', 'thumbnail')
    self.assertEqual('thumbnail', getListBoxRenderer(listbox).getListboxDisplayStyle())
    self.assertSameSet([('title', 'Title'), ('thumbnail', 'Thumbnail')],
                         getListBoxRenderer(listbox).getSelectedColumnList())

    request.set('list_style', 'table')
    self.assertSameSet([('id', u'ID'), ('title', u'Title'), ('getQuantity', u'Quantity')],
                         getListBoxRenderer(listbox).getSelectedColumnList())

  def test_ListboxRequestParameterPropagandation(self):
    """
      Test that rendering a listbox field will set respective form & field_id of current form
      in REQUEST for further usage by used by litsbox's columns methods.
    """
    portal = self.getPortal()
    request = get_request()
    request['here'] = portal.foo_module
    portal.ListBoxZuite_reset()
    form = portal.FooModule_viewFooList
    self.assertEqual(None, request.get('listbox_form_id'))
    form.render()
    self.assertEqual(form.getId(), request.get('listbox_form_id'))
    self.assertEqual(form.listbox.getId(), request.get('listbox_field_id'))

  def test_query_timeout(self):
    portal = self.getPortal()
    portal.ListBoxZuite_reset()

    # Set short enough publisher timeout configuration
    import Products.ERP5Type.Timeout
    Products.ERP5Type.Timeout.publisher_timeout = 2.0

    # We create a Z SQL Method that takes too long
    list_method_id = 'ListBox_zSlowQuery'
    portal.portal_skins.custom.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod(
      id=list_method_id,
      title='',
      connection_id='erp5_sql_connection',
      arguments='',
      template="SELECT uid, path FROM catalog WHERE SLEEP(3) = 0 AND path='%s'" % portal.foo_module.getPath(),
    )
    portal.changeSkin(None)

    # set the listbox to use this as list method
    listbox = portal.FooModule_viewFooList.listbox
    listbox.ListBox_setPropertyList(
      field_list_method=list_method_id,
      field_count_method='',
    )

    # access the form
    result = self.publish(
      '%s/FooModule_viewFooList' % portal.foo_module.absolute_url(relative=True),
      '%s:%s' % (self.manager_username, self.manager_password),
    )
    self.assertEqual(result.getStatus(), 500)
    body = result.getBody()
    self.assertIn('Error Type: TimeoutReachedError', body)
    self.assertIn('Error Value: 1969: Query execution was interrupted (max_statement_time exceeded): SET STATEMENT', body)

  def test_zodb_timeout(self):
    portal = self.getPortal()
    portal.ListBoxZuite_reset()

    # Set short enough publisher timeout configuration
    import Products.ERP5Type.Timeout
    Products.ERP5Type.Timeout.publisher_timeout = 2.0

    # We create a Z SQL Method that takes too long
    list_method_id = 'ListBox_getSlowObjectValues'
    createZODBPythonScript(
        portal.portal_skins.custom,
        list_method_id,
        'selection=None, **kw',
        """
from time import sleep
sleep(3)
return context.objectValues()
        """)

    # set the listbox to use this as list method
    listbox = portal.FooModule_viewFooList.listbox
    listbox.ListBox_setPropertyList(
      field_list_method=list_method_id,
      field_count_method='',
    )

    portal.foo_module.newContent()

    # access the form
    result = self.publish(
      '%s/FooModule_viewFooList' % portal.foo_module.absolute_url(relative=True),
      '%s:%s' % (self.manager_username, self.manager_password),
    )
    self.assertEqual(result.getStatus(), 500)
    self.assertIn('Error Type: TimeoutReachedError', result.getBody())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestListBox))
  return suite

