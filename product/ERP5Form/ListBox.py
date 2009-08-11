##############################################################################
#
# Copyright (c) 2002,2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import sys
from OFS.Traversable import NotFound
from AccessControl import ClassSecurityInfo, Unauthorized
from Products.Formulator.DummyField import fields
from Products.Formulator import Widget, Validator
from Products.Formulator.Field import ZMIField
from Products.Formulator.Errors import FormValidationError, ValidationError
from Selection import Selection, DomainSelection
from SelectionTool import createFolderMixInPageSelectionMethod
from Products.ERP5Type.Utils import getPath
from Products.ERP5Type.Document import newTempBase
from Products.CMFCore.utils import getToolByName
from Products.ZSQLCatalog.zsqlbrain import ZSQLBrain
from Products.ERP5Type.Message import Message

from Acquisition import aq_base, aq_self
from zLOG import LOG, WARNING
from ZODB.POSException import ConflictError

from Globals import InitializeClass, Acquisition, get_request
from Products.PythonScripts.Utility import allow_class
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

import md5
import cgi

# For compatibility with Python 2.3.
try:
  set
except NameError:
  from sets import Set as set

class MethodWrapper:
  def __init__(self, context, method_name):
    self.context = context
    self.method_name = self.__name__ = method_name

  def __call__(self, *args, **kw):
    raise NotImplementedError

class ListMethodWrapper(MethodWrapper):
  """This class wraps list methods so that they behave like portal_catalog.
  """
  def __call__(self, *args, **kw):
    brain_list = []
    for obj in getattr(self.context, self.method_name)(*args, **kw):
      brain = ZSQLBrain(None, None).__of__(obj)
      brain.uid = obj.getUid()
      brain.path = obj.getPath()
      brain_list.append(brain)
    return brain_list

class CatalogMethodWrapper(MethodWrapper):
  """This class wraps catalog list methods so that they discard a pre-defined
     set of parameters which are part of the Selection API but not in
     SQLCatalog API.
  """
  def __call__(self, *args, **kw):
    for parameter_id in ('selection', 'selection_name', 'select_columns',
      'reset', 'selection_index', 'list_selection_name', 'list_start',
      'list_lines', 'listbox_list_start', 'listbox_uid', 'listbox_nextPage',
      'listbox_previousPage',
      # Also strip common HTML field names
      # XXX: I'm not sure if those values really belong to here
      'md5_object_uid_list', 'cancel_url', 'listbox_list_selection_name',
      'form_id', 'select_language', 'select_favorite', 'select_module',
      'select_jump', 'select_action', 'Base_doSelect'):
      kw.pop(parameter_id, None)
    # Strip all entries which have an empty string as value (ie, an empty
    # field).
    # XXX: I'm not sure if this filtering really belongs to here.
    # It is probably needed at a more generic level (Forms ? Selection ?), or
    # even a more specific one (limited to HTML ?)...
    for key, value in kw.items():
      if value == '':
        kw.pop(key)
    return getattr(self.context, self.method_name)(*args, **kw)

class ReportTree:
  """This class describes a report tree.
  """
  def __init__(self, obj = None, is_pure_summary = False, depth = 0, is_open = False,
               selection_domain = None, exception_uid_list = None, base_category = None):
    self.obj = obj
    self.is_pure_summary = is_pure_summary
    self.depth = depth
    self.is_open = is_open
    self.selection_domain = selection_domain
    self.exception_uid_list = exception_uid_list
    if exception_uid_list is None:
      self.exception_uid_set = None
    else:
      self.exception_uid_set = set(exception_uid_list)
    self.base_category = base_category

    relative_url = obj.getRelativeUrl()
    if base_category is not None and not relative_url.startswith(base_category + '/'):
      self.domain_url = '%s/%s' % (base_category, relative_url)
    else:
      self.domain_url = relative_url

allow_class(ReportTree)

class ReportSection:
  """This class describes a report section.
  """
  def __init__(self, is_summary = False, object_list = (), object_list_len = 0,
               is_open = False, selection_domain = None, context = None, offset = 0,
               depth = 0, domain_title = None):
    self.is_summary = is_summary
    self.object_list = object_list
    self.object_list_len = object_list_len
    self.is_open = is_open
    self.selection_domain = selection_domain
    self.context = context
    self.offset = offset
    self.depth = depth
    self.domain_title = domain_title

class ListBoxWidget(Widget.Widget):
    """
        ListBox widget

        The ListBox widget allows to display a collection of objects in a form.
        The ListBox widget can be used for many applications:

        1- show the content of a folder by providing a list of meta_types
           and eventually a sort order

        2- show the content of a relation by providing the name of the relation,
           a list of meta_types and eventually a sort order

        3- show the result of a search request by selecting a query and
           providing parameters for that query (and eventually a sort order)

        In all 3 cases, a parameter to hold the current start item must be
        stored somewhere, typically in a selection object.

        Parameters in case 3 should stored in a selection object which allows a per user
        per PC storage.

        ListBox uses the following control variables

        - sort_by -- the id to sort results

        - sort_order -- the order of sorting
    """
    # Define Properties for ListBoxWidget.
    property_names = list(Widget.Widget.property_names)

    # Default has no meaning in ListBox.
    property_names.remove('default')

    lines = fields.IntegerField('lines',
                                title='Lines',
                                description=(
        "The number of lines of this list. Required."),
                                default=20,
                                required=1)
    property_names.append('lines')

    columns = fields.ListTextAreaField('columns',
                                 title="Columns",
                                 description=(
        "A list of attributes names to display. Required."),
                                 default=[],
                                 required=1)
    property_names.append('columns')

    all_columns = fields.ListTextAreaField('all_columns',
                                 title="More Columns",
                                 description=(
        "An optional list of attributes names to display."),
                                 default=[],
                                 required=0)
    property_names.append('all_columns')

    search_columns = fields.ListTextAreaField('search_columns',
                                 title="Searchable Columns",
                                 description=(
        "An optional list of columns to search."),
                                 default=[],
                                 required=0)
    property_names.append('search_columns')

    sort_columns = fields.ListTextAreaField('sort_columns',
                                 title="Sortable Columns",
                                 description=(
        "An optional list of columns to sort."),
                                 default=[],
                                 required=0)
    property_names.append('sort_columns')

    sort = fields.ListTextAreaField('sort',
                                 title='Default Sort',
                                 description=('The default sort keys and order'),
                                 default=[],
                                 required=0)
    property_names.append('sort')

    list_method = fields.MethodField('list_method',
                                 title='List Method',
                                 description=('The method to use to list'
                                              'objects'),
                                 default='',
                                 required=0)
    property_names.append('list_method')

    count_method = fields.MethodField('count_method',
                                 title='Count Method',
                                 description=('The method to use to count'
                                              'objects'),
                                 default='',
                                 required=0)
    property_names.append('count_method')

    stat_method = fields.MethodField('stat_method',
                                 title='Stat Method',
                                 description=('The method to use to stat'
                                              'objects'),
                                 default='',
                                 required=0)
    property_names.append('stat_method')

    row_css_method = fields.MethodField('row_css_method',
                                 title='Row CSS Method',
                                 description=('The method to set the css class name of a row'),
                                 default='',
                                 required=0)
    property_names.append('row_css_method')

    selection_name = fields.StringField('selection_name',
                                 title='Selection Name',
                                 description=('The name of the selection to store'
                                              'params of selection'),
                                 default='',
                                 required=1)
    property_names.append('selection_name')

    meta_types = fields.ListTextAreaField('meta_types',
                                 title="Meta Types",
                                 description=(
        "Meta Types of objects to list. Required."),
                                 default=[],
                                 required=0)
    property_names.append('meta_types')

    portal_types = fields.ListTextAreaField('portal_types',
                                 title="Portal Types",
                                 description=(
        "Portal Types of objects to list. Required."),
                                 default=[],
                                 required=0)
    property_names.append('portal_types')

    # XXX Do we still need this?
    default_params = fields.ListTextAreaField('default_params',
                                 title="Default Parameters",
                                 description=(
        "Default Parameters for the List Method."),
                                 default=[],
                                 required=0)
    property_names.append('default_params')

    search = fields.CheckBoxField('search',
                                 title='Search Row',
                                 description=('Search Row'),
                                 default=0,
                                 required=0)
    property_names.append('search')

    select = fields.CheckBoxField('select',
                                 title='Select Column',
                                 description=('Select Column'),
                                 default=0,
                                 required=0)
    property_names.append('select')

    anchor = fields.CheckBoxField('anchor',
                                  title='Anchor Column',
                                  description=(
      'An optional anchor column which can always clickable.'),
                                  default=0,
                                  required=0)
    property_names.append('anchor')

    hide_rows_on_no_search_criterion = \
      fields.CheckBoxField('hide_rows_on_no_search_criterion', \
                           title = 'Hide Rows (On No Search Criterion)', \
                           description = ('Hide listbox rows if no search criterion is provided by user'), \
                                          default = 0, \
                                          required = 0)
    property_names.append('hide_rows_on_no_search_criterion')

    editable_columns = fields.ListTextAreaField('editable_columns',
                                 title="Editable Columns",
                                 description=(
        "An optional list of columns which can be modified."),
                                 default=[],
                                 required=0)
    property_names.append('editable_columns')

    stat_columns = fields.ListTextAreaField('stat_columns',
                                 title="Stat Columns",
                                 description=(
        "An optional list of columns which can be used for statistics."),
                                 default=[],
                                 required=0)
    property_names.append('stat_columns')

    url_columns = fields.ListTextAreaField('url_columns',
                                 title="URL Columns",
                                 description=(
        "An optional list of columns which can provide a custom URL."),
                                 default=[],
                                 required=0)
    property_names.append('url_columns')

    untranslatable_columns = fields.ListTextAreaField('untranslatable_columns',
                                 title="Untranslatable Columns",
                                 description=(
        "An optional list of columns titles which should not be translated."),
                                 default=[],
                                 required=0)
    property_names.append('untranslatable_columns')

    # XXX do we still need this?
    global_attributes = fields.ListTextAreaField('global_attributes',
                                 title="Global Attributes",
                                 description=(
        "An optional list of attributes which are set by hidden fields and which are applied to each editable column."),
                                 default=[],
                                 required=0)
    property_names.append('global_attributes')

    domain_tree = fields.CheckBoxField('domain_tree',
                                 title='Domain Tree',
                                 description=('Selection Tree'),
                                 default=0,
                                 required=0)
    property_names.append('domain_tree')

    domain_root_list = fields.ListTextAreaField('domain_root_list',
                                 title="Domain Root",
                                 description=(
        "A list of domains which define the possible root."),
                                 default=[],
                                 required=0)
    property_names.append('domain_root_list')

    report_tree = fields.CheckBoxField('report_tree',
                                 title='Report Tree',
                                 description=('Report Tree'),
                                 default=0,
                                 required=0)
    property_names.append('report_tree')

    report_root_list = fields.ListTextAreaField('report_root_list',
                                 title="Report Root",
                                 description=(
        "A list of domains which define the possible root."),
                                 default=[],
                                 required=0)
    property_names.append('report_root_list')

    list_action = fields.StringField('list_action',
                                 title='List Action',
                                 description=('The id of the object action'
                                              ' to display the current list'),
                                 default='list',
                                 required=0)
    property_names.append('list_action')

    page_template = fields.StringField('page_template',
                                 title='Page Template',
                                 description=('The id of a Page Template'
                                              ' to render the ListBox'),
                                 default='',
                                 required=0)
    property_names.append('page_template')

    def render_view(self, field, value, REQUEST=None, render_format='html', key='listbox', render_prefix=None):
        """
          Render a ListBox in read-only.
        """
        if REQUEST is None: REQUEST=get_request()
        return self.render(field, key, value, REQUEST, render_format=render_format,
                           render_prefix=render_prefix)

    def render(self, field, key, value, REQUEST, render_format='html',
               render_prefix=None):
        """
          This is where most things happen. This method renders a list
          of items

          render_format allows to produce either HTML (default)
          or produce a generic 'list' format which can be converted by page templates
          or dtml into various formats (ex. PDF, CSV, OpenOffice, etc.)

          the 'list' format includes additional metainformation

          - depth in a report tree (ex. 0, 1, 2, etc.)

          - nature of the line (ex. stat or nonstat)

          - identification of the tree (ex. relative_url)

          - uid if any (to allow future import)

          - etc.

          which is intended to simplify operation with a spreadsheet or a pagetemplate
        """
        if REQUEST is None:
          REQUEST = get_request()
        if render_format == 'list':
          renderer = ListBoxListRenderer(self, field, REQUEST,
                                         render_prefix=render_prefix)
        else:
          renderer = ListBoxHTMLRenderer(self, field, REQUEST, render_prefix=render_prefix)

        return renderer()

