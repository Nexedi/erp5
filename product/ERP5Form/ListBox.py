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

import string
from Products.Formulator.DummyField import fields
from Products.Formulator import Widget, Validator
from Products.Formulator.Field import ZMIField
from Products.Formulator.Form import BasicForm
from Products.Formulator.Errors import FormValidationError, ValidationError
from Products.Formulator.MethodField import BoundMethod
from Selection import Selection
from DateTime import DateTime
from Products.ERP5Type.Utils import getPath
from Products.ERP5Type.Document import newTempBase
from Products.CMFCore.utils import getToolByName
from copy import copy

from Acquisition import aq_base, aq_inner, aq_parent, aq_self
from zLOG import LOG

import random
import md5

def getAsList(a):
  l = []
  for e in a:
    l.append(e)
  return l

def makeTreeBody(root, depth, total_depth, unfolded_list, form_id, selection_name):

  tree_body = ''
  unfolded_ids = []
  for t in unfolded_list:
    if len(t) > 0:
      unfolded_ids += [t[0]]

  for o in root.objectValues():
    tree_body += '<TR>' + '<TD WIDTH="16" NOWRAP>' * depth
    if o.id in unfolded_ids:
      tree_body += """<TD NOWRAP VALIGN="TOP" ALIGN="LEFT" COLSPAN="%s">
<a href="portal_selections/setDomainList?domain_list_url=%s&form_id=%s&list_selection_name=%s" >- <b>%s</b></a>
</TD>""" % (total_depth - depth + 1, o.getUrl() , form_id, selection_name, o.id)
      new_unfolded_list = []
      for t in unfolded_list:
        if len(t) > 0:
          if t[0] == o.id:
            new_unfolded_list += [t[1:]]
      tree_body += makeTreeBody(o, depth + 1, total_depth, new_unfolded_list, form_id, selection_name)
    else:
      tree_body += """<TD NOWRAP VALIGN="TOP" ALIGN="LEFT" COLSPAN="%s">
<a href="portal_selections/setDomainList?domain_list_url=%s&form_id=%s&list_selection_name=%s" >+ %s</a>
</TD>""" % (total_depth - depth + 1, o.getUrl() , form_id, selection_name, o.id)

  return tree_body

