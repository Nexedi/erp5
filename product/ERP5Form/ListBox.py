##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import string, types, sys
from AccessControl import ClassSecurityInfo
from Products.Formulator.DummyField import fields
from Products.Formulator import Widget, Validator
from Products.Formulator.Field import ZMIField
from Products.Formulator.Form import BasicForm
from Products.Formulator.Errors import FormValidationError, ValidationError
from Products.Formulator.MethodField import BoundMethod
from Selection import Selection, DomainSelection
from DateTime import DateTime
from Products.ERP5Type.Utils import getPath
from Products.ERP5Type.Document import newTempBase
from Products.CMFCore.utils import getToolByName
from copy import copy

from Acquisition import aq_base, aq_inner, aq_parent, aq_self
from zLOG import LOG

from Globals import InitializeClass, Persistent, Acquisition
from Products.PythonScripts.Utility import allow_class

import random
import md5

def getAsList(a):
  l = []
  for e in a:
    l.append(e)
  return l

def makeTreeBody(form, root_dict, domain_path, depth, total_depth, unfolded_list, form_id, selection_name):
  """
    This method builds a report tree

    domain_path  --    ('region', 'skill', 'group', 'group', 'region')

    root -- {'region': <instance>, 'group'; instance}

  """
  LOG('makeTreeBody root_dict', 0, str(root_dict))
  LOG('makeTreeBody domain_path', 0, str(domain_path))
  LOG('makeTreeBody unfolded_list', 0, str(unfolded_list))

  if total_depth is None:
    total_depth = max(1, len(unfolded_list))

  if type(domain_path) is type('a'): domain_path = domain_path.split('/')

  portal_categories = getattr(form, 'portal_categories', None)
  portal_domains = getattr(form, 'portal_domains', None)
  portal_object = form.portal_url.getPortalObject()

  if len(domain_path):
    base_category = domain_path[0]
  else:
    base_category = None

  if root_dict is None:
    root_dict = {}

  is_empty_level = 1
  while is_empty_level:
    if not root_dict.has_key(base_category):
      root = None
      if portal_categories is not None:
        if base_category in portal_categories.objectIds():
          root = root_dict[base_category] = root_dict[None] = portal_categories[base_category]
          domain_path = domain_path[1:]
      if root is None and portal_domains is not None:
        if base_category in portal_domains.objectIds():
          root = root_dict[base_category] = root_dict[None] = portal_domains[base_category]
          domain_path = domain_path[1:]
      if root is None:
        try:
          root = root_dict[None] = portal_object.unrestrictedTraverse(domain_path)
        except KeyError:
          root = None
        domain_path = ()
    else:
      root = root_dict[None] = root_dict[base_category]
      if len(domain_path) >= 1:
        domain_path = domain_path[1:]
      else:
        domain_path = ()
    is_empty_level = (root.objectCount() == 0) and (len(domain_path) != 0)
    if is_empty_level: base_category = domain_path[0]

  tree_body = ''
  if root is None: return tree_body

  for o in root.objectValues():
    tree_body += '<TR>' + '<TD WIDTH="16" NOWRAP>' * depth
    if o.getRelativeUrl() in unfolded_list:
      tree_body += """<TD NOWRAP VALIGN="TOP" ALIGN="LEFT" COLSPAN="%s">
<a href="portal_selections/foldDomain?domain_url=%s&form_id=%s&list_selection_name=%s&domain_depth:int=%s" >- <b>%s</b></a>
</TD>""" % (total_depth - depth + 1, o.getRelativeUrl() , form_id, selection_name, depth, o.id)
      new_root_dict = root_dict.copy()
      new_root_dict[None] = new_root_dict[base_category] = o
      tree_body += makeTreeBody(form, new_root_dict, domain_path, depth + 1, total_depth, unfolded_list, form_id, selection_name)
    else:
      tree_body += """<TD NOWRAP VALIGN="TOP" ALIGN="LEFT" COLSPAN="%s">
<a href="portal_selections/unfoldDomain?domain_url=%s&form_id=%s&list_selection_name=%s&domain_depth:int=%s" >+ %s</a>
</TD>""" % (total_depth - depth + 1, o.getRelativeUrl() , form_id, selection_name, depth, o.id)

  return tree_body