ListBoxWidgetInstance = ListBoxWidget()

def lazyMethod(func):
  """Return a function which stores a computed value in an instance
  at the first call.
  """
  key = '_cache_' + str(id(func))
  def decorated(self, *args, **kw):
    try:
      return getattr(self, key)
    except AttributeError:
      result = func(self, *args, **kw)
      setattr(self, key, result)
      return result
  return decorated

class ListBoxRenderer:
  """This class deals with rendering of a ListBox field.

  In ListBox, rendering is not only viewing but also setting parameters in a selection
  and a request object.
  """

  def __init__(self, widget = None, field = None, REQUEST = None, render_prefix=None, **kw):
    """Store the parameters for later use.
    """
    self.widget = widget
    self.field = field
    self.request = REQUEST
    self.render_prefix = render_prefix

  def getPhysicalPath(self):
    """
      Return the path of form we render.
      This function is required to be able to use ZopeProfiler product with
      listbox.
    """
    return self.field.getPhysicalPath()

  def getLineClass(self):
    """Return a class object for a line. This must be overridden.
    """
    raise NotImplementedError, "getLineClass must be overridden in a subclass"

  # Here, define many getters which cache the results for better performance.

  def getContext(self):
    """Return the context of rendering this ListBox.
    """
    value = self.request.get('here')
    if value is None:
      value = self.getForm().aq_parent
    return value

  getContext = lazyMethod(getContext)

  def getForm(self):
    """Return the form which contains the ListBox.
    """
    return self.field.aq_parent

  getForm = lazyMethod(getForm)

  def getEncoding(self):
    """Retutn the encoding of strings in the fields. Default to UTF-8.
    """
    return self.getPortalObject().getProperty('management_page_charset', 'utf-8')

  getEncoding = lazyMethod(getEncoding)

  def isReset(self):
    """Determine if the ListBox should be reset.
    """
    reset = self.request.get('reset', 0)
    return (reset not in (0, '0'))

  isReset = lazyMethod(isReset)

  def getFieldErrorDict(self):
    """Return a dictionary of errors.
    """
    return self.request.get('field_errors', {})

  getFieldErrorDict = lazyMethod(getFieldErrorDict)

  def getUrl(self):
    """
      Return a requested URL.
      Generate the URL from context and request because self.request['URL']
      might contain a function name, which would make all redirections call
      the function - which both we don't want and will probably crash.
    """
    return '%s/%s' % (self.getContext().absolute_url(),
                      self.request.other.get('current_form_id', 'view'))

  getUrl = lazyMethod(getUrl)

  def getRequestedSelectionName(self):
    """Return a selection name which may be passed by a request.
    If not present, return "default". This selection can be different from the selection
    defined in the ListBox.
    """
    selection_name = self.request.get('selection_name', 'default')

    # This is a workaround, as selection_name becomes a list or tuple sometimes.
    # XXX really? why?
    if not isinstance(selection_name, str):
      selection_name = selection_name[0]

    return selection_name

  getRequestedSelectionName = lazyMethod(getRequestedSelectionName)

  def getSelectionIndex(self):
    """Return the index of a requested selection, or None if not specified.
    """
    return self.request.get('selection_index', None)

  getSelectionIndex = lazyMethod(getSelectionIndex)

  def getReportDepth(self):
    """Return the depth of reports, or None if not specified.
    """
    return self.request.get('report_depth', None)

  getReportDepth = lazyMethod(getReportDepth)

  def getPortalObject(self):
    """Return the portal object.
    """
    return self.getContext().getPortalObject()

  getPortalObject = lazyMethod(getPortalObject)

  def getPortalUrlString(self):
    """Return the URL of the portal as a string.
    """
    return self.getPortalObject().portal_url()

  getPortalUrlString = lazyMethod(getPortalUrlString)

  def getCategoryTool(self):
    """Return the Category Tool.
    """
    return self.getPortalObject().portal_categories

  getCategoryTool = lazyMethod(getCategoryTool)

  def getDomainTool(self):
    """Return the Domain Tool.
    """
    return self.getPortalObject().portal_domains

  getDomainTool = lazyMethod(getDomainTool)

  def getCatalogTool(self):
    """Return the Catalog Tool.
    """
    return self.getPortalObject().portal_catalog

  getCatalogTool = lazyMethod(getCatalogTool)

  def getSelectionTool(self):
    """Return the Selection Tool.
    """
    return self.getPortalObject().portal_selections

  getSelectionTool = lazyMethod(getSelectionTool)

  def getPrefixedString(self, string):
    prefix = self.render_prefix
    if prefix is None:
      result = string
    else:
      result = '%s_%s' % (prefix, string)
    return result

  def getId(self):
    """Return the id of the field. Usually, "listbox".
       The prefix will automatically be added
    """
    return self.getPrefixedString(self.field.id)

  getId = lazyMethod(getId)

  def getUnprefixedId(self):
    """Return the id of the field. Usually, "listbox".
    """
    return self.field.id

  getUnprefixedId = lazyMethod(getUnprefixedId)

  def getTitle(self):
    """Return the title. Make sure that it is in unicode.
    """
    return unicode(self.field.get_value('title'), self.getEncoding())

  getTitle = lazyMethod(getTitle)

  def getMaxLineNumber(self):
    """Return the maximum number of lines shown in a page.
    This must be overridden in subclasses.
    """
    raise NotImplementedError, "getMaxLineNumber must be overridden in a subclass"

  def showSearchLine(self):
    """Return a boolean that represents whether a search line is displayed or not.
    """
    return self.field.get_value('search')

  showSearchLine = lazyMethod(showSearchLine)

  def showSelectColumn(self):
    """Return a boolean that represents whether a select column is displayed or not.
    """
    return self.field.get_value('select')

  showSelectColumn = lazyMethod(showSelectColumn)

  def showAnchorColumn(self):
    """Return a boolean that represents whether a anchor column is displayed or not.
    """
    return self.field.get_value('anchor')

  showAnchorColumn = lazyMethod(showAnchorColumn)

  def isHideRowsOnNoSearchCriterion(self):
    """
      Return a boolean that represents whether search rows are shown or not.
    """
    REQUEST = self.request
    hide_rows_on_no_search_criterion = \
                            self.field.get_value('hide_rows_on_no_search_criterion')
    if not hide_rows_on_no_search_criterion:
      # we show all rows and do not care to hide anything
      return 0

    # Always display lines in report mode
    if self.isReportTreeMode():
      return 0

    # In domain mode, returns lines only if a domain is selected
    if self.isDomainTreeMode():
      if self.getDomainSelection():
        return 0

    # ignore_hide_rows parameter force to display the content
    ignore_hide_rows = REQUEST.get('ignore_hide_rows', 0)
    if ignore_hide_rows:
      return 0

    # we could hide rows only if missing in request or selection search criterions
    selection_params = self.getSelection().getParams()

    # Try to get workflow state parameter, in order to always allow worklist display
    # guess all column names from catalog schema
    possible_state_list = [column_name for column_name in
         self.getPortalObject().portal_catalog.getSQLCatalog().getColumnMap() if
         column_name.endswith('state') and '.' not in column_name]
    for state_var in possible_state_list:
      workflow_state_criterion = REQUEST.get(state_var,
                                        selection_params.get(state_var, None))
      if workflow_state_criterion not in (None, ""):
        return 0

    listbox_searchable_column_id_list = [x[0] for x in self.getSearchValueList() \
                                           if x[0] is not None]

    for listbox_searchable_column_id in listbox_searchable_column_id_list:
      search_criterion = REQUEST.get(listbox_searchable_column_id, \
                                     selection_params.get(listbox_searchable_column_id, None))
      if search_criterion not in (None, "",) and not isinstance(search_criterion, dict):
        # search criterion is usually input by user by UI, ignore created automated 
        # by listbox_xxx form fields selection parameters as they do not represent
        # user input but rather a developer formating definition in form
        return 0
    return 1

  isHideRowsOnNoSearchCriterion = lazyMethod(isHideRowsOnNoSearchCriterion)

  def showStat(self):
    """Return a boolean that represents whether a stat line is displayed or not.

    FIXME: This is not very correct, because stat columns may define their own
    stat method independently.
    """
    return (self.getStatMethod() is not None) and (len(self.getStatColumnList()) > 0)

  showStat = lazyMethod(showStat)

  def isDomainTreeSupported(self):
    """Return a boolean that represents whether a domain tree is supported or not.
    """
    return (self.field.get_value('domain_tree') and len(self.getDomainRootList()) > 0)

  isDomainTreeSupported = lazyMethod(isDomainTreeSupported)

  def isReportTreeSupported(self):
    """Return a boolean that represents whether a report tree is supported or not.
    """
    return (self.field.get_value('report_tree') and len(self.getReportRootList()) > 0)

  isReportTreeSupported = lazyMethod(isReportTreeSupported)

  def isDomainTreeMode(self):
    """Return whether the current mode is domain tree mode or not.
    """
    return self.isDomainTreeSupported() and self.getSelection().domain_tree_mode

  isDomainTreeMode = lazyMethod(isDomainTreeMode)

  def isReportTreeMode(self):
    """Return whether the current mode is report tree mode or not.
    """
    return self.isReportTreeSupported() and self.getSelection().report_tree_mode

  isReportTreeMode = lazyMethod(isReportTreeMode)

  def getDefaultParamList(self):
    """Return the list of default parameters.
    """
    return self.field.get_value('default_params')

  getDefaultParamList = lazyMethod(getDefaultParamList)

  def getListMethodName(self):
    """Return the name of the list method. If not defined, return None.
    """
    list_method = self.field.get_value('list_method')
    try:
      name = getattr(list_method, 'method_name')
    except AttributeError:
      name = list_method
    return name or None

  getListMethodName = lazyMethod(getListMethodName)

  def getCountMethodName(self):
    """Return the name of the count method. If not defined, return None.
    """
    count_method = self.field.get_value('count_method')
    try:
      name = getattr(count_method, 'method_name')
    except AttributeError:
      name = count_method
    return name or None

  getCountMethodName = lazyMethod(getCountMethodName)

  def getStatMethodName(self):
    """Return the name of the stat method. If not defined, return None.
    """
    stat_method = self.field.get_value('stat_method')
    try:
      name = getattr(stat_method, 'method_name')
    except AttributeError:
      name = stat_method
    return name or None

  getStatMethodName = lazyMethod(getStatMethodName)

  def getRowCSSMethodName(self):
    """Return the name of the row CSS method. If not defined, return None.
    """
    row_css_method = self.field.get_value('row_css_method')
    try:
      name = getattr(row_css_method, 'method_name')
    except AttributeError:
      name = row_css_method
    return name or None

  getRowCSSMethodName = lazyMethod(getRowCSSMethodName)
  
  def getSelectionName(self):
    """Return the selection name.
    """
    return self.getPrefixedString(self.field.get_value('selection_name'))

  getSelectionName = lazyMethod(getSelectionName)

  def getMetaTypeList(self):
    """Return the list of meta types for filtering. Return None when empty.
    """
    meta_types = [c[0] for c in self.field.get_value('meta_types')]
    return meta_types or None

  getMetaTypeList = lazyMethod(getMetaTypeList)

  def getPortalTypeList(self):
    """Return the list of portal types for filtering. Return None when empty.
    """
    portal_types = [c[0] for c in self.field.get_value('portal_types')]
    return portal_types or None

  getPortalTypeList = lazyMethod(getPortalTypeList)

  def getColumnList(self):
    """Return the columns. Make sure that the titles are in unicode.
    """
    columns = self.field.get_value('columns')
    return [(str(c[0]), unicode(c[1], self.getEncoding())) for c in columns]

  getColumnList = lazyMethod(getColumnList)

  def getAllColumnList(self):
    """Return the all columns. Make sure that the titles are in unicode.
    """
    all_column_list = list(self.getColumnList())
    all_column_id_set = set([c[0] for c in all_column_list])
    all_column_list.extend([(str(c[0]), unicode(c[1], self.getEncoding())) \
                              for c in self.field.get_value('all_columns') \
                              if c[0] not in all_column_id_set])
    return all_column_list

  getAllColumnList = lazyMethod(getAllColumnList)

  def getStatColumnList(self):
    """Return the stat columns. Fall back to all the columns if empty.
    """
    stat_columns = self.field.get_value('stat_columns')
    if stat_columns:
      stat_column_list = [(str(c[0]), unicode(c[1], self.getEncoding())) for c in stat_columns]
    else:
      stat_column_list = [(c[0], c[0]) for c in self.getAllColumnList()]
    return stat_column_list

  getStatColumnList = lazyMethod(getStatColumnList)

  def getUrlColumnList(self):
    """Return the url columns. Make sure that it is an empty list, when not defined.
    """
    url_columns = self.field.get_value('url_columns')
    return url_columns or []

  def getUntranslatableColumnList(self):
    """Return the untranslatable columns. Make sure that it is an empty list, 
    when not defined.
    """
    untranslatable_columns = self.field.get_value('untranslatable_columns')
    return untranslatable_columns or []

  getUrlColumnList = lazyMethod(getUrlColumnList)

  def getDefaultSortColumnList(self):
    """Return the default sort columns.
    """
    return self.field.get_value('sort')

  getDefaultSortColumnList = lazyMethod(getDefaultSortColumnList)

  def getDomainRootList(self):
    """Return the domain root list. Make sure that the titles are in unicode.
    """
    domain_root_list = self.field.get_value('domain_root_list')
    return [(str(c[0]), unicode(c[1], self.getEncoding())) for c in domain_root_list]

  getDomainRootList = lazyMethod(getDomainRootList)

  def getReportRootList(self):
    """Return the report root list. Make sure that the titles are in unicode.
    """
    report_root_list = self.field.get_value('report_root_list')
    return [(str(c[0]), unicode(c[1], self.getEncoding())) for c in report_root_list]

  getReportRootList = lazyMethod(getReportRootList)

  def getSearchColumnIdSet(self):
    """Return the set of the ids of the search columns. Fall back to the catalog schema, if not defined.
    """
    search_columns = self.field.get_value('search_columns')
    if search_columns:
      search_column_id_list = [c[0] for c in search_columns]
    else:
      search_column_id_list = self.getCatalogTool().schema()
    return set(search_column_id_list)

  getSearchColumnIdSet = lazyMethod(getSearchColumnIdSet)

  def getSortColumnIdSet(self):
    """Return the set of the ids of the sort columns. Fall back to search column ids, if not defined.
    """
    sort_columns = self.field.get_value('sort_columns')
    if sort_columns:
      sort_column_id_set = set([c[0] for c in sort_columns])
    else:
      sort_column_id_set = self.getSearchColumnIdSet()
    return sort_column_id_set

  getSortColumnIdSet = lazyMethod(getSortColumnIdSet)

  def getEditableColumnIdSet(self):
    """Return the set of the ids of the editable columns.
    """
    editable_columns = self.field.get_value('editable_columns')
    return set([c[0] for c in editable_columns])

  getEditableColumnIdSet = lazyMethod(getEditableColumnIdSet)

  def getListActionUrl(self):
    """Return the URL of the list action.
    """
    list_action = self.field.get_value('list_action')
    if '/' in list_action:
      # This is a 'real' URL
      return list_action
    else:
      # This is only a method name. Let us build the URL
      list_action_part_list = [self.getContext().absolute_url(), '/', list_action]
    if '?' in list_action_part_list[-1]:
      list_action_part_list.append('&reset=1')
    else:
      list_action_part_list.append('?reset=1')
    if self.request.get('ignore_layout', None):
      list_action_part_list.append('&ignore_layout:int=1')
    return ''.join(list_action_part_list)

  getListActionUrl = lazyMethod(getListActionUrl)

  # Whether the selection object is initialized.
  is_selection_initialized = False

  def getSelection(self):
    """FIXME: Tweak a selection and return the selection object.
    This code depends on the implementation of Selection too much.
    In the future, the API of SelectionTool should be refactored and
    ListBox should not use Selection directly.
    """
    selection_tool = self.getSelectionTool()
    selection_name = self.getSelectionName()
    selection = selection_tool.getSelectionFor(selection_name, REQUEST = self.request)

    if self.is_selection_initialized:
      return selection

    # Create a selection, if not present, with the default sort order.
    if selection is None:
      selection = Selection(params = dict(self.getDefaultParamList()), default_sort_on = self.getDefaultSortColumnList())
      selection = selection.__of__(selection_tool)
    # Or make sure all sort arguments are valid.
    else:
      # Reset the selection, if specified.
      if self.isReset():
        selection_tool.setSelectionToAll(selection_name)
        selection_tool.setSelectionSortOrder(selection_name, sort_on = [])

      # Modify the default sort index every time, because it may change immediately.
      selection.edit(default_sort_on = self.getDefaultSortColumnList())

      # Filter out non-sortable items.
      sort_column_id_set = self.getSortColumnIdSet()
      sort_list = [c for c in selection.sort_on if c[0] in sort_column_id_set]
      if len(selection.sort_on) != len(sort_list):
        selection.sort_on = sort_list

    if getattr(selection, 'flat_list_mode', None) is None:
      # Initialize the render mode. Choose flat list mode by default.
      selection.edit(flat_list_mode = 1, domain_tree_mode = 0, report_tree_mode = 0)

    # Remember if the items have to be displayed for report tree mode.
    is_report_opened = self.request.get('is_report_opened', selection.isReportOpened())
    selection.edit(report_opened = is_report_opened)

    self.is_selection_initialized = True

    return selection

  getSelection = lazyMethod(getSelection)

  def getCheckedUidList(self):
    """Return the list of checked uids.
    """
    return self.getSelection().getCheckedUids()

  getCheckedUidList = lazyMethod(getCheckedUidList)

  def getCheckedUidSet(self):
    """Return the set of checked uids.
    """
    return set(self.getCheckedUidList())

  getCheckedUidSet = lazyMethod(getCheckedUidSet)

  def getSelectedColumnList(self):
    """Return the list of selected columns.
    """
    return self.getSelectionTool().getSelectionColumns(self.getSelectionName(),
                                                       columns = self.getColumnList(),
                                                       REQUEST = self.request)

  getSelectedColumnList = lazyMethod(getSelectedColumnList)

  def getColumnAliasList(self):
    """Return the list of column aliases for SQL, because SQL does not allow a symbol to contain dots.
    """
    alias_list = []
    for sql, title in self.getSelectedColumnList():
      alias_list.append(sql.replace('.', '_'))
    return alias_list

  getColumnAliasList = lazyMethod(getColumnAliasList)

  def getParamDict(self):
    """Return a dictionary of parameters.
    """
    params = dict(self.getSelection().getParams())
    if self.getListMethodName():
      # Update parameters, only if list_method is defined.
      # (i.e. do not update parameters in listboxes intended to show a previously defined selection.
      params.update(self.request.form)
      for k, v in self.getDefaultParamList():
        params.setdefault(k, v)

      search_prefix = 'search_%s_' % (self.getId(), )
      for k, v in params.items():
        if k.startswith(search_prefix):
          params[k[len(search_prefix):]] = v

      search_value_list = [x for x in self.getSearchValueList(param_dict=params) if isinstance(x[1], basestring)]
      listbox_form = self.getForm()
      listbox_id = self.getId()
      for search_id, search_value, search_field in search_value_list:
        if search_field is None:
          search_alias = '_'.join(search_id.split('.'))
          # If the search field could not be found, try to get an "editable" field on current form.
          search_field = self.getEditableField(search_alias)
          if search_field is None:
            continue

        render_dict = search_field.render_dict(search_value)
        if render_dict is not None:
          params[search_id] = render_dict

      # Set parameters, depending on the list method.
      list_method_name = self.getListMethodName()
      meta_type_list = self.getMetaTypeList()
      portal_type_list = self.getPortalTypeList()
      if portal_type_list is not None:
        params.setdefault('portal_type', portal_type_list)
      elif meta_type_list is not None:
        params.setdefault('meta_type', meta_type_list)

      # Remove FileUpload parameters
      for k, v in params.items():
        if k == "listbox":
          # listbox can also contain useless parameters
          new_list = []
          for line in v:
            for k1, v1 in line.items():
              if hasattr(v1, 'read'):
                del line[k1]
            new_list.append(line)
          params[k] = new_list
        if hasattr(v, 'read'):
          del params[k]

      # remove some erp5_xhtml_style specific parameters
      params.pop('saved_form_data', None)

    # Set the columns. The idea behind this is that, instead of selecting all columns,
    # ListBox can specify only required columns, in order to reduce the data transferred
    # from a SQL Server to Zope.
    sql_column_list = []
    for (sql, title), alias in zip(self.getSelectedColumnList(), self.getColumnAliasList()):
      if sql != alias:
        sql_column_list.append('%s AS %s' % (sql, alias))
      else:
        sql_column_list.append(alias)

    # XXX why is this necessary? For compatibility?
    for sql, title in self.getAllColumnList():
      if sql in ('catalog.path', 'path'):
        alias = sql.replace('.', '_')
        if sql != alias:
          sql_column_list.append('%s AS %s' % (sql, alias))
        else:
          sql_column_list.append(alias)
        break

    params['select_columns'] = ', '.join(sql_column_list)

    # XXX Remove selection_expression if present.
    # This is necessary for now, because the actual selection expression in
    # search catalog does not take the requested columns into account. If
    # select_expression is passed, this can raise an exception, because stat
    # method sets select_expression, and this might cause duplicated column
    # names.
    #
    # In the future, this must be addressed in a clean way. selection_expression
    # should be used for search catalog, and search catalog should not use
    # catalog.* but only selection_expression. But this is a bit difficult,
    # because there is no simple way to distinguish queried columns from callable
    # objects in the current ListBox configuration.
    if 'select_expression' in params:
      del params['select_expression']

    self.getSelection().edit(params=params)
    return params

  getParamDict = lazyMethod(getParamDict)

  def getEditableField(self, alias):
    """Get an editable field for column, using column alias.
    Return None if a field for this column does not exist.
    """
    form = self.getForm()
    editable_field_id = '%s_%s' % (self.getUnprefixedId(), alias)
    if form.has_field(editable_field_id, include_disabled=1):
      return form.get_field(editable_field_id, include_disabled=1)
    
    # if we are rendering a proxy field, also look for editable fields from the
    # template field's form.
    if self.field.has_value('form_id'):
      form = getattr(self.field, self.field.get_value('form_id'), None)
      if form and form.has_field(editable_field_id, include_disabled=1):
        return form.get_field(editable_field_id, include_disabled=1)

    return None

  def getListMethod(self):
    """Return the list method object.
    """
    list_method_name = self.getListMethodName()

    if list_method_name in ('objectValues', 'contentValues'):
      list_method = ListMethodWrapper(self.getContext(), list_method_name)
    elif list_method_name == 'searchFolder':
      list_method = CatalogMethodWrapper(self.getContext(), list_method_name)
    elif list_method_name is not None:
      list_method = getattr(self.getContext(), list_method_name, None)
    else:
      list_method = None

    return list_method

  getListMethod = lazyMethod(getListMethod)

  def getCountMethod(self):
    """Return the count method object.
    """
    count_method_name = self.getCountMethodName()

    if count_method_name == 'objectValues':
      # Get all objects anyway in this case.
      count_method = None
    elif count_method_name == 'portal_catalog':
      count_method = CatalogMethodWrapper(self.getCatalogTool(), 'countResults')
    elif count_method_name == 'countFolder':
      count_method = CatalogMethodWrapper(self.getContext(), count_method_name)
    elif count_method_name is not None:
      count_method = getattr(self.getContext(), count_method_name, None)
    else:
      count_method = None

    return count_method

  getCountMethod = lazyMethod(getCountMethod)

  def getStatMethod(self):
    """Return the stat method object.
    """
    stat_method_name = self.getStatMethodName()

    if stat_method_name == 'objectValues':
      # Nothing to do in this case.
      stat_method = None
    elif stat_method_name == 'portal_catalog':
      stat_method = CatalogMethodWrapper(self.getCatalogTool(), 'countResults')
    elif stat_method_name == 'countFolder':
      stat_method = CatalogMethodWrapper(self.getContext(), stat_method_name)
    elif stat_method_name is not None:
      stat_method = getattr(self.getContext(), stat_method_name, None)
    else:
      stat_method = None

    return stat_method

  getStatMethod = lazyMethod(getStatMethod)

  def getRowCSSMethod(self):
    """Return the row css method object.
    """
    row_css_method_name = self.getRowCSSMethodName()
    row_css_method = None
    if row_css_method_name is not None:
      row_css_method = getattr(self.getContext(), row_css_method_name, None)
    return row_css_method

  getRowCSSMethod = lazyMethod(getRowCSSMethod)
  
  def getDomainSelection(self):
    """Return a DomainSelection object wrapped with the context.
    """
    portal_object = self.getPortalObject()
    selection = self.getSelection()
    domain_list = selection.getDomainList()

    if len(domain_list) > 0:
      category_tool = self.getCategoryTool()
      domain_tool = self.getDomainTool()
      root_dict = {}

      for domain in domain_list:
        # XXX workaround for a past bug in Selection
        if not isinstance(domain, str):
          continue

        root = None
        base_domain = domain.split('/', 1)[0]
        if category_tool is not None:
          root = category_tool.restrictedTraverse(domain, None)
          if root is not None :
            root_dict[base_domain] = ('portal_categories', domain)
          elif domain_tool is not None:
            try:
              root = domain_tool.getDomainByPath(domain, None)
            except KeyError:
              root = None
            if root is not None:
              root_dict[base_domain] = ('portal_domains', domain)
        if root is None:
          root = portal_object.restrictedTraverse(domain, None)
          if root is not None:
            root_dict[None] = (None, domain)

      return DomainSelection(domain_dict = root_dict).__of__(self.getContext())

  getDomainSelection = lazyMethod(getDomainSelection)

  def getStatSelectExpression(self):
    """Return a string which expresses the information retrieved by SELECT for
    the statistics.
    """
    select_expression_list = []
    if self.showStat():
      stats = self.getSelectionTool().getSelectionStats(self.getSelectionName(), REQUEST = self.request)
      stat_column_list = self.getStatColumnList()

      for index, ((sql, title), alias) in enumerate(zip(self.getSelectedColumnList(), self.getColumnAliasList())):
        # XXX This might be slow.
        for column in stat_column_list:
          if column[0] == sql:
            break
        else:
          column = None
        if (column is not None) and (column[0] == column[1]):
          try:
            if stats[index] != ' ':
              select_expression_list.append('%s(%s) AS %s' % (stats[index], sql, alias))
            else:
              select_expression_list.append("'' AS %s" % alias)
          except IndexError:
            select_expression_list.append("'' AS %s" % alias)

    return ', '.join(select_expression_list)

  getStatSelectExpression = lazyMethod(getStatSelectExpression)

  def makeReportTreeList(self, root_dict = None, report_path = None, base_category = None, depth = 0,
                         unfolded_list = (), is_report_opened = True, sort_on = (('id', 'ASC'),)):
    """Return a list of report trees.
    """
    if isinstance(report_path, str):
      report_path = report_path.split('/')
    if base_category is None and len(report_path):
      base_category = report_path[0]

    category_tool = self.getCategoryTool()
    domain_tool = self.getDomainTool()
    portal_object = self.getPortalObject()
    report_depth = self.getReportDepth()

    if root_dict is None:
      root_dict = {}

    # Find the root object.
    is_empty_level = 1
    category = base_category
    while is_empty_level:
      if not root_dict.has_key(category):
        root = None
        if category_tool is not None:
          try:
            if category == 'parent':
              # parent has a special treatment
              root = self.getContext()
              root_dict[category] = root_dict[None] = (root, (None, root.getRelativeUrl()))
            else:
              root = category_tool[category]
              root_dict[category] = root_dict[None] = (root, ('portal_categories', root.getRelativeUrl()))
            report_path = report_path[1:]
          except KeyError:
            pass
        if root is None and domain_tool is not None:
          try:
            root = domain_tool[category]
            root_dict[category] = root_dict[None] = (root, ('portal_domains', root.getRelativeUrl()))
            report_path = report_path[1:]
          except KeyError:
            pass
        if root is None:
          root = portal_object.unrestrictedTraverse(report_path, None)
          if root is not None:
            root_dict[None] = (root, (None, root.getRelativeUrl()))
          report_path = ()
      else:
        root_dict[None] = root_dict[category]
        root = root_dict[None][0]
        report_path = report_path[1:]
      is_empty_level = (root is None or root.objectCount() == 0) and (len(report_path) != 0)
      if is_empty_level:
        category = report_path[0]

    tree_list = []
    if root is None: return tree_list

    # Get the list of objects in the root. Use getChildDomainValueList, if defined,
    # to generate child domains dynamically.
    getChildDomainValueList = getattr(aq_base(root), 'getChildDomainValueList', None)
    contentValues = getattr(aq_base(root), 'contentValues', None)
    if getChildDomainValueList is not None and base_category != 'parent':
      obj_list = root.getChildDomainValueList(root, depth = depth)
    elif contentValues is not None:
      obj_list = root.contentValues(sort_on = sort_on)
    else:
      obj_list = ()

    for obj in obj_list:
      new_root_dict = root_dict.copy()
      new_root_dict[None] = new_root_dict[base_category] = (obj, (new_root_dict[base_category][1][0], obj.getRelativeUrl()))
      domain_dict = {}
      for k, v in new_root_dict.iteritems():
        domain_dict[k] = v[1]
      selection_domain = DomainSelection(domain_dict = domain_dict)

      if base_category == 'parent':
        exception_uid_list = []
      else:
        exception_uid_list = None

      #LOG('ListBox', 0, 'depth = %r, report_depth = %r, unfolded_list = %r, obj.getRelativeUrl() = %r' % (depth, report_depth, unfolded_list, obj.getRelativeUrl()))
      if (report_depth is not None and depth <= (report_depth - 1)) or obj.getRelativeUrl() in unfolded_list:
        # If the base category is parent, do not display sub-objects
        # which can be used as a part of the report tree. Otherwise,
        # sub-objects are displayed twice unnecessarily.
        if base_category == 'parent':
          for sub_obj in obj.contentValues(sort_on = sort_on):
            if getattr(aq_base(sub_obj), 'objectValues', None) is not None:
              exception_uid_list.append(sub_obj.getUid())

        # Summary (open)
        tree_list.append(ReportTree(obj = obj, is_pure_summary = True, depth = depth,
                                    base_category = base_category,
                                    is_open = True, selection_domain = selection_domain,
                                    exception_uid_list = exception_uid_list))
        if is_report_opened:
          # List (contents, closed, must be strict selection)
          tree_list.append(ReportTree(obj = obj, is_pure_summary = False, depth = depth,
                                      base_category = base_category,
                                      is_open = False, selection_domain = selection_domain,
                                      exception_uid_list = exception_uid_list))
        # manage multiple base category
        if len(report_path) >= 1 and base_category != report_path[0]:
          new_base_category = None
        else:
          new_base_category = base_category
        tree_list.extend(self.makeReportTreeList(root_dict = new_root_dict,
                                                 report_path = report_path,
                                                 base_category = new_base_category,
                                                 depth = depth + 1,
                                                 unfolded_list = unfolded_list,
                                                 is_report_opened = is_report_opened,
                                                 sort_on = sort_on))
      else:
        # Summary (closed)
        tree_list.append(ReportTree(obj = obj, is_pure_summary = True, depth = depth,
                                    base_category = base_category,
                                    is_open = False, selection_domain = selection_domain,
                                    exception_uid_list = exception_uid_list))

    return tree_list

  def getLineStart(self):
    """Return where the first line should start from. Note that this is simply a requested value,
    so the real value can be different from this. For example, if the value exceeds the total number
    of lines, the start number is forced to fit into somewhere. This must be overridden in subclasses.
    """
    raise NotImplementedError, "getLineStart must be overridden in a subclass"

  def getSelectedDomainPath(self):
    """Return a selected domain path.
    """
    domain_path = self.getSelection().getDomainPath()
    if domain_path == ('portal_categories',):
      try:
        # Default to the first domain.
        domain_path = self.getDomainRootList()[0][0]
      except IndexError:
        domain_path = None
    return domain_path

  getSelectedDomainPath = lazyMethod(getSelectedDomainPath)

  def getSelectedReportPath(self):
    """Return a selected report path.
    """
    category_tool = self.getCategoryTool()
    domain_tool = self.getDomainTool()
    report_root_list = self.getReportRootList()
    selection = self.getSelection()

    default_selection_report_path = report_root_list[0][0].split('/', 1)[0]
    if (category_tool is None or category_tool._getOb(default_selection_report_path, None) is None) \
        and (domain_tool is None or domain_tool._getOb(default_selection_report_path, None) is None):
      default_selection_report_path = report_root_list[0][0]

    return selection.getReportPath(default = default_selection_report_path)

  getSelectedReportPath = lazyMethod(getSelectedReportPath)

  def getLabelValueList(self):
    """Return a list of values, where each value is a tuple consisting of an property id, a title and a string which
    describes the current sorting order, one of ascending, descending and None. If a value is not sortable, the id is
    set to None, otherwise to a string.
    """
    sort_list = self.getSelectionTool().getSelectionSortOrder(self.getSelectionName())
    sort_dict = {}
    for sort_item in sort_list:
      sort_dict[sort_item[0]] = sort_item[1] # sort_item can be couple or a triplet
    sort_column_id_set = self.getSortColumnIdSet()

    value_list = []
    for c in self.getSelectedColumnList():
      if c[0] in sort_column_id_set:
        value_list.append((c[0], c[1], sort_dict.get(c[0])))
      else:
        value_list.append((None, c[1], None))

    return value_list

  def getSearchValueList(self, param_dict=None):
    """Return a list of values, where each value is a tuple consisting of an alias, a current value and a search field.
    If a column is not searchable, the alias is set to None, otherwise to a string. If a search field is not present,
    it is set to None.
    """
    search_column_id_set = self.getSearchColumnIdSet()
    if param_dict is None:
      param_dict = self.getParamDict()
    value_list = []
    for (sql, title), alias in zip(self.getSelectedColumnList(), self.getColumnAliasList()):
      if sql in search_column_id_set:
        # Get the current value and encode it in unicode.
        param = param_dict.get(alias, param_dict.get(sql, u''))
        if isinstance(param, dict):
          param = param.get('query', u'')
        if isinstance(param, str):
          param = unicode(param, self.getEncoding())

        # Obtain a search field, if any.
        form = self.getForm()
        if form.has_field(alias):
          search_field = form.get_field(alias)
        else:
          search_field = None

        value_list.append((sql, param, search_field))
      else:
        value_list.append((None, None, None))

    return value_list
  
  def getStatValueList(self):
    """Return a list of values, where each value is a tuple consisting of an original value and a processed value.
    A processed value is always an unicode object, and it may differ from the original value, for instance,
    a processed value may describe an error, when an original value is None.
    """
    # First, get the statitics by the global stat method.
    param_dict = self.getParamDict()
    new_param_dict = param_dict.copy()
    new_param_dict['select_expression'] = self.getStatSelectExpression()
    selection = self.getSelection()
    selection.edit(params = new_param_dict)

    _result = {'value':None, 'called':False}
    def getStatMethodResult():
      """Stat method must be called only when necessary"""
      if _result['called']:
        return _result['value']
      _result['value'] = selection(method = self.getStatMethod(), context = self.getContext(), REQUEST = self.request)
      _result['called'] = True
      return _result['value']

    # For each column, check the presense of a specific stat method. If not present,
    # use getStatMethodResult defined above.
    value_list = []
    stat_column_dict = dict(self.getStatColumnList())
    for (sql, title), alias in zip(self.getSelectedColumnList(), self.getColumnAliasList()):
      original_value = None
      processed_value = None

      # Get a specific stat method, if any.
      stat_method_id = stat_column_dict.get(sql)
      if stat_method_id is not None and stat_method_id != sql:
        stat_method = getattr(self.getContext(), stat_method_id)
      else:
        stat_method = None

      if stat_method_id is None:
        original_value = None
        processed_value = u''
      elif stat_method is None:
        try:
          original_value = getattr(getStatMethodResult()[0], alias)
          processed_value = original_value
        except (IndexError, AttributeError, KeyError, ValueError):
          original_value = None
          processed_value = u''
      else:
        if callable(stat_method):
          try:
            original_value = stat_method(selection = selection,
                                         selection_name = selection.getName())
            processed_value = original_value
          except (ConflictError, RuntimeError):
            raise
          except:
            LOG('ListBox', WARNING, 'could not call %r with %r' % (stat_method, self.getContext()),
                error = sys.exc_info())
            original_value = None
            processed_value = u''
        else:
          original_value = stat_method
          processed_value = original_value

      editable_field = self.getEditableField(alias)
      if editable_field is not None:
        processed_value = editable_field.render_view(value=original_value)

      if not isinstance(processed_value, unicode):
        processed_value = unicode(str(processed_value), self.getEncoding())

      value_list.append((original_value, processed_value))

    return value_list

  def getRowCSSClassName(self, **kw):
    """Return the css class name of a table row. If the method is not callable, returns None.
    """
    row_css_method = self.getRowCSSMethod()
    if callable(row_css_method):
      return row_css_method(**kw)
    return None

  def getReportSectionList(self):
    """Return a list of report sections.
    """
    param_dict = self.getParamDict()
    category_tool = self.getCategoryTool()
    domain_tool = self.getDomainTool()
    report_depth = self.getReportDepth()
    selection = self.getSelection()
    selection_tool = self.getSelectionTool()
    report_list = selection.getReportList()
    stat_select_expression = self.getStatSelectExpression()
    stat_method = self.getStatMethod()
    count_method = self.getCountMethod()
    list_method = self.getListMethod()
    context = self.getContext()
    selection_name = self.getSelectionName()
    start = self.getLineStart()
    max_lines = self.getMaxLineNumber()
    report_section_list = []

    if self.isReportTreeMode():
      # In report tree mode, there are three types of lines:
      #
      #   - summary line with statistics
      #   - summary line with the first object in a domain
      #   - object line
      #
      # These lines are compiled into report sections for convenience.

      selection_report_path = self.getSelectedReportPath()

      #LOG('ListBox', 0, 'report_depth = %r' % (report_depth,))
      if report_depth is not None:
        selection_report_current = ()
      else:
        selection_report_current = report_list

      report_tree_list = self.makeReportTreeList(report_path = selection_report_path,
                                                 unfolded_list = selection_report_current,
                                                 is_report_opened = selection.isReportOpened(),
                                                 sort_on = selection.sort_on)

      # Update report list if report_depth was specified. This information is used
      # to store what domains are unfolded by clicking on a depth.
      if report_depth is not None:
        report_list = [t.obj.getRelativeUrl() for t in report_tree_list if t.is_open]
        selection.edit(report_list = report_list)

      for report_tree in report_tree_list:
        # Prepare query by defining selection report object.
        report_tree_obj = report_tree.obj

        # FIXME: this code needs optimization. The query should be delayed
        # as late as possible, because this code queries all data, even if
        # it is not displayed.
        selection.edit(report = report_tree.selection_domain)

        # FIXME: The following is only meant to be a temporary workaround.
        # Eventually, Selection should be rewritten to provide a more complete
        # API than just one __call__ method, and to support method_name
        # redefinition by the domain.

        # If the domain has a context_url, list_method or stat_method
        # parameters, we should use them instead of the ListBox ones when
        # looking for objects in the domain.
        domain_context = report_tree_obj.getProperty('context_url', None)
        if domain_context is not None:
          domain_context = context.restrictedTraverse(domain_context)
        else:
          domain_context = context
        domain_list_method = report_tree_obj.getProperty('list_method',
            list_method)
        domain_stat_method = report_tree_obj.getProperty('stat_method',
            stat_method)

        if report_tree.is_pure_summary and self.showStat():
          # Push a new select_expression.
          new_param_dict = param_dict.copy()
          new_param_dict['select_expression'] = stat_select_expression
          selection.edit(params = new_param_dict)

          # Query the stat.
          stat_brain = selection(method=domain_stat_method, context=domain_context, REQUEST=self.request)

          domain_title = report_tree_obj.getTitle()# XXX Yusei Keep original domain title before overriding

          stat_result = {}
          for index, (k, v) in enumerate(self.getSelectedColumnList()):
            try:
              stat_result[k] = str(stat_brain[0][index + 1])
            except IndexError:
              stat_result[k] = ''

          stat_context = report_tree_obj.asContext(**stat_result)
          # XXX yo thinks that this code below is useless, so disabled.
          #absolute_url_txt = report_tree_obj.absolute_url()
          #stat_context.absolute_url = lambda: absolute_url_txt
          stat_context.domain_url = report_tree.domain_url
          report_section_list.append(ReportSection(is_summary = True, object_list = [stat_context],
                                                   object_list_len = 1, is_open = report_tree.is_open,
                                                   selection_domain = report_tree.selection_domain,
                                                   context = stat_context, depth = report_tree.depth,
                                                   domain_title = domain_title))
        else:
          selection.edit(params = param_dict)

          if list_method is not None:
            # FIXME: this should use a count method, if present, and obtain objects, only if necessary.
            object_list = selection(method=domain_list_method, context=domain_context, REQUEST=self.request)
          else:
            # If list_method is None, use already selected values.
            object_list = self.getSelectionTool().getSelectionValueList(selection_name,
                                                                        context = context,
                                                                        REQUEST = self.request)

          if report_tree.exception_uid_set is not None:
            # Filter folders if this is a parent tree.
            new_object_list = []
            for o in object_list:
              if o.getUid() not in report_tree.exception_uid_set:
                new_object_list.append(o)
            object_list = new_object_list

          object_list_len = len(object_list)
          #LOG('ListBox', 0, 'report_tree.__dict__ = %r, object_list = %r, object_list_len = %r' % (report_tree.__dict__, object_list, object_list_len))
          if not report_tree.is_pure_summary:
            if self.showStat():
              report_section_list.append(ReportSection(is_summary = False, object_list = object_list,
                                                       object_list_len = object_list_len,
                                                       is_open = report_tree.is_open,
                                                       selection_domain = report_tree.selection_domain,
                                                       depth = report_tree.depth))
          else:
            stat_context = report_tree_obj.asContext()
            #absolute_url_txt = s[0].absolute_url()
            #stat_context.absolute_url = lambda : absolute_url_txt
            stat_context.domain_url = report_tree.domain_url
            if object_list_len and report_tree.is_open:
              # Display the first object at the same level as a category selector,
              # if this selector is open.
              report_section_list.append(ReportSection(is_summary = False,
                                                       object_list = [object_list[0]],
                                                       object_list_len = 1,
                                                       is_open = True,
                                                       selection_domain = report_tree.selection_domain,
                                                       context = stat_context,
                                                       depth = report_tree.depth))
              report_section_list.append(ReportSection(is_summary = False,
                                                       object_list = object_list,
                                                       object_list_len = object_list_len - 1,
                                                       is_open = True,
                                                       selection_domain = report_tree.selection_domain,
                                                       offset = 1,
                                                       depth = report_tree.depth))
            else:
              if report_tree.exception_uid_list is not None:
                # Display current parent domain.
                report_section_list.append(ReportSection(is_summary = False,
                                                         object_list = [report_tree_obj],
                                                         object_list_len = 1,
                                                         is_open = report_tree.is_open,
                                                         selection_domain = report_tree.selection_domain,
                                                         context = stat_context,
                                                         depth = report_tree.depth))
              else:
                # No data to display
                report_section_list.append(ReportSection(is_summary = False,
                                                         object_list = [None],
                                                         object_list_len = 1,
                                                         is_open = report_tree.is_open,
                                                         selection_domain = report_tree.selection_domain,
                                                         context = stat_context,
                                                         depth = report_tree.depth))

      # Reset the report parameter.
      selection.edit(report = None)
    else:
      # Flat list mode or domain tree mode.
      selection.edit(params = param_dict, report = None)

      domain_found = 0
      if self.isDomainTreeMode():
        domain_selection = self.getDomainSelection()
        selection.edit(domain=domain_selection)
        if domain_selection is not None:
          for k, d in domain_selection.asDomainDict().iteritems():
            if k is not None:
              domain = domain_selection._getDomainObject(
                  context.getPortalObject(), d)
              # FIXME: The following is only meant to be a temporary
              # workaround. Eventually, Selection should be rewritten to
              # provide a more complete API than just one __call__ method, and
              # to support method_name redefinition by the domain.

              # If the domain has a context_url, list_method or count_method
              # parameters, we should use them instead of the ListBox ones
              # when looking for objects in the domain.
              domain_context = domain.getProperty('context_url', None)
              if domain_context is not None:
                domain_context = context.restrictedTraverse(domain_context)
              else:
                domain_context = context
              domain_list_method = domain.getProperty('list_method',
                  list_method)
              domain_count_method = domain.getProperty('count_method',
                  count_method)
              domain_found = 1
              break
      if not domain_found:
        domain_context = context
        domain_list_method = list_method
        domain_count_method = count_method

      if list_method is not None:
        if count_method is not None and not selection.invert_mode and max_lines > 0:
          # If the count method is available, get only required objects.
          count = selection(method=domain_count_method, context=domain_context, REQUEST=self.request)
          object_list_len = int(count[0][0])

          # Tweak the line start.
          if start >= object_list_len:
            start = max(object_list_len - 1, 0)
          start -= (start % max_lines)

          # Obtain only required objects.
          new_param_dict = param_dict.copy()
          new_param_dict['limit'] = (start, max_lines)
          selection.edit(params = new_param_dict)
          object_list = selection(method=domain_list_method, context=domain_context, REQUEST=self.request)
          selection.edit(params = param_dict) # XXX Necessary?

          # Add padding for convenience.
          report_section_list.append(ReportSection(is_summary = False,
                                                   object_list_len = start))
          report_section_list.append(ReportSection(is_summary = False,
                                                   object_list = object_list,
                                                   object_list_len = len(object_list)))
          report_section_list.append(ReportSection(is_summary = False,
                                                   object_list_len = object_list_len - len(object_list) - start))
        else:
          object_list = selection(method=domain_list_method, context=domain_context, REQUEST=self.request)
          object_list_len = len(object_list)
          report_section_list.append(ReportSection(is_summary = False,
                                                   object_list = object_list,
                                                   object_list_len = object_list_len))
      else:
        # If list_method is None, use already selected values.
        object_list = selection_tool.getSelectionValueList(selection_name,
                                                                   context = context, REQUEST = self.request)
        object_list_len= len(object_list)
        report_section_list.append(ReportSection(is_summary = False,
                                                 object_list = object_list,
                                                 object_list_len = object_list_len))

    return report_section_list

  def query(self):
    """Get report sections and construct a list of lines. Note that this method has a side
    effect in the selection, and the renderer object itself.
    """
    start = self.getLineStart()
    max_lines = self.getMaxLineNumber()
    if self.isHideRowsOnNoSearchCriterion():
      report_section_list = []
    else:
      report_section_list = self.getReportSectionList()
    param_dict = self.getParamDict()

    # Set the total number of objects.
    self.total_size = sum([s.object_list_len for s in report_section_list])

    # Calculuate the start and the end offsets, and set the page numbers.
    if max_lines == 0:
      end = self.total_size
      self.total_pages = 1
      self.current_page = 0
    else:
      self.total_pages = int(max(self.total_size - 1, 0) / max_lines) + 1
      if start >= self.total_size:
        start = max(self.total_size - 1, 0)
      start -= (start % max_lines)
      self.current_page = int(start / max_lines)
      end = min(start + max_lines, self.total_size)
      param_dict['list_start'] = start
      param_dict['list_lines'] = max_lines
      selection = self.getSelection()
      selection.edit(params = param_dict)

    # Make a list of lines.
    line_class = self.getLineClass()
    line_list = []

    try:
      section_index = 0
      current_section_base_index = 0
      current_section = report_section_list[0]
      current_section_size = current_section.object_list_len
      for i in range(start, end):
        # Make sure we go to the right section.
        while current_section_base_index + current_section_size <= i:
          current_section_base_index += current_section_size
          section_index += 1
          current_section = report_section_list[section_index]
          current_section_size = current_section.object_list_len

        offset = i - current_section_base_index + current_section.offset
        if current_section.is_summary:
          index = None
        elif self.isReportTreeMode():
          index = offset
        else:
          index = i
        #LOG('ListBox', 0, 'current_section.__dict__ = %r' % (current_section.__dict__,))
        new_param_dict = param_dict.copy()
        new_param_dict['brain'] = current_section.object_list[offset]
        new_param_dict['list_index'] = index
        new_param_dict['total_size'] = self.total_size
        row_css_class_name = self.getRowCSSClassName(**new_param_dict)
        line = line_class(renderer = self,
                          obj = current_section.object_list[offset],
                          index = index,
                          is_summary = current_section.is_summary,
                          context = current_section.context,
                          is_open = current_section.is_open,
                          selection_domain = current_section.selection_domain,
                          depth = current_section.depth,
                          domain_title = current_section.domain_title,
                          row_css_class_name = row_css_class_name)
        line_list.append(line)
    except IndexError:
      # If the report section list is empty, nothing to do.
      pass

    return line_list

  def render(self, **kw):
    """Render the data. This must be overridden.
    """
    raise NotImplementedError, "render must be overridden in a subclass"

  def __call__(self, **kw):
    """Render the ListBox. The real rendering must be done the method "render" which should
    be defined in subclasses.
    """
    return self.render(**kw)