def makeTreeList(root, depth, total_depth, unfolded_list, form_id, selection_name):
  """
    (object, is pure summary, depth, is open)
  """

  tree_list = []
  unfolded_ids = []
  for t in unfolded_list:
    if len(t) > 0:
      unfolded_ids += [t[0]]

  for o in root.objectValues():
    if o.id in unfolded_ids:
      tree_list += [(o, 1, depth, 1)]
      new_unfolded_list = []
      for t in unfolded_list:
        if len(t) > 0:
          if t[0] == o.id:
            new_unfolded_list += [t[1:]]
      tree_list += [(o, 0, depth, 0)]
      tree_list += makeTreeList(o, depth + 1, total_depth, new_unfolded_list, form_id, selection_name)
    else:
      tree_list += [(o, 1, depth, 0)]

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
                      'editable_columns', 'all_editable_columns', 'global_attributes',
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

    def render(self, field, key, value, REQUEST):
        """
          This is where most things happen. This method renders a list
          of items
        """
        # First grasp the variables we may need

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
        #selection_name = REQUEST.get('selection_name',None)
        #if selection_name is None:
        #  selection_name = str(random.randrange(1,2147483600))
        current_selection_name = REQUEST.get('selection_name','default')
        list_action = here.absolute_url() + '/' + field.get_value('list_action') + '?reset=1'
        object_list = []

        #LOG('Listbox',0,'search_columns1: %s' % str(search_columns))
        if search_columns == [] or search_columns is None or search_columns == '':
          # We will set it as the schema
          search_columns = map(lambda x: [x,x],here.portal_catalog.schema())
          #LOG('Listbox',0,'search_columns2: %s' % str(search_columns))
        search_columns_id_list = map(lambda x: x[0], search_columns)

        if sort_columns == [] or sort_columns is None or sort_columns == '':
          sort_columns = search_columns
        sort_columns_id_list = map(lambda x: x[0], sort_columns)

        # We only display stats if a stat button exsists
        # XXXXXXXXXXXX This is not necessarily a good
        # idea since we may want to hardcode stats in certain cases
        filtered_actions = here.portal_actions.listFilteredActionsFor(here);
        object_ui = filtered_actions.has_key('object_ui')
        show_stat = object_ui

        has_catalog_path = None
        for (k, v) in all_columns:
          if k == 'catalog.path' or k == 'path':
            has_catalog_path = k
            break

        selection = here.portal_selections.getSelectionFor(selection_name, REQUEST=REQUEST)
        # Create selection if needed, with default sort order
        if selection is None:
          selection = Selection(params=default_params, sort_on = sort)
        # Or make sure all sort arguments are valid
        else:
          # Reset Selection is needed
          if reset is not 0 and reset is not '0':
            here.portal_selections.setSelectionToAll(selection_name)
            here.portal_selections.setSelectionSortOrder(selection_name, sort_on = sort)

          # Filter non searchable items
          sort = []
          fix_sort = 0
          for (k , v) in selection.selection_sort_on:
            if k in sort_columns_id_list:
              sort.append((k,v))
            else:
              fix_sort = 1
          if fix_sort: selection.selection_sort_on = sort

        if not hasattr(selection, 'selection_flat_list_mode'):
          selection.edit(flat_list_mode=(not (domain_tree or
           report_tree)),domain_tree_mode=domain_tree,report_tree_mode= report_tree)

        # Selection
        #LOG("Selection",0,str(selection.__dict__))

        # Display choosen by the user

        if selection.selection_flat_list_mode is not None:
          if selection.selection_flat_list_mode == 1:
            domain_tree = 0
            report_tree = 0
          elif selection.selection_domain_tree_mode == 1:
            domain_tree = 1
            report_tree = 0
          elif selection.selection_report_tree_mode == 1:
            domain_tree = 0
            report_tree = 1

        checked_uids = selection.getSelectionCheckedUids()
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
        params = selection.getSelectionParams()
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

        # Build the columns selections
        # The idea is: instead of selecting *, listbox is able to
        # provide what should be selected. This should allow to reduce
        # the quantity of data transfered between MySQL and Zope
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

        # Execute the query
        kw = params
        if hasattr(list_method, 'method_name'):
          if list_method.method_name == 'objectValues':
            list_method = here.objectValues
            kw = copy(params)
            kw['spec'] = filtered_meta_types
          elif list_method.method_name == 'portal_catalog':
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
          elif list_method in (None, ''): # Use current selection
            # Use previously used list method
            list_method = None
          else:
            # Include portal_type selection
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

            # Try to get the method through acquisition
            try:
              list_method = getattr(here, list_method.method_name)
            except:
              pass

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

        # Build the stat query part which is common to each query of this script
        if show_stat:
          stats = here.portal_selections.getSelectionStats(selection_name, REQUEST=REQUEST)
          stat_query = ''
          index = 0

          for (k,v) in columns:
            try:
              if stats[index] != ' ':
                stat_query += stats[index] + '(' + k + ') AS ' + k + ','
              else:
                stat_query += '\'&nbsp;\' AS ' + k + ','
            except:
              stat_query += '\'&nbsp;\' AS ' + k + ','
            index = index + 1

          stat_query = stat_query[:len(stat_query) - 1]
          kw['stat_query'] = stat_query
          selection.edit( params = kw )

        if domain_tree:
          selection_domain_path = selection.getSelectionDomainPath()
          selection_domain_current = selection.getSelectionDomainList()
          if len(selection_domain_current) > 0:
            try:
              kw['query'] = here.unrestrictedTraverse(selection_domain_path).unrestrictedTraverse(
                                        selection_domain_current[0]).asSqlExpression()
            except:
              "The selection does not exist"
              pass


        # When we build the body, we have to go through
        # All report lines
        # This is made as a list of tuples
        # (section_id, object_list, object_list_size, is_summary)
        report_query = ''
        if report_tree:
          original_query = kw.get('query')
          selection_report_path = selection.getSelectionReportPath()
          selection_report_current = selection.getSelectionReportList()
          report_tree_list = makeTreeList(here.unrestrictedTraverse(selection_report_path),
                 0, max(map(lambda x: len(x), selection_report_current)),
                 selection_report_current, form.id, selection_name )
          report_sections = []
          #LOG("Report Tree",0,str(report_tree_list))
          for s in report_tree_list:
            if s[1]:
              # Prepare query
              if domain_tree:
                # This will not work at present XXX
                # Because we can combine AND queries on the same table
                kw['query'] = '(%s AND %s)' % (original_query,
                      s[0].asSqlExpression(strict_membership=0))
              else:
                kw['query'] = s[0].asSqlExpression(strict_membership=0)
              selection.edit( params = kw )
              #LOG('ListBox 569', 0, str((selection_name, selection.__dict__)))
              stat_temp = selection(selection_method = stat_method,
                        context=here, REQUEST=REQUEST)



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
              stat_context.domain_url = s[0].getUrl()
              report_sections += [(s[0].id, 1, s[2], [stat_context], 1, s[3])]
            else:
              # Prepare query
              if domain_tree:
                # This will not work at present XXX
                # Because we can combine AND queries on the same table
                kw['query'] = '(%s AND %s)' % (original_query,
                      s[0].asSqlExpression(strict_membership=1))
              else:
                kw['query'] = s[0].asSqlExpression(strict_membership=1)
              report_query += kw['query']
              selection.edit( params = kw )
              if list_method not in (None, ''):
                object_list = selection(selection_method = list_method, context=here, REQUEST=REQUEST)
              else:
                # If list_method is None, use already selected values.
                object_list = here.portal_selections.getSelectionValueList(selection_name, context=here, REQUEST=REQUEST)
              # PERFORMANCE
              report_sections += [ (None, 0, s[2], object_list, len(object_list), s[3]) ]
          if original_query is not None:
            kw['query'] = original_query
          else:
            del kw['query']

        else:
          selection.edit( params = kw )
          #LOG('ListBox 612', 0, str((selection_name, selection.__dict__)))
          if list_method not in (None, ''):
            object_list = selection(selection_method = list_method, context=here, REQUEST=REQUEST)
          else:
            # If list_method is None, use already selected values.
            object_list = here.portal_selections.getSelectionValueList(selection_name, context=here, REQUEST=REQUEST)
          # PERFORMANCE
          report_sections = ( (None, 0, 0, object_list, len(object_list), 0),  )

        object_uid_list = map(lambda x: getattr(x, 'uid', None), object_list)
        LOG('ListBox.render, object_uid_list:',0,object_uid_list)
        # Then construct the md5 corresponding this uid list
        # It is used in order to do some checks in scripts.
        # For example, if we do delete objects, then we do have a list of
        # objects to delete, but it is possible that on another tab the selection
        # change, and then when we confirm the deletion, we don't delete what
        # we want, so this is really dangerous. with this md5 we can check if the
        # selection is the same
        sorted_object_uid_list = copy(object_uid_list)
        sorted_object_uid_list.sort()
        md5_string = md5.new(str(sorted_object_uid_list)).hexdigest()
        #md5_string = md5.new(str(object_uid_list)).digest()


        #LOG("Selection", 0, str(selection.__dict__))

        # Build the real list by slicing it
        # PERFORMANCE ANALYSIS: the result of the query should be
        # if possible a lazy sequence

        total_size = 0
        for s in report_sections:
          total_size += s[4]
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

        # Store the resulting selection if list_method is not None
        if list_method is not None:
          try:
            method_path = getPath(here) + '/' + list_method.method_name
            LOG('ListBox', 0, 'method_path = %s, getPath = %s, list_method.method_name = %s' % (repr(method_path), repr(getPath(here)), repr(list_method.method_name)))
          except:
            method_path = getPath(here) + '/' + list_method.__name__
            LOG('ListBox', 0, 'method_path = %s, getPath = %s, list_method.__name__ = %s' % (repr(method_path), repr(getPath(here)), repr(list_method.__name__)))
          # Sometimes the seltion name is a list ??? Why ????
          if type(current_selection_name) in (type(()),type([])):
            current_selection_name = current_selection_name[0]
          list_url =  url+'?selection_name='+current_selection_name+'&selection_index='+str(selection_index)
          selection.edit( method_path= method_path, params = kw, list_url = list_url)
          #LOG("Selection kw", 0, str(selection.selection_params))
          here.portal_selections.setSelectionFor(selection_name, selection, REQUEST=REQUEST)

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
    <select name="list_start" title="Change Page" size="1"
      onChange="submitAction(this.form,'%s/portal_selections/setPage')">