def makeTreeList(form, root_dict, report_path, base_category, depth, unfolded_list, form_id, selection_name, report_depth, is_report_opened=1):
  """
    (object, is_pure_summary, depth, is_open, select_domain_dict)

    select_domain_dict is a dictionary of  associative list of (id, domain)
  """
  if type(report_path) is type('a'): report_path = report_path.split('/')

  portal_categories = getattr(form, 'portal_categories', None)
  portal_domains = getattr(form, 'portal_domains', None)
  portal_object = form.portal_url.getPortalObject()

  if len(report_path):
    base_category = report_path[0]

  if root_dict is None:
    root_dict = {}

  is_empty_level = 1
  while is_empty_level:
    if not root_dict.has_key(base_category):
      root = None
      if portal_categories is not None:
        if base_category in portal_categories.objectIds():
          root = root_dict[base_category] = root_dict[None] = portal_categories[base_category]
          report_path = report_path[1:]
      if root is None and portal_domains is not None:
        if base_category in portal_domains.objectIds():
          root = root_dict[base_category] = root_dict[None] = portal_domains[base_category]
          report_path = report_path[1:]
      if root is None:
        try:
          root = root_dict[None] = portal_object.unrestrictedTraverse(report_path)
        except KeyError:
          root = None
        report_path = ()
    else:
      root = root_dict[None] = root_dict[base_category]
      report_path = report_path[1:]
    is_empty_level = (root.objectCount() == 0) and (len(report_path) != 0)
    if is_empty_level: base_category = report_path[0]

  tree_list = []
  if root is None: return tree_list

  for o in root.objectValues():
    new_root_dict = root_dict.copy()
    new_root_dict[None] = new_root_dict[base_category] = o
    selection_domain = DomainSelection(domain_dict = new_root_dict)
    if (report_depth is not None and depth <= (report_depth - 1)) or o.getRelativeUrl() in unfolded_list:
      tree_list += [(o, 1, depth, 1, selection_domain)] # Summary (open)
      if is_report_opened :
        tree_list += [(o, 0, depth, 0, selection_domain)] # List (contents, closed, must be strict selection)
      tree_list += makeTreeList(form, new_root_dict, report_path, base_category, depth + 1, unfolded_list, form_id, selection_name, report_depth, is_report_opened=is_report_opened)
    else:
      tree_list += [(o, 1, depth, 0, selection_domain)] # Summary (closed)

  return tree_list


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
    property_names = Widget.Widget.property_names +\
                     ['lines', 'columns', 'all_columns', 'search_columns', 'sort_columns', 'sort',
                      'editable_columns', 'all_editable_columns', 'stat_columns', 'url_columns', 'global_attributes',
                      'list_method', 'stat_method', 'selection_name',
                      'meta_types', 'portal_types', 'default_params',
                      'search', 'select',
                      'domain_tree', 'domain_root_list',
                      'report_tree', 'report_root_list',
                      'list_action' ]

    default = fields.TextAreaField('default',
                                   title='Default',
                                   description=(
        "Default value of the text in the widget."),
                                   default="",
                                   width=20, height=3,
                                   required=0)

    lines = fields.IntegerField('lines',
                                title='Lines',
                                description=(
        "The number of lines of this list. Required."),
                                default=10,
                                required=1)

    columns = fields.ListTextAreaField('columns',
                                 title="Columns",
                                 description=(
        "A list of attributes names to display. Required."),
                                 default=[],
                                 required=1)

    all_columns = fields.ListTextAreaField('all_columns',
                                 title="More Columns",
                                 description=(
        "An optional list of attributes names to display."),
                                 default=[],
                                 required=0)

    search_columns = fields.ListTextAreaField('search_columns',
                                 title="Searchable Columns",
                                 description=(
        "An optional list of columns to search."),
                                 default=[],
                                 required=0)

    sort_columns = fields.ListTextAreaField('sort_columns',
                                 title="Sortable Columns",
                                 description=(
        "An optional list of columns to sort."),
                                 default=[],
                                 required=0)

    sort = fields.ListTextAreaField('sort',
                                 title='Default Sort',
                                 description=('The default sort keys and order'),
                                 default=[],
                                 required=0)

    list_method = fields.MethodField('list_method',
                                 title='List Method',
                                 description=('The method to use to list'
                                              'objects'),
                                 default='',
                                 required=0)

    stat_method = fields.MethodField('stat_method',
                                 title='Stat Method',
                                 description=('The method to use to count'
                                              'objects'),
                                 default='',
                                 required=0)

    selection_name = fields.StringField('selection_name',
                                 title='Selection Name',
                                 description=('The name of the selection to store'
                                              'params of selection'),
                                 default='',
                                 required=0)

    meta_types = fields.ListTextAreaField('meta_types',
                                 title="Meta Types",
                                 description=(
        "Meta Types of objects to list. Required."),
                                 default=[],
                                 required=0)

    portal_types = fields.ListTextAreaField('portal_types',
                                 title="Portal Types",
                                 description=(
        "Portal Types of objects to list. Required."),
                                 default=[],
                                 required=0)

    default_params = fields.ListTextAreaField('default_params',
                                 title="Default Parameters",
                                 description=(
        "Default Parameters for the List Method."),
                                 default=[],
                                 required=0)

    search = fields.CheckBoxField('search',
                                 title='Search Row',
                                 description=('Search Row'),
                                 default='',
                                 required=0)

    select = fields.CheckBoxField('select',
                                 title='Select Column',
                                 description=('Select Column'),
                                 default='',
                                 required=0)

    editable_columns = fields.ListTextAreaField('editable_columns',
                                 title="Editable Columns",
                                 description=(
        "An optional list of columns which can be modified."),
                                 default=[],
                                 required=0)

    all_editable_columns = fields.ListTextAreaField('all_editable_columns',
                                 title="All Editable Columns",
                                 description=(
        "An optional list of columns which can be modified."),
                                 default=[],
                                 required=0)

    stat_columns = fields.ListTextAreaField('stat_columns',
                                 title="Stat Columns",
                                 description=(
        "An optional list of columns which can be used for statistics."),
                                 default=[],
                                 required=0)

    url_columns = fields.ListTextAreaField('url_columns',
                                 title="URL Columns",
                                 description=(
        "An optional list of columns which can provide a custom URL."),
                                 default=[],
                                 required=0)

    global_attributes = fields.ListTextAreaField('global_attributes',
                                 title="Global Attributes",
                                 description=(
        "An optional list of attributes which are set by hidden fields and which are applied to each editable column."),
                                 default=[],
                                 required=0)

    domain_tree = fields.CheckBoxField('domain_tree',
                                 title='Domain Tree',
                                 description=('Selection Tree'),
                                 default='',
                                 required=0)

    domain_root_list = fields.ListTextAreaField('domain_root_list',
                                 title="Domain Root",
                                 description=(
        "A list of domains which define the possible root."),
                                 default=[],
                                 required=0)

    report_tree = fields.CheckBoxField('report_tree',
                                 title='Report Tree',
                                 description=('Report Tree'),
                                 default='',
                                 required=0)



    report_root_list = fields.ListTextAreaField('report_root_list',
                                 title="Report Root",
                                 description=(
        "A list of domains which define the possible root."),
                                 default=[],
                                 required=0)

    list_action = fields.StringField('list_action',
                                 title='List Action',
                                 description=('The id of the object action'
                                              'to display the current list'),
                                 default='',
                                 required=1)

    def render(self, field, key, value, REQUEST, render_format='html'):
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
        ###############################################################
        #
        # First, grasp and intialize the variables we may need later
        #
        ###############################################################

        here = REQUEST['here']
        reset = REQUEST.get('reset', 0)
        form = field.aq_parent
        field_errors = REQUEST.get('field_errors',{});
        field_title = field.get_value('title')
        lines = field.get_value('lines')
        meta_types = field.get_value('meta_types')
        portal_types= field.get_value('portal_types')
        columns = field.get_value('columns')
        all_columns = field.get_value('all_columns')
        default_params = field.get_value('default_params')
        search = field.get_value('search')
        select = field.get_value('select')
        sort = field.get_value('sort')
        editable_columns = field.get_value('editable_columns')
        all_editable_columns = field.get_value('all_editable_columns')
        stat_columns = field.get_value('stat_columns')
        url_columns = field.get_value('url_columns')
        search_columns = field.get_value('search_columns')
        sort_columns = field.get_value('sort_columns')
        domain_tree = field.get_value('domain_tree')
        report_tree = field.get_value('report_tree')
        domain_root_list = field.get_value('domain_root_list')
        report_root_list = field.get_value('report_root_list')
        list_method = field.get_value('list_method')
        stat_method = field.get_value('stat_method')
        selection_index = REQUEST.get('selection_index')
        selection_name = field.get_value('selection_name')
        portal_url_string = getToolByName(here, 'portal_url')()
        portal_categories = getattr(form, 'portal_categories', None)
        portal_domains = getattr(form, 'portal_domains', None)
        portal_object = form.portal_url.getPortalObject()
        #selection_name = REQUEST.get('selection_name',None)
        #if selection_name is None:
        #  selection_name = str(random.randrange(1,2147483600))
        current_selection_name = REQUEST.get('selection_name','default')
        current_selection_index = REQUEST.get('selection_index', 0)
        report_depth = REQUEST.get('report_depth', None)
        list_action = here.absolute_url() + '/' + field.get_value('list_action')
        if list_action.find('?') < 0:
          list_action += '?reset=1'
        else:
          list_action += '&reset=1'
        object_list = []
        translate = portal_object.translation_service.translate

        # Make sure list_result_item is defined
        list_result_item = [] 

        if render_format == 'list': 
          # initialize the result
          listboxline_list = []

        # Make sure that the title is not UTF-8.
        field_title = unicode(field_title, 'utf-8')

        # Make sure that columns are not UTF-8.
        columns = [(str(cname[0]), unicode(cname[1], 'utf-8')) for cname in columns]

        # Make sure that columns are not UTF-8.
        domain_root_list = [(str(cname[0]), unicode(cname[1], 'utf-8')) for cname in domain_root_list]

        #LOG('Listbox',0,'search_columns1: %s' % str(search_columns))
        if search_columns == [] or search_columns is None or search_columns == '':
          # We will set it as the schema
          search_columns = map(lambda x: [x,x],here.portal_catalog.schema())
          #LOG('Listbox',0,'search_columns2: %s' % str(search_columns))
        search_columns_id_list = map(lambda x: x[0], search_columns)

        if sort_columns == [] or sort_columns is None or sort_columns == '':
          sort_columns = search_columns
        sort_columns_id_list = map(lambda x: x[0], sort_columns)

        # Display statistics if the button Parameter exists or stat columns are defined explicitly.
        filtered_actions = here.portal_actions.listFilteredActionsFor(here);
        object_ui = filtered_actions.has_key('object_ui')
        show_stat = (object_ui or stat_columns)

        # If nothing is specified to stat_columns, assume that all columns are available.
        # For compatibility, because there was no stat_columns before.
        if not stat_columns:
          stat_columns = []
          for column in all_columns:
            stat_columns.append((column[0], column[0]))
          for column in columns: # Sometimes, all_columns is not defined
            stat_columns.append((column[0], column[0]))

        if not url_columns:
          url_columns = []

        has_catalog_path = None
        for (k, v) in all_columns:
          if k == 'catalog.path' or k == 'path':
            has_catalog_path = k
            break

        selection = here.portal_selections.getSelectionFor(selection_name, REQUEST=REQUEST)
        # Create selection if needed, with default sort order
        if selection is None:
          selection = Selection(params=default_params, default_sort_on = sort)
        # Or make sure all sort arguments are valid
        else:
          # Reset Selection is needed
          if reset is not 0 and reset is not '0':
            here.portal_selections.setSelectionToAll(selection_name)
            here.portal_selections.setSelectionSortOrder(selection_name, sort_on = [])

          # Modify the default sort index every time, because it may change immediately.
          selection.edit(default_sort_on = sort)

          # Filter non searchable items
          sort_list = []
          fix_sort = 0
          for (k , v) in selection.sort_on:
            if k in sort_columns_id_list:
              sort_list.append((k,v))
            else:
              fix_sort = 1
          if fix_sort: selection.sort_on = sort_list

        if not hasattr(selection, 'flat_list_mode'):
          # initialisation of render mode. Choose flat_list_mode by default
          selection.edit(flat_list_mode=1,domain_tree_mode=0,report_tree_mode=0)
          #selection.edit(flat_list_mode=(not (domain_tree or
          # report_tree)),domain_tree_mode=domain_tree,report_tree_mode= report_tree)

        #LOG('ListBox', 0, 'sort = %s, selection.selection_sort_on = %s' % (repr(sort), repr(selection.selection_sort_on)))
        # Selection
        #LOG("Selection",0,str(selection.__dict__))

        # Display choosen by the user

        if selection.flat_list_mode is not None:
          if selection.flat_list_mode == 1:
            domain_tree = 0
            report_tree = 0
          elif selection.domain_tree_mode == 1:
            domain_tree = 1
            report_tree = 0
          elif selection.report_tree_mode == 1:
            domain_tree = 0
            report_tree = 1

        # In report tree mode, we want to remember if the items have to be displayed
        is_report_opened = REQUEST.get('is_report_opened', selection.isReportOpened())
        selection.edit(report_opened=is_report_opened)

        checked_uids = selection.getCheckedUids()
        columns = here.portal_selections.getSelectionColumns(selection_name,
                                                columns=columns, REQUEST=REQUEST)


        editable_column_ids = map(lambda x: x[0], editable_columns)
        all_editable_column_ids = map(lambda x: x[0], all_editable_columns)

        url = REQUEST.URL

        # Build the list of meta_types
        filtered_meta_types = map(lambda x: x[0], meta_types)
        if len(filtered_meta_types) == 0:
          filtered_meta_types = None

        # Build the list of meta_types
        filtered_portal_types = map(lambda x: x[0], portal_types)
        if len(filtered_portal_types) == 0:
            filtered_portal_types = None

        # Combine default values, selection values and REQUEST
        params = selection.getParams()
        if list_method not in (None, ''):
          # Only update params if list_method is defined
          # (ie. do not update params in listboxed intended to show a previously defined selection
          params.update(REQUEST.form)
          for (k,v) in default_params:
            if REQUEST.form.has_key(k):
              params[k] = REQUEST.form[k]
            elif not params.has_key(k):
              params[k] = eval(v)

        # Allow overriding list_method and stat_method by params
        if params.has_key('list_method_id'):
          #try:
          list_method = getattr(here.portal_skins.local_list_method , params['list_method_id']) # Coramy specific
          #except:
          #  list_method = list_method
        if params.has_key('stat_method_id'):
          #try:
          list_method = getattr(here.portal_skins.local_list_method , params['stat_method_id']) # Coramy specific
          #except:
          #  list_method = list_method

        # Set the params spec (this should change in the future)
        if list_method not in (None, ''):
          # Only update params if list_method is defined
          # (ie. do not update params in listboxed intended to show a previously defined selection
          params['meta_type'] = filtered_meta_types
          params['portal_type'] = filtered_portal_types

        ###############################################################
        #
        # Build the columns selections
        #
        # The idea is: instead of selecting *, listbox is able to
        # provide what should be selected. This should allow to reduce
        # the quantity of data transfered between MySQL and Zope
        #
        ###############################################################
        extended_columns = []
        sql_columns = []
        for (sql, title) in columns:
          # original SQL id, Title, alias
          alias = string.split(sql,'.')
          alias = string.join(alias, '_')
          extended_columns += [(sql, title, alias)]
          if alias != sql:
            sql_columns += ['%s AS %s' % (sql, alias)]
          else:
            sql_columns += [alias]
        if has_catalog_path:
          alias = string.split(has_catalog_path,'.')
          alias = string.join(alias, '_')
          if alias != has_catalog_path:
            sql_columns += ['%s AS %s' % (has_catalog_path, alias)]
          else:
            sql_columns += [alias]
        sql_columns_string = string.join(sql_columns,' , ')
        params['select_columns'] = sql_columns_string

        ###############################################################
        #
        # Execute the query
        #
        ###############################################################

        kw = params

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
        if 'select_expression' in kw:
          del kw['select_expression']

        if hasattr(list_method, 'method_name'):
          if list_method.method_name == 'objectValues':
            list_method = here.objectValues
            kw = copy(params)
            kw['spec'] = filtered_meta_types
          else:
            # The Catalog Builds a Complex Query
            # So we should not pass too many variables
            kw = {}
            if REQUEST.form.has_key('portal_type'):
              kw['portal_type'] = REQUEST.form['portal_type']
            elif REQUEST.has_key('portal_type'):
              kw['portal_type'] = REQUEST['portal_type']
            elif filtered_portal_types is not None:
              kw['portal_type'] = filtered_portal_types
            elif filtered_meta_types is not None:
              kw['meta_type'] = filtered_meta_types
            elif kw.has_key('portal_type'):
              if kw['portal_type'] == '':
                del kw['portal_type']

            # Remove useless matter
            for cname in params.keys():
              if params[cname] != '' and params[cname]!=None:
                kw[cname] = params[cname]

            # Try to get the method through acquisition
            try:
              list_method = getattr(here, list_method.method_name)
            except:
              pass
        elif list_method in (None, ''): # Use current selection
          # Use previously used list method
          list_method = None


        # Lookup the stat_method
        if hasattr(stat_method, 'method_name'):
          if stat_method.method_name == 'objectValues':
            stat_method = None # Nothing to do in this case
            show_stat = 0
          elif stat_method.method_name == 'portal_catalog':
            # We use the catalog count results
            stat_method = here.portal_catalog.countResults
          else:
            # Try to get the method through acquisition
            try:
              stat_method = getattr(here, stat_method.method_name)
              show_stat = 1
            except:
              show_stat = 0
              pass
        else:
          stat_method = here.portal_catalog.countResults

        #LOG('ListBox', 0, 'domain_tree = %s, selection.getDomainPath() = %s, selection.getDomainList() = %s' % (repr(domain_tree), repr(selection.getDomainPath()), repr(selection.getDomainList())))
        if domain_tree:
          selection_domain_path = selection.getDomainPath()
          selection_domain_current = selection.getDomainList()
          if len(selection_domain_current) > 0:
            root_dict = {}
            for domain in selection_domain_current:
              if type(domain) != type(''): continue # XXX workaround for a past bug in Selection
              root = None
              base_category = domain.split('/')[0]
              if portal_categories is not None:
                if base_category in portal_categories.objectIds():
                  root = root_dict[base_category] = portal_categories.restrictedTraverse(domain)
              if root is None and portal_domains is not None:
                if base_category in portal_domains.objectIds():
                  root = root_dict[base_category] = portal_domains.restrictedTraverse(domain)
              if root is None:
                try:
                  root_dict[None] = portal_object.restrictedTraverse(domain)
                except KeyError:
                  root = None
              #LOG('domain_tree root aq_parent', 0, str(root_dict[base_category].aq_parent))
            selection.edit(domain = DomainSelection(domain_dict = root_dict))
            #LOG('selection.domain', 0, str(selection.domain.__dict__))
        else:
          selection.edit(domain = None)

        #LOG('ListBox', 0, 'list_method = %s, list_method.__dict__ = %s' % (repr(list_method), repr((list_method.__dict__))))

        ###############################################################
        #
        # Prepare the stat select_expression
        #
        ###############################################################
        select_expression = ''
        if show_stat:
          stats = here.portal_selections.getSelectionStats(selection_name, REQUEST=REQUEST)
          index = 0

          for (sql,title,alias) in extended_columns:
            # XXX This might be slow.
            for column in stat_columns:
              if column[0] == sql:
                break
            else:
              column = None
            if column is not None and column[0] == column[1]:
              try:
                if stats[index] != ' ':
                  select_expression += stats[index] + '(' + sql + ') AS ' + alias + ','
                else:
                  select_expression += '\'&nbsp;\' AS ' + alias + ','
              except:
                select_expression += '\'&nbsp;\' AS ' + alias + ','
            index = index + 1

          select_expression = select_expression[:len(select_expression) - 1]

        ###############################################################
        #
        # Build the report tree
        #
        # When we build the body, we have to go through all report lines
        #
        # Each report line is a tuple of the form:
        #
        # (section_id, is_summary, depth, object_list, object_list_size, is_open)
        #
        ###############################################################
        if report_tree:
          selection_report_path = selection.getReportPath()
          if report_depth is not None:
            selection_report_current = ()
          else:
            selection_report_current = selection.getReportList()
          report_tree_list = makeTreeList(form, None, selection_report_path, None,
                                          0, selection_report_current, form.id, selection_name, report_depth, is_report_opened)

          # Update report list if report_depth was specified
          if report_depth is not None:
            report_list = map(lambda s:s[0].getRelativeUrl(), report_tree_list)
            selection.edit(report_list=report_list)

          report_sections = []
          #LOG("Report Tree",0,str(report_tree_list))
          for s in report_tree_list:
            # Prepare query by defining selection report object
            selection.edit(report = s[4])
            if s[1]:
              # Push new select_expression
              original_select_expression = kw.get('select_expression')
              kw['select_expression'] = select_expression
              selection.edit( params = kw )
              #LOG('ListBox 569', 0, str((selection_name, selection.__dict__)))
              stat_temp = selection(method = stat_method, context=here, REQUEST=REQUEST)
              # Pop new select_expression
              if original_select_expression is None:
                del kw['select_expression']
              else:
                kw['select_expression'] = original_select_expression



              # stat_result is a list
              # we want now to make it a dictionnary
              # Is this a report line
              # object_stat = ....
              stat_result = {}
              index = 1

              for (k,v) in columns:
                try:
                  stat_result[k] = str(stat_temp[0][index])
                except IndexError:
                  stat_result[k] = ''
                index = index + 1

              stat_context = s[0].asContext(**stat_result)
              stat_context.absolute_url = lambda x: s[0].absolute_url()
              stat_context.domain_url = s[0].getRelativeUrl()
              report_sections += [(s[0].id, 1, s[2], [stat_context], 1, s[3], s[4])]
            else:
              # Prepare query
              selection.edit( params = kw )
              if list_method not in (None, ''):
                object_list = selection(method = list_method, context=here, REQUEST=REQUEST)
              else:
                # If list_method is None, use already selected values.
                object_list = here.portal_selections.getSelectionValueList(selection_name, context=here, REQUEST=REQUEST)