class ListBoxRendererLine:
  """This class describes a line in a ListBox to assist ListBoxRenderer.
  """
  def __init__(self, renderer = None, obj = None, index = 0, is_summary = False, context = None,
               is_open = False, selection_domain = None, depth = 0, domain_title=None, render_prefix=None,
               row_css_class_name=None):
    """In reality, the object is a brain or a brain-like object.
    """
    self.renderer = renderer
    self.obj = obj
    self.index = index
    self.is_summary = is_summary
    self.context = context
    self.is_open = is_open
    self.selection_domain = selection_domain
    self.depth = depth
    self.domain_title = domain_title
    self.render_prefix = render_prefix
    self.row_css_class_name = row_css_class_name
    
  def getBrain(self):
    """Return the brain. This can be identical to a real object.
    """
    return self.obj

  def getObject(self):
    """Return a real object.
    """
    try:
      return self.obj.getObject()
    except AttributeError:
      return self.obj

  getObject = lazyMethod(getObject)

  def getUid(self):
    """Return the uid of the object.
    """
    return getattr(aq_base(self.obj), 'uid', None)

  getUid = lazyMethod(getUid)

  def getUrl(self):
    """Return the absolute URL path of the object
    """
    return self.getBrain().getUrl()

  getUrl = lazyMethod(getUrl)

  def isSummary(self):
    """Return whether this line is a summary or not.
    """
    return self.is_summary

  def getContext(self):
    """Return the context of a line. This is used only for a summary line.
    """
    return self.context

  def isOpen(self):
    """Return whether this line is open or not. This is used only for a summary line.
    """
    return self.is_open

  def getDomainUrl(self):
    """Return the URL of a domain. Used only for a summary line.
    """
    return getattr(self.getContext(), 'domain_url', '')

  def getDomainTitle(self):
    """Return original title of domain"""
    if self.domain_title is not None:
      return self.domain_title
    else:
      context = self.getContext()
      if context is not None:
        return context.getTitleOrId() or ''
    return ''

  def getDepth(self):
    """Return the depth of a domain. Used only for a summary line.
    """
    return self.depth

  def getDomainSelection(self):
    """Return the domain selection. Used only for a summary line.
    """
    return self.selection_domain

  def getRowCSSClassName(self):
    """Return the css class name of a row.
    """
    return self.row_css_class_name
  
  def getValueList(self):
    """Return the list of values corresponding to selected columns.

    The format of a return value is [(original_value, processed_value), ...],
    where the original value means a raw result, while the processed value stands for
    a value more comprehensive for human, such as an error message.

    Every processed value is guaranteed to be encoded in unicode.
    """
    # If this is a report line without statistics, just return an empty result.
    renderer = self.renderer
    if self.getObject() is None:
      return [(None, '')] * len(renderer.getSelectedColumnList())

    # Otherwise, evaluate each column.
    stat_column_dict = dict(renderer.getStatColumnList())
    _marker = []
    value_list = []
    selection = renderer.getSelection()
    param_dict = renderer.getParamDict()

    # Embed the selection index.
    selection.edit(index = self.index)

    for (sql, title), alias in zip(renderer.getSelectedColumnList(), renderer.getColumnAliasList()):
      editable_field = None
      original_value = None
      processed_value = None

      if self.isSummary():
        # Use a stat method for a summary.
        stat_method_id = stat_column_dict.get(sql)
        if stat_method_id == sql:
          stat_method_id = None

        context = self.getContext()
        if getattr(aq_base(context), alias, _marker) is not _marker and stat_method_id is None:
          # If a stat method is not specified, use the result in the context itself.
          original_value = getattr(context, alias)
          processed_value = original_value
        elif stat_method_id is not None:
          stat_method = getattr(context, stat_method_id)
          if callable(stat_method):
            try:
              new_param_dict = param_dict.copy()
              new_param_dict['closed_summary'] = not self.isOpen()
              selection.edit(params = new_param_dict, report = self.getDomainSelection())
              try:
                original_value = stat_method(selection = selection,
                                             selection_name = selection.getName())
                processed_value = original_value
              except (ConflictError, RuntimeError):
                raise
              except:
                LOG('ListBox', WARNING, 'could not call %r with %r' % (stat_method, new_param_dict),
                    error = sys.exc_info())
                processed_value = 'Could not evaluate %s' % (stat_method_id,)
            finally:
              selection.edit(params = param_dict, report = None)
          else:
            original_value = stat_method
            processed_value = original_value
      else:
        # This is an usual line.
        obj = None # Only evaluate if needed
        brain = self.getBrain()

        # Use a widget, if any.
        editable_field = renderer.getEditableField(alias)
        tales = False
        if editable_field is not None:
          tales = editable_field.tales.get('default', '')
          if tales:
            if obj is None: obj = self.getObject()
            original_value = editable_field.__of__(obj).get_value('default',
                                                        cell=brain)
            processed_value = original_value

        # If a tales expression is not defined, get a skin, an accessor or a property.
        if not tales:
          if (obj is None or brain is not obj) and getattr(aq_self(brain), alias, None) is not None:
            original_value = getattr(brain, alias)
            processed_value = original_value
          else:
            obj = self.getObject()
            if obj is not None:
              try:
                # Get the trailing part.
                try:
                  property_id = sql[sql.rindex('.') + 1:]
                except ValueError:
                  property_id = sql
  
                try:
                  original_value = obj.getProperty(property_id, _marker)
                  if original_value is _marker:
                    raise AttributeError, property_id
                  processed_value = original_value
                except AttributeError:
                  original_value = getattr(obj, property_id, None)
                  processed_value = original_value
              except (AttributeError, KeyError, Unauthorized):
                original_value = None
                processed_value = 'Could not evaluate %s' % property_id
            else:
              original_value = None
              processed_value = 'Object does not exist'

      # If the value is callable, evaluate it.
      if callable(original_value):
        try:
          try:
            original_value = original_value(brain = self.getBrain(),
                                            selection = selection,
                                            selection_name = selection.getName())
            processed_value = original_value
          except TypeError:
            original_value = original_value()
            processed_value = original_value
        except (ConflictError, RuntimeError):
          raise
        except:
          processed_value = 'Could not evaluate %s' % (original_value,)
          LOG('ListBox', WARNING, 'could not evaluate %r' % (original_value,),
              error = sys.exc_info())
          original_value = None

      # Process the value.
      if processed_value is None:
        processed_value = u''
      elif not isinstance(processed_value, unicode):
        processed_value = unicode(str(processed_value), renderer.getEncoding())

      value_list.append((original_value, processed_value))

    #LOG('ListBox.getValueList', 0, value_list)
    return value_list

