############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
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

from Products.ERP5Type.Globals import get_request
from Products.Formulator.TALESField import TALESMethod
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type.Message import translateString
from Products.ERP5Form.Form import ERP5Form
from Products.ERP5Form.ListBox import ListBoxListRenderer


def getSearchDialog(self, REQUEST=None):
  """Generate a dynamic search dialog from a listbox.
  """
  request = get_request()
  portal = self.getPortalObject()
  category_tool = getToolByName(portal, 'portal_categories')
  types_tool = getToolByName(portal, 'portal_types')
  workflow_tool = getToolByName(portal, 'portal_workflow')

  default_view = self.getTypeInfo().getDefaultViewFor(self)
  listbox = default_view.listbox

  temp_form = ERP5Form('Folder_viewSearchDialog', 'Search').__of__(portal).__of__(self)
  temp_form.pt = 'form_dialog'
  temp_form.action = 'Folder_search'

  selection_name = listbox.get_value('selection_name')
  request.set('selection_name', selection_name)
  request.set('form_id', default_view.getId())


  def addListField(field_id, field_title):
    # this one is for categories
    request_key = field_id
    field_id = 'your_%s_relative_url' % field_id
    if field_id not in temp_form.objectIds():
      temp_form.manage_addField(field_id, field_title, 'ProxyField')
    field = temp_form._getOb(field_id)
    field.manage_edit_xmlrpc(dict(
        form_id='Base_viewDialogFieldLibrary',
        field_id='your_category_list'))
    field._surcharged_edit(dict(title=field_title), ['title'])
    field._surcharged_tales(
        dict(
            default=TALESMethod(
              'here/portal_selections/%s/dialog_%s_relative_url | '
              'here/portal_selections/%s/dialog_strict_%s_relative_url | nothing'
                                    % (selection_name, request_key,
                                       selection_name, request_key)),
            items=TALESMethod('python: getattr(here.portal_categories["%s"],'
                             'here.portal_preferences.getPreference("'
                             'preferred_category_child_item_list_method_id",'
                             '"getCategoryChildCompactLogicalPathItemList"))('
                             'checked_permission="View", base=1,'
                             'display_none_category=False,'
                             'local_sort_id="int_index")' % request_key)),
            ['title', 'items', 'default'])

    field_id = 'your_%s_relative_url_is_strict_' % request_key
    if field_id not in temp_form.objectIds():
      temp_form.manage_addField(field_id, field_title, 'ProxyField')
    field = temp_form._getOb(field_id)
    field.manage_edit_xmlrpc(dict(
        form_id='Base_viewFieldLibrary',
        field_id='your_checkbox'))
    field._surcharged_edit(dict(title='%s Strict' % field_title), ['title'])
    field._surcharged_tales(
        dict(
            default=TALESMethod(
              'here/portal_selections/%s/dialog_strict_%s_relative_url | nothing'
                                    % (selection_name, request_key,))),
        ['title', 'default'])

    field_id = 'your_%s_relative_url_is_excluded_' % request_key
    if field_id not in temp_form.objectIds():
      temp_form.manage_addField(field_id, field_title, 'ProxyField')
    field = temp_form._getOb(field_id)
    field.manage_edit_xmlrpc(dict(
        form_id='Base_viewFieldLibrary',
        field_id='your_checkbox'))
    field._surcharged_edit(dict(title='%s Excluded' % field_title), ['title'])
    from zLOG import LOG
    LOG("selection_name %r, request_key %r" %(selection_name, request_key), 300, field_id)
    field._surcharged_tales(
        dict(
            default=TALESMethod(
              'here/portal_selections/%s/dialog_excluded_%s_relative_url | nothing'
                                    % (selection_name, request_key,))),
        ['title', 'default'])



  def addFloatField(field_id, field_title):
    request_key = field_id
    field_id = 'your_%s' % field_id
    if field_id not in temp_form.objectIds():
      temp_form.manage_addField(field_id, field_title, 'ProxyField')
    field = temp_form._getOb(field_id)
    field.manage_edit_xmlrpc(dict(
        form_id='Base_viewDialogFieldLibrary',
        field_id='your_money_quantity'))
    field._surcharged_edit(dict(title=field_title), ['title'])
    field._surcharged_tales(
        dict(default=TALESMethod(
            'here/portal_selections/%s/%s_value_ | nothing'
                % (selection_name, request_key))), ['title', 'default'])
    field_id = 'your_%s_usage_' % request_key
    if field_id not in temp_form.objectIds():
      temp_form.manage_addField(field_id, field_title, 'ProxyField')
    field = temp_form._getOb(field_id)
    field.manage_edit_xmlrpc(dict(
        form_id='Base_viewDialogFieldLibrary',
        field_id='your_category'))
    field._surcharged_edit(dict(
      title=translateString('${key} ${usage}',
                            mapping=dict(key=translateString(column_title),
                                         usage=translateString('Usage'))),
      items=[(translateString('Equal to'), ''),
             (translateString('Greater than'), '>'),
             (translateString('Less than'), '<'),
             (translateString('Greater than or Equal to'), '>='),
             (translateString('Less than or Equal to'), '<='),
             ]),

                           ['title', 'items'])
    field._surcharged_tales(
        dict(
            default=TALESMethod(
              'here/portal_selections/%s/%s_usage_ | nothing'
                  % (selection_name, request_key))),
            ['title', 'items', 'default'])

  def addDateTimeField(field_id, field_title):
    request_key = field_id
    field_id = 'your_%s' % field_id
    if field_id not in temp_form.objectIds():
      temp_form.manage_addField(field_id, field_title, 'ProxyField')
    field = temp_form._getOb(field_id)
    field.manage_edit_xmlrpc(dict(
        form_id='Base_viewDialogFieldLibrary',
        field_id='your_date'))
    field._surcharged_edit(dict(title=field_title), ['title'])
    field._surcharged_tales(
        dict(default=TALESMethod(
            'here/portal_selections/%s/%s_value_ | nothing'
                % (selection_name, request_key))), ['title', 'default'])
    field_id = 'your_%s_usage_' % request_key
    if field_id not in temp_form.objectIds():
      temp_form.manage_addField(field_id, field_title, 'ProxyField')
    field = temp_form._getOb(field_id)
    field.manage_edit_xmlrpc(dict(
        form_id='Base_viewDialogFieldLibrary',
        field_id='your_category'))
    field._surcharged_edit(dict(title=translateString('${key} ${usage}', mapping=dict(key=translateString(column_title), usage=translateString('Usage'))),
                                items=[(translateString('Equal to'), ''),
                                       (translateString('Greater than'), '>'),
                                       (translateString('Less than'), '<'),
                                       (translateString('Greater than or Equal to'), '>='),
                                       (translateString('Less than or Equal to'), '<='),
                                       ]),

                           ['title', 'items'])
    field._surcharged_tales(
        dict(
            default=TALESMethod(
              'here/portal_selections/%s/%s_usage_ | nothing'
                  % (selection_name, request_key))),
            ['title', 'items', 'default'])


  def addStringField(field_id, field_title):
    request_key = field_id
    field_id = 'your_%s' % field_id
    if field_id not in temp_form.objectIds():
      temp_form.manage_addField(field_id, field_title, 'ProxyField')
    field = temp_form._getOb(field_id)
    field.manage_edit_xmlrpc(dict(
        form_id='Base_viewDialogFieldLibrary',
        field_id='your_title'))
    field._surcharged_edit(dict(title=field_title,
                                description=''), ['title', 'description'])
    field._surcharged_tales(
        dict(default=TALESMethod(
          'here/portal_selections/%s/%s/query |'
          'here/portal_selections/%s/%s | string:'
       % (selection_name, request_key, selection_name, request_key))),
        ['title', 'description', 'default'])


  def addFullTextStringField(field_id, field_title):
    addStringField(field_id, field_title)

  def addKeywordSearchStringField(column_id, column_title,
                                  default_search_key='ExactMatch'):
    addStringField(column_id, column_title)
    request_key = column_id
    field_id = 'your_%s_search_key' % column_id
    if field_id not in temp_form.objectIds():
      temp_form.manage_addField(field_id, column_title, 'ProxyField')
    field = temp_form._getOb(field_id)
    field.manage_edit_xmlrpc(dict(
        form_id='Base_viewDialogFieldLibrary',
        field_id='your_category'))
    field._surcharged_edit(dict(title=translateString('${key} ${usage}', mapping=dict(key=translateString(column_title), usage=translateString('Search Key'))),
                                description='',
                                items=[(translateString('Default (${search_key})',
                                            mapping=dict(search_key=
                                               translateString(default_search_key))), ''),
                                       (translateString('Exact Match'), 'ExactMatch' ),
                                       (translateString('Keyword'), 'Keyword'),
                                       ]),

                           ['title', 'items'])
    field._surcharged_tales(
        dict(
            default=TALESMethod(
              'here/portal_selections/%s/%s_search_key | nothing'
                      % (selection_name, request_key))),
            ['title', 'items', 'default'])


  base_category_list = set(category_tool.getBaseCategoryList())
  catalog_schema = portal.portal_catalog.schema()
  sql_catalog = portal.portal_catalog.getSQLCatalog()
  sql_catalog_keyword_search_keys = sql_catalog.sql_catalog_keyword_search_keys
  sql_catalog_full_text_search_keys =\
              sql_catalog.sql_catalog_full_text_search_keys

  column_list = ListBoxListRenderer(
                      listbox.widget, listbox, request).getAllColumnList()

  added_column_set = set()

  for column_id, column_title in column_list:
    if column_id in added_column_set:
      continue
    added_column_set.add(column_id)
    short_column_id = column_id
    # strip the usual default_ and _title that are on standard fields.
    if short_column_id.endswith('_translated_title'):
      short_column_id = short_column_id[:-len('_translated_title')]
    if short_column_id.endswith('_title'):
      short_column_id = short_column_id[:-len('_title')]
    if short_column_id.endswith('_reference') and short_column_id not in (
        'source_reference', 'destination_reference'):
      short_column_id = short_column_id[:-len('_reference')]
    if short_column_id.startswith('default_'):
      short_column_id = short_column_id[len('default_'):]
    # is it a base category ?
    if short_column_id in base_category_list:
      # is this base category empty ? then it might be used to relate documents,
      # in that case, simply provide a text input
      if not len(category_tool[short_column_id]):
        default_search_key = 'ExactMatch'
        if column_id in sql_catalog_keyword_search_keys:
          default_search_key = 'Keyword'
        addKeywordSearchStringField(column_id, column_title,
                                    default_search_key=default_search_key)
        continue
      else:
        addListField(short_column_id, column_title)
        continue


    if column_id in catalog_schema:
      if column_id.endswith('state') or column_id.endswith('state_title'):
        # this is a workflow state, it will be handled later
        continue
      elif 'date' in column_id:
        # is it date ? -> provide exact + range
        # TODO: do we need an API in catalog for this ?
        addDateTimeField(column_id, column_title)

      elif 'quantity' in column_id or 'price' in column_id:
        # is it float ? -> provide exact + range
        # TODO: do we need an API in catalog for this ?
        addFloatField(column_id, column_title)
      else:
        if column_id in sql_catalog_full_text_search_keys:
          addFullTextStringField(column_id, column_title)
        else:
          default_search_key = 'ExactMatch'
          if column_id in sql_catalog_keyword_search_keys:
            default_search_key = 'Keyword'
          addKeywordSearchStringField(column_id, column_title,
                          default_search_key=default_search_key)

  allowed_content_types = self.getTypeInfo().getTypeAllowedContentTypeList()
  # remember which workflow we already displayed
  workflow_set = set()
  # possible workflow states
  for type_name in allowed_content_types:
    for workflow_id in workflow_tool.getChainFor(type_name):
      workflow = workflow_tool.getWorkflowById(workflow_id)
      state_var = workflow.variables.getStateVar()

      if state_var in workflow_set:
        continue

      workflow_set.add(state_var)
      if workflow.states is None or \
                len(workflow.states.objectIds()) <= 1:
        continue

      field_id = 'your_%s' % state_var
      if field_id not in temp_form.objectIds():
        temp_form.manage_addField(field_id, field_id, 'ProxyField')
      field = temp_form._getOb(field_id)
      field.manage_edit_xmlrpc(dict(
          form_id='Base_viewDialogFieldLibrary',
          field_id='your_category_list'))
      items = sorted([(translateString(x.title), x.id) for x
                         in workflow.states.objectValues()],
                         key=lambda x:str(x[0]))
      field._surcharged_edit(
              dict(title=translateString(workflow.title),
                   items=items,
                   size=len(items)),
              ['title', 'items', 'size'])
      field._surcharged_tales(
          dict(
              default=TALESMethod(
                'here/portal_selections/%s/%s | python:[]'
                        % (selection_name, state_var))),
              ['title', 'items', 'size', 'default'])


  # if more than 1 allowed content types -> list possible content types
  if len(allowed_content_types) > 1:
    field_id = 'your_portal_type'
    if field_id not in temp_form.objectIds():
      temp_form.manage_addField(field_id, field_id, 'ProxyField')
    field = temp_form._getOb(field_id)
    field.manage_edit_xmlrpc(dict(
        form_id='Base_viewDialogFieldLibrary',
        field_id='your_category_list'))
    field._surcharged_edit(
            dict(title=translateString('Type'),
                 items=[(translateString(x), x) for x in allowed_content_types]),

            ['title', 'items'])
    field._surcharged_tales(
        dict(
            default=TALESMethod(
              'here/portal_selections/%s/portal_type | nothing'
                                    % selection_name)),
            ['title', 'items', 'default'])


  addFullTextStringField('SearchableText', 'Full Text Search')

  # Order fields
  default_group = temp_form.group_list[0]
  field_list = temp_form.get_fields()
  for field in field_list:
    field_id = field.getId()
    if field_id.endswith('search_key') or field_id.endswith('_usage_'):
      temp_form.move_field_group([field_id], default_group, 'right')
    elif field.get_value('field_id') in ('your_category_list',
                                         'your_checkbox') \
        or field_id == 'your_SearchableText':
      temp_form.move_field_group([field_id], default_group, 'center')

  if REQUEST is not None:
    # if called from the web, render the form, other wise return it (for
    # Base_callDialogMethod)
    return temp_form(REQUEST)
  return temp_form

