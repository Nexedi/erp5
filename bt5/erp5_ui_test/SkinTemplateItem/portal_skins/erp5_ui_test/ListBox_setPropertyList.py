"""
Used to set properties for Listbox
"""
from erp5.component.module.Log import log

field = context
d = dict(
  field_title = 'Foos',
  field_description = '',
  field_css_class = '',
  field_alternate_name = '',
  field_hidden = '',
  field_lines = kw.get('field_lines', '3'),
  field_columns = '\n'.join((
    'id | ID',
    'title | Title',
    'getQuantity | Quantity',
  )),
  field_all_columns = '',
  field_search_columns = '',
  field_sort_columns = '',
  field_sort = 'id', # Very important, this allow to test tales expression on listbox_XXX fields
  field_editable_columns = 'id',
  field_stat_columns = '',
  field_url_columns = '',
  field_list_method = 'searchFolder',
  field_count_method = 'countFolder',
  field_stat_method = '',
  field_row_css_method = '',
  field_selection_name = 'foo_selection',
  field_meta_types = '',
  field_portal_types = 'Foo',
  field_default_params = '',
  field_global_attributes = '',
  field_search = 'checked',
  field_select = 'checked',
  field_anchor = '',
  field_domain_tree = '',
  field_domain_root_list = '',
  field_report_tree = '',
  field_report_root_list = '',
  field_display_style_list = '',
  field_default_display_style = '',
  field_global_search_column = '',
  field_global_search_column_script = '',
  field_page_navigation_template = 'ListBox_viewSliderPageNavigationRenderer',
  field_list_action = 'list',
  field_enabled = 'checked',
  field_editable = '',
  field_page_template = '',
  field_external_validator = '',
  field_untranslatable_columns = '',
  field_hide_rows_on_no_search_criterion = '',
  field_style_columns = '',
)

d.update(context.REQUEST)
d.update(kw)

# If the listbox is a proxy field, replace it with just a listbox
# before it was always failing on "form_id was not transferred"
if field.meta_type == "ProxyField":
  form = field.aq_parent
  field_id = field.getId()
  field_title = field.getTitle()
  log("Replacing ProxyField with a Listbox for {!s}.{!s}".format(form, context))
  form.manage_delObjects(field_id)
  form.manage_addField(field_id, field_title, 'ListBox')
  field = getattr(form, 'listbox')

#context.log('ListBox_setPropertyList', 'kw = %r, d = %r' % (kw, d,))
r = field.form.validate(d)
field.manage_edit_xmlrpc(r)

return 'Set Successfully.'