class ListBoxHTMLRendererLine(ListBoxRendererLine):
  """This class is specialized to the HTML renderer.
  """
  def render(self):
    """Render the values obtained by getValueList. The result is a list of tuples,
    where each tuple consists of a piece of HTML, the original value and a boolean value which represents
    an error status. If the status is true, an error is detected.
    """
    renderer = self.renderer
    request = renderer.request
    editable_column_id_set = renderer.getEditableColumnIdSet()
    field_id = renderer.getId()
    form = renderer.getForm()
    error_dict = renderer.getFieldErrorDict()
    brain = self.getBrain()
    encoding = renderer.getEncoding()
    url_column_dict = dict(renderer.getUrlColumnList())
    selection = renderer.getSelection()
    selection_name = renderer.getSelectionName()
    ignore_layout = int(request.get('ignore_layout', \
                        not request.get('is_web_mode', False) and 1 or 0))
    ui_domain = 'erp5_ui'

    html_list = []

    # Generate page selection methods based on the Listbox id
    createFolderMixInPageSelectionMethod(field_id)

    # Check is there is a validation error at the level of the listbox
    # as a whole. This will be required later to decide wherer to
    # display values from (ie. from the REQUEST or from the object)
    has_error = 0
    for key in error_dict.keys():
      for editable_id in editable_column_id_set:
        candidate_field_key = "%s_%s" % (field_id, editable_id)
        if key.startswith(candidate_field_key):
          has_error = 1
          break
      if has_error:
        break

    for (original_value, processed_value), (sql, title), alias \
      in zip(self.getValueList(), renderer.getSelectedColumnList(), renderer.getColumnAliasList()):
      # By default, no error.
      error = False

      # Embed the selection index.
      selection.edit(index = self.index)

      # If a field is editable, generate an input form.
      # XXX why don't we generate an input form when a widget is not defined?
      editable_field = None
      if not self.isSummary():
        editable_field = renderer.getEditableField(alias)

      # Prepare link value - we now use it for both static and field rendering
      no_link = False
      url_method = None
      url = None

      # Find an URL method.
      if url_column_dict.has_key(sql):
        url_method_id = url_column_dict.get(sql)
        if url_method_id != sql:
          if url_method_id not in (None, ''):
            url_method = getattr(brain, url_method_id, None)
            if url_method is None:
              LOG('ListBox', WARNING, 'could not find the url method %s' % (url_method_id,))
              no_link = True
          else:
            # If the URL Method is empty, generate no link.
            no_link = True

      if url_method is not None:
        try:
          url = url_method(brain = brain, selection = selection,
                           selection_name = selection.getName())
        except (ConflictError, RuntimeError):
          raise
        except:
          LOG('ListBox', WARNING, 'could not evaluate the url method %r with %r' % (url_method, brain),
              error = sys.exc_info())
      elif not no_link:
        # XXX For compatibility?
        # Check if this object provides a specific URL method.
        if getattr(brain, 'getListItemUrl', None) is not None:
          try:
            url = brain.getListItemUrl(alias, self.index, selection_name)
          except (ConflictError, RuntimeError):
            raise
          except:
            LOG('ListBox', WARNING, 'could not evaluate the url method getListItemUrl with %r' % (brain,),
                error = sys.exc_info())
        else:
          try:
            url = '%s/view?selection_index=%s&amp;selection_name=%s&amp;ignore_layout:int=%s&amp;reset:int=1' % (
                      # brain.absolute_url() is slow because it invokes
                      # _aq_dynamic() every time to get brain.REQUEST,
                      # so we call request.physicalPathToURL() directly
                      # instead of brain.absolute_url().
                      request.physicalPathToURL(brain.getPath()),
                      self.index, selection_name, ignore_layout)
          except AttributeError:
            pass

      if editable_field is not None and sql in editable_column_id_set:
        # XXX what if the object does not have uid?
        key = '%s_%s' % (editable_field.getId(), self.getUid())
        widget_key = editable_field.generate_field_key(key=key)
        if has_error: # If there is any error on listbox, we should use what the user has typed
          display_value = None
        else:
          validated_value_dict = request.get(field_id, None)
          if validated_value_dict is None:
            # If this is neither an error nor a validated listbox
            # we should use the original value
            display_value = original_value
          else:
            # If the listbox has been validated (ie. as it is the
            # case whenever a relation field displays a popup menu)
            # we have to use the value entered by the user
            display_value = None #
        if error_dict.has_key(key): # If error on current field, we should display message
          error_text = error_dict[key].error_text
          error_text = cgi.escape(error_text)
          if isinstance(error_text, str):
            error_mapping = getattr(error_dict[key], 'error_mapping', None)
            if error_mapping is not None:
              error_text = u'%s' % Message(domain=ui_domain,
                                           message=error_text,
                                           mapping=error_mapping)
            else:
              error_text = u'%s' % Message(domain=ui_domain,
                                           message=error_text)
          error_message = u'<br />' + error_text
        else:
          error_message = u''

        if getattr(brain, 'asContext', None) is not None:
          # We needed a way to pass the current line object (ie. brain)
          # to the field which is being displayed. Since the
          # render_view API did not permit this, we pass the line object
          # as the REQUEST. But this has side effects since it breaks
          # many possibilities. Therefore, the trick is to wrap
          # the REQUEST into the brain. In addition, the define a
          # cell property on the request itself so that forms may
          # use the 'cell' value (refer to get_value method in Form.py)
          cell_request = brain.asContext( REQUEST = request
                                        , form    = request.form
                                        , cell    = brain
                                        )
          if editable_field.get_value('enabled', REQUEST=cell_request):
            cell_html = editable_field.render( \
                              value   = display_value
                            , REQUEST = cell_request
                            , key     = key
                            )
          else:
            cell_html = ''
        else:
          # If the brain does not support asContext (eg. it is None), no way
          request.cell = self.getObject()
          cell_request = brain
          if editable_field.get_value('enabled', REQUEST=cell_request):
            cell_html = editable_field.render( value   = display_value
                                             , REQUEST = cell_request
                                             , key     = key
                                             )
          else:
            cell_html = ''

        if isinstance(cell_html, str):
          cell_html = unicode(cell_html, encoding)

        if url is None:
          html = cell_html + error_message
        else:
          if editable_field.get_value('editable', REQUEST=cell_request):
            html = u'%s' % cell_html
          else:
            html = u'<a href="%s">%s</a>' % (url, cell_html)
          if error_message not in ('', None):
            html += u' <span class="error">%s</span>' % error_message
      else:
        # If not editable, show a static text with a link, if enabled.
        processed_value = cgi.escape(processed_value)
        if url is None:
          html = processed_value
        else:
          # JPS-XXX - I think we should not display a URL for objects
          # which do not have the View permission
          if type(url) is str:
            url = unicode(url.decode('utf-8'))
          html = u'<a href="%s">%s</a>' % (url, processed_value)

      html_list.append((html, original_value, error, editable_field, url))

    return html_list