""" % REQUEST.URL1
        else:
          pages = """\
   <td nowrap valign="middle" align="center">
    <input type="image" src="%s/images/1leftarrowv.png"
      Title="Previous Page" name="portal_selections/previousPage:method" border="0" />
   </td>
   <td nowrap valign="middle" align="center">
    <select name="list_start" title="Change Page" size="1"
      onChange="submitAction(this.form,'%s/portal_selections/setPage')">
""" % (portal_url_string,REQUEST.URL1)
        for p in range(0, total_pages):
          if p == current_page:
            pages += """<option selected value="%s">%s of %s</option>\n""" \
                    % (p * lines, p+1, total_pages)
          else:
            pages += """<option value="%s">%s of %s</option>\n""" \
                    % (p * lines, p+1, total_pages)

        if current_page == total_pages - 1:
          pages = pages + """\
    </select>
   </td>
   <td nowrap valign="middle" align="center">
   </td>
"""
        else:
          pages = pages + """\
    </select>
   </td>
   <td nowrap valign="middle" align="center">
    <input type="image" src="%s/images/1rightarrowv.png"
      Title="Next Page" name="portal_selections/nextPage:method" border="0" />
   </td>
""" % portal_url_string
        # Create the header of the table - this should probably become DTML
        # Create also View Selector which enables to switch from a view mode
        # to another directly from the listbox
        header = """\