#               # PERFORMANCE ? is len(object_list) fast enough ?
              report_sections += [ (None, 0, s[2], object_list, len(object_list), s[3], s[4]) ]

          # Reset original value
          selection.edit(report = None)
        else:
          selection.edit( params = kw, report = None )
          #LOG('ListBox 612', 0, str((selection_name, selection.__dict__)))
          if list_method not in (None, ''):
            object_list = selection(method = list_method, context=here, REQUEST=REQUEST)
          else:
            # If list_method is None, use already selected values.
            object_list = here.portal_selections.getSelectionValueList(selection_name, context=here, REQUEST=REQUEST)
          # PERFORMANCE PROBLEM ? is len(object_list) fast enough ?
          report_sections = ( (None, 0, 0, object_list, len(object_list), 0),  )


        ###############################################################
        #
        # Build an md5 signature of the selection
        #
        # It is calculated based on the selection uid list
        # It is used in order to do some checks in scripts.
        # For example, if we do delete objects, then we do have a list of
        # objects to delete, but it is possible that on another tab the selection
        # change, and then when we confirm the deletion, we don't delete what
        # we want, so this is really dangerous. with this md5 we can check if the
        # selection is the same
        #
        ###############################################################

        object_uid_list = map(lambda x: getattr(x, 'uid', None), object_list)
        #LOG('ListBox.render, object_uid_list:',0,object_uid_list)
        sorted_object_uid_list = copy(object_uid_list)
        sorted_object_uid_list.sort()
        md5_string = md5.new(str(sorted_object_uid_list)).hexdigest()
        #md5_string = md5.new(str(object_uid_list)).digest()


        ###############################################################
        #
        # Calculate list start and stop
        #
        # Build the real list by slicing it
        # PERFORMANCE ANALYSIS: the result of the query should be
        # if possible a lazy sequence
        #
        ###############################################################

        #LOG("Selection", 0, str(selection.__dict__))
        total_size = 0
        for s in report_sections:
          total_size += s[4]
        if render_format == 'list':
          start = 0
          end = total_size
          total_pages = 1
          current_page = 0
        else:
          try:
            start = REQUEST.get('list_start')
            start = int(start)
          except:
            start = params.get('list_start',0)
            start = int(start)
          end = min(start + lines, total_size)
          #object_list = object_list[start:end]
          total_pages = int(max(total_size-1,0) / lines) + 1
          current_page = int(start / lines)
          start = max(start, 0)
          start = min(start, max(0, total_pages * lines - lines) )
          kw['list_start'] = start
          kw['list_lines'] = lines

        ###############################################################
        #
        # Store new selection values
        #
        # Store the resulting selection if list_method is not None and render_format is not list
        #
        ###############################################################
        if list_method is not None and render_format != 'list':
          try:
            method_path = getPath(here) + '/' + list_method.method_name
            #LOG('ListBox', 0, 'method_path = %s, getPath = %s, list_method.method_name = %s' % (repr(method_path), repr(getPath(here)), repr(list_method.method_name)))
          except:
            method_path = getPath(here) + '/' + list_method.__name__
            #LOG('ListBox', 0, 'method_path = %s, getPath = %s, list_method.__name__ = %s' % (repr(method_path), repr(getPath(here)), repr(list_method.__name__)))
          # Sometimes the seltion name is a list ??? Why ????
          if type(current_selection_name) in (type(()),type([])):
            current_selection_name = current_selection_name[0]
          list_url =  url+'?selection_name='+current_selection_name+'&selection_index='+str(selection_index)
          selection.edit( method_path= method_path, params = kw, list_url = list_url)
          #LOG("Selection kw", 0, str(selection.selection_params))
          here.portal_selections.setSelectionFor(selection_name, selection, REQUEST=REQUEST)

        ###############################################################
        #
        # Build HTML header and footer
        #
        ###############################################################

        # Provide the selection name
        selection_line = """\
<input type="hidden" name="list_selection_name" value="%s" />
""" % selection_name
        selection_line +="""\
<input type="hidden" name="md5_object_uid_list" value="%s" />
""" % md5_string

        # Create the Page Selector
        if start == 0:
          pages = """\
   <td nowrap valign="middle" align="center">
   </td>
   <td nowrap valign="middle" align="center">
    <select name="list_start" title="%s" size="1"
      onChange="submitAction(this.form,'%s/portal_selections/setPage')">
""" % (translate('ui', 'Change Page'), REQUEST.URL1)
        else:
          pages = """\
   <td nowrap valign="middle" align="center">
    <input type="image" src="%s/images/1leftarrowv.png"
      title="%s" name="portal_selections/previousPage:method" border="0" />
   </td>
   <td nowrap valign="middle" align="center">
    <select name="list_start" title="%s" size="1"
      onChange="submitAction(this.form,'%s/portal_selections/setPage')">
""" % (portal_url_string, translate('ui', 'Previous Page'), translate('ui', 'Change Page'), REQUEST.URL1)
        for p in range(0, total_pages):
          if p == current_page:
            selected = 'selected'
          else:
            selected = ''
          pages += '<option %s value="%s">%s</option>\n' \
                  % (selected,
                     p * lines,
                     translate('ui', '${page} of ${total_pages}',
                               mapping = {'page' : p+1, 'total_pages': total_pages}))

        if current_page == total_pages - 1:
          pages += """\
    </select>
   </td>
   <td nowrap valign="middle" align="center">
   </td>
"""
        else:
          pages += """\
    </select>
   </td>
   <td nowrap valign="middle" align="center">
    <input type="image" src="%s/images/1rightarrowv.png"
      title="%s" name="portal_selections/nextPage:method" border="0" />
   </td>
""" % (portal_url_string, translate('ui', 'Next Page'))
        # Create the header of the table - this should probably become DTML
        # Create also View Selector which enables to switch from a view mode
        # to another directly from the listbox
        #LOG('ListBox', 0, 'field_title = %s, translate(\'ui\', field_title) + %s' % (repr(field_title), repr(translate('ui', field_title))))
        format_dict = {
                        'portal_url_string' : portal_url_string,
                        'list_action' : list_action,
                        'field_title' : translate('ui', field_title),
                        'pages' : pages,
                        'record_number' : translate('ui', '${number} record(s)',
                                                    mapping = { 'number' : str(total_size) }),
                        'item_number' : translate('ui', '${number} item(s) selected',
                                                  mapping = { 'number' : str(len(checked_uids)) }),
                        'flat_list_title': translate('ui', 'Flat List'),
                        'report_tree_title': translate('ui', 'Report Tree'),
                        'domain_tree_title': translate('ui', 'Domain Tree'),
                      }
        header = """\
<!-- List Summary -->
<div class="ListSummary">
 <table border="0" cellpadding="0" cellspacing="0">
  <tr height="10">
   <td height="10"><img src="%(portal_url_string)s/images/Left.png" border="0"></td>
   <td class="Top" colspan="2" height="10">
    <img src="%(portal_url_string)s/images/spacer.png" width="5" height="10" border="0"
      alt="spacer"/></td>
   <td class="Top" colspan="3" height="10">
    <img src="%(portal_url_string)s/images/spacer.png" width="5" height="10" border="0"
      alt="spacer"/>
   </td>
  </tr>
  <tr>
   <td class="Left" width="17">
    <img src="%(portal_url_string)s/images/spacer.png" width="5" height="5" border="0"
        alt="spacer"/>
   </td>
   <td valign="middle" nowrap>

    <input type="image" src="%(portal_url_string)s/images/text_block.png" id="flat_list"
       title="%(flat_list_title)s" name="portal_selections/setFlatListMode:method" value="1" border="0" alt="img"/">
    <input type="image" src="%(portal_url_string)s/images/view_tree.png" id="flat_list"
       title="%(report_tree_title)s" name="portal_selections/setReportTreeMode:method" value="1" border="0" alt="img"/">
        <input type="image" src="%(portal_url_string)s/images/view_choose.png" id="flat_list"
       title="%(domain_tree_title)s" name="portal_selections/setDomainTreeMode:method" value="1" border="0" alt="img"/"></td>
   <td width="100%%" valign="middle">&nbsp; <a href="%(list_action)s">%(field_title)s</a>:
        %(record_number)s - %(item_number)s
   </td>
   %(pages)s
  </tr>
 </table>
</div>
<!-- List Content -->
<div class="ListContent">
 <table cellpadding="0" cellspacing="0" border="0">
""" % format_dict

        # pages

        # Create the footer. This should be replaced by DTML
        # And work as some kind of parameter

        footer = """\
      </div>
     </td>
    </div>
   </tr>
   <tr >
    <td colspan="%s" width="50" align="center" valign="middle"
        class="DataA">
    </td>
   </tr>
  </table>
 </div>
""" % (len(columns))

        # Create the header of the table with the name of the columns
        # Create also Report Tree Column if needed
        if report_tree:
          report_tree_options = ''
          for c in report_root_list:
            if c[0] == selection_report_path:
              report_tree_options += """<option selected value="%s">%s</option>\n""" % (c[0], c[1])
            else:
              report_tree_options += """<option value="%s">%s</option>\n""" % (c[0], c[1])
          report_popup = """<select name="report_root_url"
onChange="submitAction(this.form,'%s/portal_selections/setReportRoot')">
        %s</select>""" % (here.getUrl(),report_tree_options)
          report_popup = """
  <td class="Data" width="50" align="center" valign="middle">
  %s
  </td>
""" % report_popup
        else:
          report_popup = ''

        if select:
          format_dict = {
                          'portal_url_string' : portal_url_string,
                          'report_popup' : report_popup,
                          'check_all_title' : translate('ui', 'Check All'),
                          'uncheck_all_title' : translate('ui', 'Uncheck All'),
                        }
          list_header = """\
<tr>%(report_popup)s
   <td class="Data" width="50" align="center" valign="middle">
    <input type="image" name="portal_selections/checkAll:method" value="1"
      src="%(portal_url_string)s/images/checkall.png" border="0" alt="Check All" title=%(check_all_title)s />
    <input type="image" name="portal_selections/uncheckAll:method" value="1"
      src="%(portal_url_string)s/images/decheckall.png" border="0" alt="Uncheck All" title=%(uncheck_all_title)s />
""" % format_dict
        else:
          list_header = """\
<tr>%s
""" % report_popup

        # csort is a list of couples
        # we should convert it into a dict because a list of couples would need
        # a loop in each loop
        sort_dict = {}
        csort = here.portal_selections.getSelectionSortOrder(selection_name)
        for index in csort:
          sort_dict[index[0]] = index[1]

        for cname in columns:
          if sort_dict.has_key(cname[0]):
            if sort_dict[cname[0]] == 'ascending':
              img = '<img src="%s/images/1bottomarrow.png" alt="Ascending display">' % portal_url_string
            elif sort_dict[cname[0]] == 'descending':
              img = '<img src="%s/images/1toparrow.png" alt="Descending display">' % portal_url_string
            else:
              img = ''
          else:
            img = ''
          #LOG('ListBox', 0, 'cname = %r' % (cname,))
          if cname[0] in search_columns_id_list:
            #LOG('ListBox', 0, 'str(cname[1]) = %s, translate(\'ui\',str(cname[1])) = %s' % (repr(str(cname[1])), repr(translate('ui',str(cname[1])))))
            list_header += ("<td class=\"Data\"><a href=\"%s/portal_selections/setSelectionQuickSortOrder?selection_name=%s&sort_on=%s\">%s</a> %s</td>\n" %
                (here.absolute_url(),str(selection_name),cname[0],translate('ui',cname[1]),img))
          else:
            list_header += ("<td class=\"Data\">%s</td>\n" % translate('ui', cname[1]))
        list_header = list_header + "</tr>"

        # Create the search row of the table with the name of the columns
        if search:
          # Add empty column for report
          if report_tree:
            depth_selector = ''
            for i in range(0,6):
              # XXX We may lose previous list information
              depth_selector += """&nbsp;<a href="%s/%s?selection_name=%s&selection_index=%s&report_depth:int=%s">%s</a>""" % \
                                       (here.absolute_url(), form.id, current_selection_name, current_selection_index , i, i)
            # In report mode, we may want to hide items, and only display stat lines.
            depth_selector += """&nbsp;-&nbsp;<a href="%s/%s?selection_name=%s&selection_index=%s&is_report_opened:int=%s">%s</a>""" % \
                                     (here.absolute_url(), form.id, current_selection_name, current_selection_index , 1 - is_report_opened, is_report_opened and 'Hide' or 'Show')
            report_search = """<td class="Data" width="50" align="left" valign="middle">%s</td>""" % depth_selector
          else:
            report_search = ""

          if select:
            list_search ="""\
  <tr >
   %s
   <td class="Data" width="50" align="center" valign="middle">
     <input type="image" src="%s/images/exec16.png" title="%s" alt="Action" name="Base_doSelect:method" />
   </td>
""" % (report_search,portal_url_string,translate('ui', 'Action')) # XXX Action? Is this word appropriate here?
          else:
            list_search ="""\
  <tr >
  %s
""" % report_search

          for cname in extended_columns:
            if cname[0] in search_columns_id_list:
              alias = str(cname[2])
              if type(alias) == type(''):
                alias = unicode(alias, 'utf-8')
              param = params.get(alias,'')
              if type(param) == type(''):
                param = unicode(param, 'utf-8')
              list_search += """\
     <td class="DataB">
       <font size="-3"><input name="%s" size="8" value="%s"></font>
     </td>
""" % (alias, param)
            else:
              list_search = list_search + (
                "<td class=\"DataB\"></td> ")

          list_search = list_search + "</tr>"
        else:
          list_search = ''

        # Build the tuple of columns
        if render_format == 'list':
          c_name_list = []
          c_property_id_list = []
          for cname in columns:
            c_name_list.append(cname[1])
            c_property_id_list.append(cname[0])

        ###############################################################
        #
        # Build lines
        #
        ###############################################################


        # Build Lines
        list_body = ''


        if render_format == 'list': 
          # initialize the title line
          title_listboxline = ListBoxLine()
          title_listboxline.markTitleLine()
          for cname in columns:
            title_listboxline.addColumn( cname[0].encode('utf-8'), cname[1].encode('utf-8'))
          listboxline_list.append(title_listboxline)  

        section_index = 0
        current_section_base_index = 0
        if len(report_sections) > section_index:
          current_section = report_sections[section_index]
        elif len(report_sections):
          current_section = report_sections[0]
        else:
          current_section = None
        if current_section is not None:
          current_section_size = current_section[4]
          object_list = current_section[3]
          #if current_section is not None:
          for i in range(start,end):

            if render_format == 'list':
              # Create a ListBoxLine object
              current_listboxline = ListBoxLine()
              current_listboxline.markDataLine()
            

            # Set the selection index.
            selection.edit(index = i)

            # Make sure we go to the right section
            while current_section_base_index + current_section_size <= i:
              current_section_base_index += current_section[4]
              section_index += 1
              current_section = report_sections[section_index]
              current_section_size = current_section[4]
              object_list = current_section[3]

            is_summary = current_section[1] # Update summary type

            list_body = list_body + '<tr>'
            o = object_list[i - current_section_base_index] # FASTER PERFORMANCE
            real_o = None

            # Define the CSS
            if not (i - start) % 2:
              td_css = 'DataA'
            else:
              td_css = 'DataB'

            list_body = list_body + \
  """<input type="hidden" value="%s" name="%s_uid:list"/>
  """ % ( getattr(o, 'uid', '') , field.id ) # What happens if we list instances which are not instances of Base XXX

            section_char = ''
            if report_tree:
              if is_summary:
                # This is a summary
                section_name = current_section[0]
              else:
                section_name = ''
                
              if current_section[5]:
                if section_name != '':
                  section_char = '-'
                list_body = list_body + \
  """<td class="%s" align="left" valign="middle"><a href="portal_selections/foldReport?report_url=%s&form_id=%s&list_selection_name=%s">%s%s%s</a></td>
  """ % (td_css, getattr(current_section[3][0],'domain_url',''), form.id, selection_name, '&nbsp;&nbsp;' * current_section[2], section_char, section_name)
  
                if render_format == 'list': 
                  
                  if is_summary:
                    current_listboxline.markSummaryLine()
                  # XXX temporary correction (I dont some '' which havent signification)
                  if section_name == '':
                    section_name = None

                  current_listboxline.setSectionDepth( current_section[2]+1 )
                  current_listboxline.setSectionName( section_name )
                  current_listboxline.setSectionFolded( 0 )

              else:
                if section_name != '':
                  section_char = '+'
                list_body = list_body + \
  """<td class="%s" align="left" valign="middle"><a href="portal_selections/unfoldReport?report_url=%s&form_id=%s&list_selection_name=%s">%s%s%s</a></td>
  """ % (td_css, getattr(current_section[3][0],'domain_url',''), form.id, selection_name, '&nbsp;&nbsp;' * current_section[2], section_char, section_name)

                if render_format == 'list': 
                  
                  if is_summary:
                    current_listboxline.markSummaryLine()
                  # XXX temporary correction (I dont some '' which havent signification)
                  if section_name == '':
                    section_name = None

                  current_listboxline.setSectionDepth( current_section[2]+1 )
                  current_listboxline.setSectionName( section_name )
                  current_listboxline.setSectionFolded( 1 )

            if select:
              if o.uid in checked_uids:
                selected = 'checked'
              else:
                selected = ''
              if section_char != '':
                list_body = list_body + \
  """<td class="%s" width="50" align="center" valign="middle">&nbsp;</td>
  """ % (td_css, )
              else:
                list_body = list_body + \
  """<td class="%s" width="50" align="center" valign="middle">&nbsp;
  <input type="checkbox" %s value="%s" id="cb_%s" name="uids:list"/></td>
  """ % (td_css, selected, o.uid , o.uid)
            error_list = []


            if render_format == 'list': 
              if selected == '':
                current_listboxline.setObjectUid( o.uid )
                current_listboxline.checkLine( 0 )
              else:
                current_listboxline.setObjectUid( o.uid )
                current_listboxline.checkLine( 1 )
            
            for cname in extended_columns:
              # add attribute_original_value, because I need to know the type of the attribute 
              attribute_original_value = None

              sql = cname[0] # (sql, title, alias)
              alias = cname[2] # (sql, title, alias)
              if '.' in sql:
                property_id = '.'.join(sql.split('.')[1:]) # Only take trailing part
              else:
                property_id = alias
  #            attribute_value = getattr(o, cname_id) # FUTURE WAY OF DOING TGW Brains
              my_field = None
              tales_expr = None
              if form.has_field('%s_%s' % (field.id, alias) ) and not is_summary:
                my_field_id = '%s_%s' % (field.id, alias)
                my_field = form.get_field(my_field_id)
                tales_expr = my_field.tales.get('default', "")
              if tales_expr:
                #
                real_o = o
                if hasattr(o,'getObject'): # we have a line of sql result
                  real_o = o.getObject()
                field_kw = {'cell':real_o}
                attribute_value = my_field.__of__(real_o).get_value('default',**field_kw)
                attribute_original_value = attribute_value
              else:
                # Prepare stat_column is this is a summary
                if is_summary:
                  # Use stat method to find value
                  for stat_column in stat_columns:
                    if stat_column[0] == sql:
                      break
                  else:
                    stat_column = None
                if hasattr(aq_self(o),alias) and (not is_summary or stat_column is None or stat_column[0] == stat_column[1]): # Block acquisition to reduce risks
                  # First take the indexed value
                  attribute_value = getattr(o,alias) # We may need acquisition in case of method call
                  attribute_original_value = attribute_value
                elif is_summary:
                  attribute_value = getattr(here, stat_column[1])
                  attribute_original_value = attribute_value
                  #LOG('ListBox', 0, 'column = %s, value = %s' % (repr(column), repr(value)))
                  if callable(attribute_value):
                    try:
                      # set report and closed_summary
                      if report_tree == 1 :
                        selection.edit(report=current_section[6])
                        kw['closed_summary'] = 1 - current_section[5]
                        params = dict(kw)
                        selection.edit(params=params)
                      attribute_value=attribute_value(selection=selection)
                      attribute_original_value = attribute_value
                      # reset report and closed_summary
                      if report_tree == 1 :
                        selection.edit(report=None)
                        del kw['closed_summary']
                        params = dict(kw)
                        selection.edit(params=params)
                    except:
                      LOG('ListBox', 0, 'WARNING: Could not call %s with %s: ' % (repr(attribute_value), repr(params)), error=sys.exc_info())
                      pass
                else:
    #             MUST IMPROVE FOR PERFORMANCE REASON
    #             attribute_value = 'Does not exist'
                  if real_o is None:
                    try:
                      real_o = o.getObject()
                    except:
                      pass
                  if real_o is not None:
                    try:
                      try:
                        attribute_value = getattr(real_o,property_id, None)
                        attribute_original_value = attribute_value
                        #LOG('Look up attribute %s' % cname_id,0,str(attribute_value))
                        if not callable(attribute_value):
                          #LOG('Look up accessor %s' % cname_id,0,'')
                          attribute_value = real_o.getProperty(property_id)
                          attribute_original_value = attribute_value

                          #LOG('Look up accessor %s' % cname_id,0,str(attribute_value))
                      except:
                        attribute_value = getattr(real_o,property_id)
                        attribute_original_value = attribute_value
                        #LOG('Fallback to attribute %s' % cname_id,0,str(attribute_value))
                    except:
                      attribute_value = 'Can not evaluate attribute: %s' % sql
                      attribute_original_value = None
                  else:
                    attribute_value = 'Object does not exist'
                    attribute_original_value = None
              if callable(attribute_value):
                try:
                  try:
                    attribute_value = attribute_value(brain = o, selection = selection)
                    attribute_original_value = attribute_value
                  except TypeError:
                    attribute_value = attribute_value()
                    attribute_original_value = attribute_value
                except:
                  LOG('ListBox', 0, 'Could not evaluate', error=sys.exc_info())
                  attribute_value = "Could not evaluate"
                  attribute_original_value = None
              #LOG('ListBox', 0, 'o = %s' % repr(dir(o)))
              if type(attribute_value) is type(0.0):
                attribute_original_value = attribute_value
                if sql in editable_column_ids and form.has_field('%s_%s' % (field.id, alias) ):
                  # Do not truncate if editable
                  pass
                else:
                  #attribute_original_value = attribute_value
                  attribute_value = "%.2f" % attribute_value
                td_align = "right"
              elif type(attribute_value) is type(1):
                attribute_original_value = attribute_value
                td_align = "right"
              else:
                td_align = "left"
              # It is safer to convert attribute_value to an unicode string, because
              # it might be utf-8.
              if type(attribute_value) == type(''):
                attribute_value = unicode(attribute_value, 'utf-8')
                attribute_original_value = attribute_value
              elif attribute_value is None:
                attribute_original_value = None
                attribute_value = ''
              if sql in editable_column_ids and form.has_field('%s_%s' % (field.id, alias) ):
                key = my_field.id + '_%s' % o.uid
                if field_errors.has_key(key):
                  error_css = 'Error'
                  error_message = "<br/>%s" % translate('ui', field_errors[key].error_text)
                  # Display previous value (in case of error
                  error_list.append(field_errors.get(key))
                  display_value = REQUEST.get('field_%s' % key, attribute_value)
                else:
                  error_css = ''
                  error_message = ''
                  #display_value = REQUEST.get('field_%s' % key, attribute_value)
                  display_value = attribute_value # XXX Make sure this is ok
                #LOG('ListBox', 0, 'display_value = %r' % display_value)
                if type(display_value) == type(u''):
                  display_value = display_value.encode('utf-8')
                cell_body = my_field.render(value = display_value, REQUEST = o, key = key)
                                                              # We use REQUEST which is not so good here
                                                              # This prevents from using standard display process
                # It is safer to convert cell_body to an unicode string, because
                # it might be utf-8.
                if type(cell_body) == type(''):
                  cell_body = unicode(cell_body, 'utf-8')
                #LOG('ListBox', 0, 'cell_body = %r, error_message = %r' % (cell_body, error_message))
                list_body += ('<td class=\"%s%s\">%s%s</td>' % (td_css, error_css, cell_body, error_message))
                

                # Add item to list_result_item for list render format
                if render_format == 'list':
                  current_listboxline.addColumn(property_id , my_field._get_default(self.generate_field_key(), attribute_original_value, o))

              else:
                # Check if url_columns defines a method to retrieve the URL.
                url_method = None
                for column in url_columns:
                  if sql == column[0]:
                    url_method = getattr(o, column[1], '')
                    break
                if url_method is not None:
                  try:
                    object_url = url_method(brain = o, selection = selection)
                    list_body = list_body + \
                      ("<td class=\"%s\" align=\"%s\"><a href=\"%s\">%s</a></td>" %
                        (td_css, td_align, object_url, attribute_value))
                  except:
                    LOG('ListBox', 0, 'Could not evaluate url_method %s' % column[1], error=sys.exc_info())
                    list_body = list_body + \
                      ("<td class=\"%s\" align=\"%s\">%s</td>" % (td_css, td_align, attribute_value) )
                else:
                  # Check if this object provides a specific URL method
                  url_method = getattr(o, 'getListItemUrl', None)
                  if url_method is None:
                    try:
                      object_url = o.absolute_url() + \
                        '/view?selection_index=%s&selection_name=%s&reset=1' % (i, selection_name)
                      list_body = list_body + \
                        ("<td class=\"%s\" align=\"%s\"><a href=\"%s\">%s</a></td>" %
                          (td_css, td_align, object_url, attribute_value))
                    except:
                      list_body = list_body + \
                        ("<td class=\"%s\" align=\"%s\">%s</td>" % (td_css, td_align, attribute_value) )
                  else:
                    try:
                      object_url = url_method(alias, i, selection_name)
                      list_body = list_body + \
                        ("<td class=\"%s\" align=\"%s\"><a href=\"%s\">%s</a></td>" %
                          (td_css, td_align, object_url, attribute_value))
                    except:
                      list_body = list_body + \
                        ("<td class=\"%s\" align=\"%s\">%s</td>" % (td_css, td_align, attribute_value) )


                if render_format == 'list': 
                  # Make sure that attribute value is UTF-8
                  attribute_value_tmp  = attribute_original_value
                  if type(attribute_value_tmp) == type(u''):
                    attribute_value_tmp = attribute_original_value.encode('utf-8')

                  # XXX this is horrible, but it would be better without those &nbsp; ....
                  if type(attribute_value_tmp) == type(''):
                    if 'nbsp' in attribute_value_tmp:
                      attribute_value_tmp = None
                    
                  current_listboxline.addColumn( property_id , attribute_value_tmp)

            list_body = list_body + '</tr>'


            if render_format == 'list':
              listboxline_list.append(current_listboxline)  
              
        ###############################################################
        #
        # Build statistics
        #
        ###############################################################

        # Call the stat method
        if show_stat:

          if render_format == 'list':
            # Create a ListBoxLine object
            current_listboxline = ListBoxLine()
            current_listboxline.markStatLine()
            
          kw['select_expression'] = select_expression
          selection.edit( params = kw )

          count_results = selection(method = stat_method,
                          context=here, REQUEST=REQUEST)
          list_body = list_body + '<tr>'
    
              
          if report_tree:
            list_body += '<td class="Data">&nbsp;</td>'
          if select:
            list_body += '<td class="Data">&nbsp;</td>'
          for n in range((len(extended_columns))):
            try:
              sql = extended_columns[n][0]
              for column in stat_columns:
                if column[0] == sql:
                  break
              else:
                column = None
              #LOG('ListBox', 0, 'n = %s, extended_columns = %s, stat_columns = %s, column = %s' % (repr(n), repr(extended_columns), repr(stat_columns), repr(column)))
              if column is not None:
                if column[0] == column[1]:
                  alias = extended_columns[n][2]
                  value = getattr(count_results[0],alias,'')
                else:
                  value = getattr(here, column[1])
                  #LOG('ListBox', 0, 'column = %s, value = %s' % (repr(column), repr(value)))
                  if callable(value):
                    try:
                      #params = dict(kw)
                      #params['operator'] = stats[n]
                      #value=value(**params)
                      value=value(selection=selection)
                    except:
                      LOG('ListBox', 0, 'WARNING: Could not call %s with %s: ' % (repr(value), repr(params)), error=sys.exc_info())
                      pass
                if type(value) is type(1.0):
                  list_body += '<td class="Data" align="right">%.2f</td>' % value
                else:
                  list_body += '<td class="Data">' + str(value) + '</td>'


                if render_format == 'list': 
                  # Make sure that attribute value is UTF-8
                  value_tmp  = value
                  if type(value) == type(u''):
                    value_tmp = value.encode('utf-8')

                  # XXX this is horrible, but it would be better without those &nbsp; ....
                  if type(value_tmp) == type(''):
                    if 'nbsp' in value_tmp:
                      value_tmp = None
                    
                  current_listboxline.addColumn( column[1] , value_tmp )

              else:
                list_body += '<td class="Data">&nbsp;</td>'
                if render_format == 'list': current_listboxline.addColumn( column[1] , None)
            except:
              list_body += '<td class="Data">&nbsp;</td>'
              if render_format == 'list': current_listboxline.addColumn( column[1] , None)
          list_body += '</tr>'

          if render_format == 'list':
            listboxline_list.append(current_listboxline)  
          
        #LOG('ListBox', 0, 'header = %r, selection_list = %r, list_header = %r, list_search = %r, list_body = %r, footer = %r' % (header, selection_line, list_header, list_search, list_body, footer))
        #LOG('ListBox', 0, 'header = %r, selection_list = %r, list_header = %r, list_search = %r, footer = %r' % (header, selection_line, list_header, list_search, footer))
        list_html = header + selection_line + list_header + list_search + list_body + footer


        if render_format == 'list':
          #listboxline_list.append(current_listboxline)  
          LOG('ListBox', 0, 'listboxline_list: %s' % str(listboxline_list) )

          return listboxline_list

        #Create DomainTree Selector and DomainTree box
        if domain_tree:
          select_tree_options = ''
          for c in domain_root_list:
            if c[0] == selection_domain_path:
              select_tree_options += """<option selected value="%s">%s</option>\n""" % (c[0], c[1])
            else:
              select_tree_options += """<option value="%s">%s</option>\n""" % (c[0], c[1])
          select_tree_header = """<select name="domain_root_url"
onChange="submitAction(this.form,'%s/portal_selections/setDomainRoot')">
        %s</select>""" % (here.getUrl(),select_tree_options)

          try:
            select_tree_body = makeTreeBody(form, None, selection_domain_path,
                 0, None, selection_domain_current, form.id, selection_name )
          except KeyError:
            select_tree_body = ''

          select_tree_html = """<!-- Select Tree -->
%s
<table cellpadding="0" border="0">
%s
</table>
"""  % (select_tree_header, select_tree_body )

          return """<!-- Table Wrapping for Select Tree -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td valign="top">""" + """
%s
</td><td valign="top">
%s
<!-- End of Table Wrapping for Select Tree -->
</td></tr>
</table>""" % (select_tree_html,list_html)

        return list_html