allow_class(ListBoxHTMLRendererLine)

class ListBoxRendererContext(Acquisition.Explicit):
  """This class helps making a context for a Page Template,
  because Page Template requires an acquisition context.
  """
  def __init__(self, renderer):
    self.renderer = renderer
    # XXX this is a workaround for GlobalTranslationService.
    self.Localizer = renderer.getContext().Localizer
    # XXX this is a workaround for unicodeconflictresolver.
    self.REQUEST = renderer.request

  def __getattr__(self, name):
    return getattr(self.renderer, name)

class ListBoxHTMLRenderer(ListBoxRenderer):
  """This class implements HTML rendering for ListBox.
  """
  def getLineClass(self):
    """Return the line class.
    """
    return ListBoxHTMLRendererLine

  def getLineStart(self):
    """Return a requested start number.
    """
    return int(self.getParamDict().get('list_start', 0))

  getLineStart = lazyMethod(getLineStart)

  def getMaxLineNumber(self):
    """Return the maximum number of lines shown in a page.
    """
    list_lines = self.getParamDict().get('list_lines', None)
    if list_lines is not None:
      # it's possible to override max lines from selection parameters
      return int(list_lines)
    return self.field.get_value('lines')

  getMaxLineNumber = lazyMethod(getMaxLineNumber)

  def getMD5Checksum(self):
    """Generate a MD5 checksum against checked uids. This is used to confirm
    that selected values do not change between a display of a dialog and an execution.

    FIXME: this should only use getCheckedUidList, but Folder_deleteObjectList does not use
    the feature that checked uids are used when no list method is specified.
    """
    checked_uid_list = self.request.get('uids')
    if checked_uid_list is None:
      checked_uid_list = self.getCheckedUidList()
    if checked_uid_list is not None:
      checked_uid_list = [str(uid) for uid in checked_uid_list]
      checked_uid_list.sort()
      md5_string = md5.new(str(checked_uid_list)).hexdigest()
    else:
      md5_string = None

    return md5_string

  def getPhysicalRoot(self):
    """Return the physical root (an Application object). This method is required for
    Page Template to make a context.
    """
    return self.getContext().getPhysicalRoot()

  asHTML = PageTemplateFile('www/ListBox_asHTML', globals())

  def getPageTemplate(self):
    """Return a Page Template to render.
    """
    context = ListBoxRendererContext(self)

    # If a specific template is specified, use it.
    method_id = self.field.get_value('page_template')
    if method_id not in (None, ''):
      try:
        return getattr(context, method_id)
      except AttributeError:
        return getattr(context.getPortalObject(), method_id).__of__(context)
      return aq_base(getattr(self.getContext(), method_id)).__of__(context)
    # Try to get a page template from acquisition context then portal object
    # and fallback on default page template.
    return getattr(self.getContext(), 'ListBox_asHTML',
           getattr(context.getPortalObject(), 'ListBox_asHTML', context.asHTML)
           ).__of__(context)

  def render(self, **kw):
    """Render the data in HTML.
    """
    # Make it sure to store the current selection, only if a list method is defined.
    list_method = self.getListMethod()
    selection = self.getSelection()
    if list_method is not None:
      method_path = '%s/%s' % (getPath(self.getContext()), self.getListMethodName())
      list_url = '%s?selection_name=%s' % (self.getUrl(), self.getRequestedSelectionName())
      selection_index = self.getSelectionIndex()
      if selection_index is not None:
        list_url += '&selection_index=%s' % selection_index
      selection.edit(method_path = method_path, list_url = list_url)
      self.getSelectionTool().setSelectionFor(self.getSelectionName(), selection, REQUEST = self.request)

    pt = self.getPageTemplate()
    return pt()