<!-- List Summary -->
<div class="ListSummary">
 <table border="0" cellpadding="0" cellspacing="0">
  <tr height="10">
   <td height="10"><img src="%s/images/Left.png" border="0"></td>
   <td class="Top" colspan="2" height="10">
    <img src="%s/images/spacer.png" width="5" height="10" border="0"
      alt="spacer"/></td>
   <td class="Top" colspan="3" height="10">
    <img src="%s/images/spacer.png" width="5" height="10" border="0"
      alt="spacer"/>
   </td>
  </tr>
  <tr>
   <td class="Left" width="17">
    <img src="%s/images/spacer.png" width="5" height="5" border="0"
        alt="spacer"/>
   </td>
   <td valign="middle" nowrap>

    <input type="image" src="%s/images/text_block.png" id="flat_list"
       title="Flat List" name="portal_selections/setFlatListMode:method" value="1" border="0" alt="img"/">
    <input type="image" src="%s/images/view_tree.png" id="flat_list"
       title="Report Tree" name="portal_selections/setReportTreeMode:method" value="1" border="0" alt="img"/">
        <input type="image" src="%s/images/view_choose.png" id="flat_list"
       title="Domain Tree" name="portal_selections/setDomainTreeMode:method" value="1" border="0" alt="img"/"></td>
   <td width="100%%" valign="middle">&nbsp; <a href="%s">%s</a>:
        %s %s - %s %s
   </td>
   %s
  </tr>
 </table>
</div>
<!-- List Content -->
<div class="ListContent">
 <table cellpadding="0" cellspacing="0" border="0">