ListBoxWidgetInstance = ListBoxWidget()

class ListBoxValidator(Validator.Validator):
    property_names = Validator.Validator.property_names

    def validate(self, field, key, REQUEST):
        form = field.aq_parent
        # We need to know where we get the getter from
        # This is coppied from ERP5 Form
        here = getattr(form, 'aq_parent', REQUEST)
        columns = field.get_value('columns')
        editable_columns = field.get_value('editable_columns')
        all_editable_columns = field.get_value('all_editable_columns')
        column_ids = map(lambda x: x[0], columns)
        editable_column_ids = map(lambda x: x[0], editable_columns)
        all_editable_column_ids = map(lambda x: x[0], all_editable_columns)
        selection_name = field.get_value('selection_name')
        #LOG('ListBoxValidator', 0, 'field = %s, selection_name = %s' % (repr(field), repr(selection_name)))
        selection = here.portal_selections.getSelectionFor(selection_name, REQUEST=REQUEST)
        params = selection.getParams()
        portal_url = getToolByName(here, 'portal_url')
        portal = portal_url.getPortalObject()

        result = {}
        error_result = {}
        listbox_uids = REQUEST.get('%s_uid' % field.id, [])
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
              alias = '_'.join(sql.split('.'))
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
                  value = my_field.validator.validate(my_field, key, REQUEST) # We need cell
                  # Here we set the property
                  listbox[uid[4:]][sql] = value
                except ValidationError, err: # XXXX import missing
                  pass
        # Here we generate again the object_list with listbox the listbox we
        # have just created
        if len(listbox)>0:
          list_method = field.get_value('list_method')
          list_method = getattr(here, list_method.method_name)
          REQUEST.set('listbox',listbox)
          object_list = list_method(REQUEST=REQUEST,**params)
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
              alias = '_'.join(sql.split('.'))
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
                  value = my_field.validator.validate(my_field, key, REQUEST) # We need cell
                  result[uid[4:]][sql] = value
                except ValidationError, err: # XXXX import missing
                  #LOG("ListBox ValidationError",0,str(err))
                  err.field_id = error_result_key
                  errors.append(err)
          else:
            # Second case: modification of existing objects
            #try:
            if 1: #try:
              # We must try this
              # because sometimes, we can be provided bad uids
              o = here.portal_catalog.getObject(uid)
              for sql in editable_column_ids:
                alias = '_'.join(sql.split('.'))
                if '.' in sql:
                  property_id = '.'.join(sql.split('.')[1:]) # Only take trailing part
                else:
                  property_id = alias
                my_field_id = '%s_%s' % (field.id, alias)
                if form.has_field( my_field_id ):
                  my_field = form.get_field(my_field_id)
                  key = 'field_' + my_field.id + '_%s' % o.uid
                  error_result_key = my_field.id + '_%s' % o.uid
                  #if hasattr(o,cname_id): WHY THIS ????
                  # XXX This is not acceptable - we do not calculate things the same way in 2 different cases
                  REQUEST.cell = o # We need cell
                  try:
                    value = my_field.validator.validate(my_field, key, REQUEST) # We need cell
                    error_result[error_result_key] = value
                    try:
                      attribute_value = o.getProperty(property_id)
                    except:
                      attribute_value = getattr(o,property_id, None)
                    if my_field.meta_type == "MultiListField":
                      test_equal = 1
                      # Sometimes, the attribute is not a list
                      # so we need to force update
                      try:
                        for v in attribute_value:
                          if v not in value:
                            test_equal = 0
                      except:
                        test_equal = 0
                      try:
                        for v in value:
                          if v not in attribute_value:
                            test_equal = 0
                      except:
                        test_equal = 0
                    else:
                      test_equal = attribute_value == value
                    if not result.has_key(o.getUrl()):
                      result[o.getUrl()] = {}  # We always provide an empty dict - this should be improved by migrating the test of equality to Bae - it is not the purpose of ListBox to do this probably. XXX
                    if not test_equal:
                      result[o.getUrl()][sql] = value
                  except ValidationError, err: # XXXX import missing
                    #LOG("ListBox ValidationError",0,str(err))
                    err.field_id = error_result_key
                    errors.append(err)
            #except:
            else:
              LOG("ListBox WARNING",0,"Object uid %s could not be validated" % uid)
        if len(errors) > 0:
            LOG("ListBox FormValidationError",0,str(error_result))
            LOG("ListBox FormValidationError",0,str(errors))
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
      if id == 'default' and kw.get('render_format') in ('list', ):
        return self.widget.render(self, self.generate_field_key() , None , kw.get('REQUEST'), render_format=kw.get('render_format'))
      else:
        return ZMIField.get_value(self, id, **kw)



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
    
  security.declarePublic('__getitem__')
  def __getitem__(self, column_id):
    return getColumnProperty(self, column_id)

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
    if content_mode == 'TitleLine':
      self.is_title_line = 1
      self.is_data_line = 0
      self.is_stat_line = 0
      self.is_summary_line = 0
    elif content_mode == 'DataLine':
      self.is_title_line = 0
      self.is_data_line = 1
      self.is_stat_line = 0
      self.is_summary_line = 0
    elif content_mode == 'StatLine':
      self.is_title_line = 0
      self.is_data_line = 0
      self.is_stat_line = 1
      self.is_summary_line = 0
    elif content_mode == 'SummaryLine':
      self.is_title_line = 0
      self.is_data_line = 0
      self.is_stat_line = 0
      self.is_summary_line = 1
    self.setConfigProperty('content_mode',content_mode)

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
    
  security.declarePublic('isStateLine')
  def isStateLine(self):
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
    self.setConfigProperty('is_checked',is_checked)

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
    self.setConfigProperty('uid',object_uid)

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
    self.setConfigProperty('section_name',section_name)

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
    self.setConfigProperty('section_depth',depth)
    
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
  
InitializeClass(ListBoxLine)
allow_class(ListBoxLine)

# Psyco
import psyco
psyco.bind(ListBoxWidget.render)
psyco.bind(ListBoxValidator.validate)