allow_class(ListBoxHTMLRenderer)

class ListBoxListRenderer(ListBoxRenderer):
  """This class implements list rendering for ListBox.
  """
  def getLineClass(self):
    """Return the line class. For now, ListBoxListRenderer uses the generic class.
    """
    return ListBoxRendererLine

  def getLineStart(self):
    """Return always 0.
    """
    return 0

  def getMaxLineNumber(self):
    """Return always 0 (infinite).
    """
    return 0

  def render(self, **kw):
    """Render the data in a list of ListBoxLine objects.
    """
    listboxline_list = []

    # Make a title line.
    title_listboxline = ListBoxLine()
    title_listboxline.markTitleLine()
    for c in self.getSelectedColumnList():
      title_listboxline.addColumn(c[0], c[1].encode(self.getEncoding()))
    listboxline_list.append(title_listboxline)

    # Obtain the list of lines.
    checked_uid_set = set(self.getCheckedUidList())
    for line in self.query():
      listboxline = ListBoxLine()
      listboxline.markDataLine()
      listboxline.setSectionDepth(line.getDepth())
      listboxline.setRowCSSClassName(line.getRowCSSClassName())
      if line.isSummary():
        listboxline.markSummaryLine()
        # XXX It was line.getDepth()+1 before, but
        # it probably make no sense so I (seb) removed this
        listboxline.setSectionDepth(line.getDepth())
        # Do not get the context again, it was already computed
        # in getReportSectionList
        listboxline.setSectionName(line.domain_title)
        listboxline.setSectionFolded(not line.isOpen())

      if line.getBrain() is not None:
        uid = line.getUid()
        listboxline.setObjectUid(uid)
        listboxline.checkLine(uid in checked_uid_set)

      for (original_value, processed_value), (sql, title) in zip(line.getValueList(), self.getSelectedColumnList()):
        if isinstance(original_value, unicode):
          value = original_value.encode(self.getEncoding())
        else:
          value = original_value

        if isinstance(value, str):
          value = value.replace('&nbsp;', ' ')

        listboxline.addColumn(sql, value)

      listboxline_list.append(listboxline)

    # Make a stat line, if enabled.
    if self.showStat():
      stat_listboxline = ListBoxLine()
      stat_listboxline.markStatLine()

      for (original_value, processed_value), (sql, title) in zip(self.getStatValueList(), self.getSelectedColumnList()):
        if isinstance(original_value, unicode):
          value = original_value.encode(self.getEncoding())
        else:
          value = original_value

        if isinstance(value, str):
          value = value.replace('&nbsp;', ' ')

        stat_listboxline.addColumn(sql, value)

      listboxline_list.append(stat_listboxline)

    return listboxline_list