""" % ((portal_url_string,) * 7 + ( list_action, field_title , total_size, 'Records',  len(checked_uids), 'item(s) selected', pages))

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
          list_header = """\
<tr >%s
   <td class="Data" width="50" align="center" valign="middle">
    <input type="image" name="portal_selections/checkAll:method" value="1"
      src="%s/images/checkall.png" border="0" alt="Check All" />
    <input type="image" name="portal_selections/uncheckAll:method" value="1"
      src="%s/images/decheckall.png" border="0" alt="Uncheck All" />
""" % (report_popup,portal_url_string,portal_url_string)
        else:
          list_header = """\
<tr >%s
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
          if cname[0] in search_columns_id_list:
            list_header = list_header + ("<td class=\"Data\"><a href=\"%sportal_selections/setSelectionQuickSortOrder?selection_name=%s&sort_on=%s\">%s</a> %s</td>\n" %
                (here.absolute_url() + '/' ,str(selection_name),str(cname[0]),str(cname[1]),img))
          else:
            list_header = list_header + ("<td class=\"Data\">%s</td>\n" % str(cname[1]))
        list_header = list_header + "</tr>"

        # Create the search row of the table with the name of the columns
        if search:
          # Add empty column for report
          if report_tree:
            report_search = """<td class="Data" width="50" align="left" valign="middle">&nbsp;<a href="">1</a>&nbsp;<a href="">2</a>&nbsp;<a href=""><u>3</u></a>&nbsp;</td>"""
          else:
            report_search = ""

          if select:
            list_search ="""\
  <tr >
   %s
   <td class="Data" width="50" align="center" valign="middle">
     <input type="image" src="%s/images/exec16.png" title="Action" alt="Action" name="doSelect:method" />
   </td>
""" % (report_search,portal_url_string)
          else:
            list_search ="""\
  <tr >
  %s
""" % report_search

          for cname in extended_columns:
            if cname[0] in search_columns_id_list:
              list_search = list_search + (
                "<td class=\"DataB\"><font size=\"-3\"> \
                  <input name=\"%s\" size= \"8\" value=\"%s\" > \
                  </font></td>\n" % \
                     (str(cname[2]) , params.get(str(cname[2]),'')))
            else:
              list_search = list_search + (
                "<td class=\"DataB\"></td> ")

          list_search = list_search + "</tr>"
        else:
          list_search = ''

        # Build Lines
        list_body = ''
        section_index = 0
        current_section_base_index = 0
        current_section = report_sections[section_index]
        current_section_size = current_section[4]
        object_list = current_section[3]
        for i in range(start,end):
          # Make sure we go to the right section
          while current_section_base_index + current_section_size <= i:
            current_section_base_index += current_section[4]
            section_index += 1
            current_section = report_sections[section_index]
            current_section_size = current_section[4]
            object_list = current_section[3]

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
            if current_section[1]:
              section_name = current_section[0]
            else:
              section_name = ''
            if current_section[5]:
              if section_name != '':
                section_char = '-'
              list_body = list_body + \
"""<td class="%s" align="left" valign="middle"><a href="portal_selections/foldReport?report_url=%s&form_id=%s&list_selection_name=%s">%s%s%s</a></td>
""" % (td_css, getattr(current_section[3][0],'domain_url',''), form.id, selection_name, '&nbsp;&nbsp;' * current_section[2], section_char, section_name)
            else:
              if section_name != '':
                section_char = '+'
              list_body = list_body + \
"""<td class="%s" align="left" valign="middle"><a href="portal_selections/unfoldReport?report_url=%s&form_id=%s&list_selection_name=%s">%s%s%s</a></td>
""" % (td_css, getattr(current_section[3][0],'domain_url',''), form.id, selection_name, '&nbsp;&nbsp;' * current_section[2], section_char, section_name)

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
          for cname in extended_columns:
            sql = cname[0] # (sql, title, alias)
            alias = cname[2] # (sql, title, alias)
            if '.' in sql:
              property_id = '.'.join(sql.split('.')[1:]) # Only take trailing part
            else:
              property_id = alias