class ListBoxValidator(Validator.Validator):
    property_names = Validator.Validator.property_names

    def validate(self, field, key, REQUEST):
        form = field.aq_parent
        # We need to know where we get the getter from
        # This is coppied from ERP5 Form
        here = getattr(form, 'aq_parent', REQUEST)
        columns = field.get_value('columns')
        editable_columns = field.get_value('editable_columns')
        column_ids = [x[0] for x in columns]
        editable_column_ids = [x[0] for x in editable_columns]
        selection_name = field.get_value('selection_name')
        #LOG('ListBoxValidator', 0, 'field = %s, selection_name = %s' % (repr(field), repr(selection_name)))
        params = here.portal_selections.getSelectionParamsFor(
                                                           selection_name,
                                                           REQUEST=REQUEST)
        portal_url = getToolByName(here, 'portal_url')
        portal = portal_url.getPortalObject()

        result = {}
        error_result = {}
        MARKER = []
        listbox_uids = REQUEST.get('%s_uid' % field.id, MARKER)
        if listbox_uids is MARKER:
          raise KeyError, 'Field %s is not present in request object.' % (field.id, )
        #LOG('ListBox.validate: REQUEST',0,REQUEST)
        errors = []
        object_list = []
        # We have two things to do in the case of temp objects,
        # the first thing is to create a list with new temp objects
        # then try to validate some data, and then create again
        # the list with a listbox as parameter. Like this we
        # can use tales expression
        for uid in listbox_uids:
          if str(uid).find('new') == 0:
            list_method = field.get_value('list_method')
            list_method = getattr(here, list_method.method_name)
            #LOG('ListBoxValidator', 0, 'call %s' % repr(list_method))
            object_list = list_method(REQUEST=REQUEST, **params)
            break
        listbox = {}
        for uid in listbox_uids:
          if str(uid).find('new') == 0:
            o = None
            for object in object_list:
              if object.getUid()==uid:
                o = object
            if o is None:
              # First case: dialog input to create new objects
              o = newTempBase(portal, uid[4:]) # Arghhh - XXX acquisition problem - use portal root
              o.uid = uid
            listbox[uid[4:]] = {}
            # We first try to set a listbox corresponding to all things
            # we can validate, so that we can use the same list
            # as the one used for displaying the listbox
            for sql in editable_column_ids:
              alias = sql.replace('.', '_')
              if '.' in sql:
                property_id = '.'.join(sql.split('.')[1:]) # Only take trailing part
              else:
                property_id = alias
              my_field_id = '%s_%s' % (field.id, alias)
              if form.has_field( my_field_id ):
                my_field = form.get_field(my_field_id)
                key = 'field_' + my_field.id + '_%s' % o.uid
                error_result_key = my_field.id + '_%s' % o.uid
                REQUEST.cell = o
                try:
                  value = my_field._validate_helper(key, REQUEST) # We need cell
                  # Here we set the property
                  listbox[uid[4:]][sql] = value
                except ValidationError, err:
                  pass
                except KeyError:
                  pass
        # Here we generate again the object_list with listbox the listbox we
        # have just created
        if len(listbox)>0:
          list_method = field.get_value('list_method')
          list_method = getattr(here, list_method.method_name)
          REQUEST.set(field.id, listbox)
          object_list = list_method(REQUEST=REQUEST, **params)
        for uid in listbox_uids:
          if str(uid).find('new') == 0:
            # First case: dialog input to create new objects
            #o = newTempBase(here, uid[4:]) # Arghhh - XXX acquisition problem - use portal root
            #o.uid = uid
            o = None
            for object in object_list:
              if object.getUid()==uid:
                o = object
            if o is None:
              # First case: dialog input to create new objects
              o = newTempBase(portal, uid[4:]) # Arghhh - XXX acquisition problem - use portal root
              o.uid = uid
            result[uid[4:]] = {}
            for sql in editable_column_ids:
              alias = sql.replace('.', '_')
              if '.' in sql:
                property_id = '.'.join(sql.split('.')[1:]) # Only take trailing part
              else:
                property_id = alias
              my_field_id = '%s_%s' % (field.id, alias)
              if form.has_field( my_field_id ):
                my_field = form.get_field(my_field_id)
                REQUEST.cell = o
                if my_field.get_value('editable', REQUEST=REQUEST) and field.need_validate(REQUEST):
                  key = 'field_%s_%s' % (my_field.id, o.uid)
                  error_result_key = '%s_%s' % (my_field.id, o.uid)
                  try:
                    value = my_field._validate_helper(key, REQUEST) # We need cell
                    result[uid[4:]][sql] = value
                  except ValidationError, err:
                    #LOG("ListBox ValidationError",0,str(err))
                    err.field_id = error_result_key
                    errors.append(err)
          else:
            # Second case: modification of existing objects
            #try:
            if 1: #try:
              # We must try this
              # because sometimes, we can be provided bad uids
              try :
                o = here.portal_catalog.getObject(uid)
              except (KeyError, NotFound, ValueError):
                o = None
              if o is None:
                # It is possible that this object is not catalogged yet. So
                # the object must be obtained from ZODB.
                if not object_list:
                  list_method = field.get_value('list_method')
                  list_method = getattr(here, list_method.method_name)
                  object_list = list_method(REQUEST=REQUEST, **params)
                for object in object_list:
                  try:
                    if object.getUid() == int(uid):
                      o = object
                      break
                  except ValueError:
                    if str(object.getUid()) == uid:
                      o = object
                      break
              for sql in editable_column_ids:
                alias = sql.replace('.', '_')
                if '.' in sql:
                  property_id = '.'.join(sql.split('.')[1:]) # Only take trailing part
                else:
                  property_id = alias
                my_field_id = '%s_%s' % (field.id, alias)
                if form.has_field( my_field_id ):
                  my_field = form.get_field(my_field_id)
                  REQUEST.cell = o # We need cell
                  if my_field.get_value('editable', REQUEST=REQUEST) and field.need_validate(REQUEST):
                    tales_expr = my_field.tales.get('default', "")
                    key = 'field_' + my_field.id + '_%s' % o.uid
                    error_result_key = my_field.id + '_%s' % o.uid
                    try:
                      value = my_field.validator.validate(my_field, key, REQUEST) # We need cell
                      error_result[error_result_key] = value
                      if not result.has_key(o.getUrl()):
                        result[o.getUrl()] = {}
                      result[o.getUrl()][sql] = value
                    except ValidationError, err:
                      #LOG("ListBox ValidationError",0,str(err))
                      err.field_id = error_result_key
                      errors.append(err)
            #except:
            else:
              LOG("ListBox WARNING",0,"Object uid %s could not be validated" % uid)
        if len(errors) > 0:
            #LOG("ListBox FormValidationError",0,str(error_result))
            #LOG("ListBox FormValidationError",0,str(errors))
            raise FormValidationError(errors, error_result)
        return result