#            attribute_value = getattr(o, cname_id) # FUTURE WAY OF DOING TGW Brains
            my_field = None
            tales_expr = None
            if form.has_field('%s_%s' % (field.id, alias) ):
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
            else:
              if hasattr(aq_self(o),alias): # Block acquisition to reduce risks
                # First take the indexed value
                attribute_value = getattr(o,alias) # We may need acquisition in case of method call
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
                      #LOG('Look up attribute %s' % cname_id,0,str(attribute_value))
                      if not callable(attribute_value):
                        #LOG('Look up accessor %s' % cname_id,0,'')
                        attribute_value = real_o.getProperty(property_id)
                        #LOG('Look up accessor %s' % cname_id,0,str(attribute_value))
                    except:
                      attribute_value = getattr(real_o,property_id)
                      #LOG('Fallback to attribute %s' % cname_id,0,str(attribute_value))
                  except:
                    attribute_value = 'Can not evaluate attribute: %s' % sql
                else:
                  attribute_value = 'Object does not exist'
            if callable(attribute_value):
              try:
                attribute_value = attribute_value()
              except:
                attribute_value = "Could not evaluate"
            if type(attribute_value) is type(0.0):
              if sql in editable_column_ids and form.has_field('%s_%s' % (field.id, alias) ):
                # Do not truncate if editable
                pass
              else:
                attribute_value = "%.2f" % attribute_value
              td_align = "right"
            elif type(attribute_value) is type(1):
              td_align = "right"
            else:
              td_align = "left"
            if sql in editable_column_ids and form.has_field('%s_%s' % (field.id, alias) ):
              key = my_field.id + '_%s' % o.uid
              if field_errors.has_key(key):
                error_css = 'Error'
                error_message = "<br/>%s" % field_errors[key].error_text  # XXX localization needed
                # Display previous value (in case of error
                error_list.append(field_errors.get(key))
                display_value = REQUEST.get('field_%s' % key, attribute_value)
              else:
                error_css = ''
                error_message = ''
                #display_value = REQUEST.get('field_%s' % key, attribute_value)
                display_value = attribute_value # XXX Make sure this is ok
              cell_body = my_field.render(value = display_value, REQUEST = o, key = key)
                                                            # We use REQUEST which is not so good here
                                                            # This prevents from using standard display process
              list_body = list_body + \
                  ('<td class=\"%s%s\">%s%s</td>' % (td_css, error_css, cell_body, error_message))
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

          list_body = list_body + '</tr>'


        # Call the stat_method
        if show_stat:
          count_results = selection(selection_method = stat_method,
                          context=here, REQUEST=REQUEST)
          list_body = list_body + '<tr>'
          if report_tree:
            list_body += '<td class="Data">&nbsp;</td>'
          if select:
            list_body += '<td class="Data">&nbsp;</td>'
          for n in range((len(extended_columns))):
            try:
              alias = extended_columns[n][2]
              value = getattr(count_results[0],alias,'')
              if callable(value): value=value()
              if type(value) is type(1.0):
                list_body += '<td class="Data" align="right">%.2f</td>' % value
              else:
                list_body += '<td class="Data">' + str(value) + '</td>'
            except:
              list_body += '<td class="Data">&nbsp;</td>'
          list_body += '</tr>'

        list_html = header + selection_line + list_header + list_search + list_body + footer

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
            select_tree_body = makeTreeBody(here.unrestrictedTraverse(selection_domain_path),
                 0, max(map(lambda x: len(x), selection_domain_current)), selection_domain_current, form.id, selection_name )
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
        selection = here.portal_selections.getSelectionFor(selection_name, REQUEST=REQUEST)
        params = selection.getSelectionParams()
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


# Psyco
import psyco
psyco.bind(ListBoxWidget.render)
psyco.bind(ListBoxValidator.validate)