ListBoxValidatorInstance = ListBoxValidator()

class ListBox(ZMIField):
  meta_type = "ListBox"

  widget = ListBoxWidgetInstance
  validator = ListBoxValidatorInstance

  security = ClassSecurityInfo()

  security.declareProtected('Access contents information', 'get_value')
  def get_value(self, id, **kw):
    if (id == 'default'):
      if (kw.get('render_format') in ('list', )):
        request = kw.get('REQUEST', None)
        if request is None:
          request = get_request()
        # here the field can be a a proxyfield target, in this case just find
        # back the original proxy field so that renderer's calls to .get_value
        # are called on the proxyfield.
        field = request.get(
          'field__proxyfield_%s_%s_%s' % (self.id, self._p_oid, id),
          self)
        return self.widget.render(field, self.generate_field_key(), None,
                                  request,
                                  render_format=kw.get('render_format'),
                                  render_prefix=kw.get('render_prefix'))
      else:
        return None
    else:
      return ZMIField.get_value(self, id, **kw)

  security.declareProtected('Access contents information', 'getListMethodName')
  def getListMethodName(self):
    """Return the name of the list method. If not defined, return None.

       XXX - Is this method really necessary - I am not sure - JPS
       Why not use Formulator API instead ? -> the answer is that it is a
         MethodField, and it's method_name attribute is not available from
         restricted environment. It is only used in
         ERP5Site_checkNamingConventions

      XXX also this method is not compatible with ProxyFields.
      It will go away soon.
    """
    list_method = self.get_value('list_method')
    try:
      name = getattr(list_method, 'method_name')
    except AttributeError:
      name = list_method
    return name or None

class ListBoxLine:
  meta_type = "ListBoxLine"
  security = ClassSecurityInfo()
  #security.declareObjectPublic()

  def __init__(self):
    """
      Initialize the line and set the default values
      Selected columns must be defined in parameter of listbox.render...
    """

    self.is_title_line = 0
    self.is_data_line = 1
    self.is_stat_line = 0
    self.is_summary_line = 0

    self.is_section_folded = 1

    self.config_dict = {
      'is_checked' : 0,
      'uid' : None,
      'section_name' : None,
      'section_depth' : 0,
      'content_mode' : 'DataLine'
    }
    self.config_display_list = []

    self.column_dict = {}
    self.column_id_list = []
    self.row_css_class_name = ''
    
  security.declarePublic('__getitem__')
  def __getitem__(self, column_id):
    return self.getColumnProperty(column_id)

  #security.declarePublic('View')
  def setConfigProperty(self, config_id, config_value):
    self.config_dict[config_id] = config_value

  #security.declarePublic('View')
  def getConfigProperty(self, config_id):
    return self.config_dict[config_id]

  #security.declarePublic('View')
  def setListboxLineContentMode(self, content_mode):
    """
      Toogle the content type of the line
      content_mode can be 'TitleLine' 'StatLine' 'DataLine'
      Default value is 'DataLine'
    """
    content_mode_dict = {
      'TitleLine':(1,0,0,0),
      'DataLine':(0,1,0,0),
      'StatLine':(0,0,1,0),
      'SummaryLine':(0,0,0,1)
    }
    self.is_title_line,\
    self.is_data_line,\
    self.is_stat_line,\
    self.is_summary_line = content_mode_dict[content_mode]

    self.setConfigProperty('content_mode', content_mode)

  #security.declarePublic('View')
  def markTitleLine(self):
    """
      Set content of the line to 'TitleLine'
    """
    self.setListboxLineContentMode('TitleLine')

  security.declarePublic('isTitleLine')
  def isTitleLine(self):
    """
      Returns 1 is this line contains no data but only title of columns
    """
    return self.is_title_line

  #security.declarePublic('View')
  def markStatLine(self):
    """
      Set content of the line to 'StatLine'
    """
    self.setListboxLineContentMode('StatLine')

  security.declarePublic('isStatLine')
  def isStatLine(self):
    """
      Returns 1 is this line contains no data but only stats
    """
    return self.is_stat_line

  #security.declarePublic('View')
  def markDataLine(self):
    """
      Set content of the line to 'DataLine'
    """
    self.setListboxLineContentMode('DataLine')

  security.declarePublic('isDataLine')
  def isDataLine(self):
    """
      Returns 1 is this line contains data
    """
    return self.is_data_line

  #security.declarePublic('View')
  def markSummaryLine(self):
    """
      Set content of the line to 'SummaryLine'
    """
    self.setListboxLineContentMode('SummaryLine')

  security.declarePublic('isSummaryLine')
  def isSummaryLine(self):
    """
      Returns 1 is this line is a summary line
    """
    return self.is_summary_line

  #security.declarePublic('View')
  def checkLine(self, is_checked):
    """
      Set line to checked if is_checked=1
      Default value is 0
    """
    self.setConfigProperty('is_checked', is_checked)

  security.declarePublic('isLineChecked')
  def isLineChecked(self):
    """
      Returns 1 is this line is checked
    """
    return self.getConfigProperty('is_checked')

  #security.declarePublic('View')
  def setObjectUid(self, object_uid):
    """
      Define the uid of the object
      Default value is None
    """
    self.setConfigProperty('uid', object_uid)

  security.declarePublic('getObjectUid')
  def getObjectUid(self):
    """
      Get the uid of the object related to the line
    """
    return self.getConfigProperty('uid')

  #security.declarePublic('View')
  def setSectionName(self, section_name):
    """
      Set the section name of this line
      Default value is None
    """
    self.setConfigProperty('section_name', section_name)

  security.declarePublic('getSectionName')
  def getSectionName(self):
    """
      Returns the section name of this line
      Default value is None
    """
    return self.getConfigProperty('section_name')

  #security.declarePublic('View')
  def setSectionDepth(self, depth):
    """
      Set the section depth of this line
      default value is 0 and means no depth
    """
    self.setConfigProperty('section_depth', depth)

  security.declarePublic('getSectionDepth')
  def getSectionDepth(self):
    """
      Returns the section depth of this line
      0 means no depth
    """
    return self.getConfigProperty('section_depth')

  #security.declarePublic('View')
  def setSectionFolded(self, is_section_folded):
    """
      Set the section mode of this line to 'Folded' if is_section_folded=1
    """
    self.is_section_folded = is_section_folded

  security.declarePublic('isSectionFolded')
  def isSectionFolded(self):
    """
      Returns 1 if section is in 'Folded' Mode
    """
    return self.is_section_folded

  #security.declarePublic('View')
  def addColumn(self, column_id, column_value):
    """
      Add a new column
    """
    self.column_dict[column_id] = column_value
    self.column_id_list.append(column_id)

  security.declarePublic('getColumnProperty')
  def getColumnProperty(self, column_id):
    """
      Returns the property of a column
    """
    return self.column_dict[column_id]

  security.declarePublic('getColumnPropertyList')
  def getColumnPropertyList(self, column_id_list = None):
    """
      Returns a list of the property
      column_id_list selects the column_id returned
    """

    if column_id_list == None:
      column_id_list = self.column_id_list

    if self.isTitleLine():
      config_column = [None] * len(self.config_display_list)
    else:
      config_column = [self.config_dict[column_id] for column_id in self.config_display_list]

    return config_column + [self.column_dict[column_id] for column_id in column_id_list]

  security.declarePublic('getColumnPropertyTypeName')
  def getColumnPropertyTypeName(self, column_id):
    """
      Returns the type of a property of a column in
      the form of a string

      NOTE: experimental method - may change in the future
    """
    return type(self.column_dict[column_id]).__name__

  security.declarePublic('getColumnItemList')
  def getColumnItemList(self, column_id_list = None ):
    """
      Returns a list of property tuple
      column_id_list selects the column_id returned
    """

    if column_id_list == None:
      column_id_list = self.column_id_list

    """
    if self.isTitleLine():
      config_column = [None] * len(self.config_display_list)
    else:
      config_column = [(config_id, self.config_dict[column_id]) for config_id in self.config_display_list]
    """
    config_column = [(config_id, self.config_dict[config_id]) for config_id in self.config_display_list]

    return config_column + [(column_id , self.column_dict[column_id]) for column_id in column_id_list]

  security.declarePublic('setListboxLineDisplayListMode')
  def setListboxLineDisplayListMode(self, display_list):
    """
      Set the config columns displayable
      display_list can content the key of self.config_dict
      Default value of display_list is []
    """
    self.config_display_list = display_list

  security.declarePublic('setRowCSSClassName')
  def setRowCSSClassName(self, row_css_class_name):
    """Set the CSS class name of a row
    """
    self.row_css_class_name = row_css_class_name

  security.declarePublic('getRowCSSClassName')
  def getRowCSSClassName(self):
    """Return the CSS class name of a row
    """
    return self.row_css_class_name
  
InitializeClass(ListBoxLine)
allow_class(ListBoxLine)

# Psyco
from Products.ERP5Type.PsycoWrapper import psyco
#psyco.bind(ListBoxWidget.render)
psyco.bind(ListBoxValidator.validate)

# Register get_value
from Products.ERP5Form.ProxyField import registerOriginalGetValueClassAndArgument
registerOriginalGetValueClassAndArgument(ListBox, 'default')
