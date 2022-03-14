"""(Re)Sets properties of chosen Fields in Foo_view.

Use this in your tests to alter for example Float Field configuration
instead of copy&pasting new form and changing such property manualy.

Usage: input parameters are supposed to have key <field-name>__<property_name> (please
note double underscore being separator). Those field/property combination will get
propagated into the view IF we already have default value for it.

Example: in your test, call ${base_url}/FooView_setFieldsProperties?my_quantity__precision=2&amp;listbox_quantity__precision=checked
"""
portal = context.getPortalObject()
form = portal.Foo_view
request = context.REQUEST

if not property_dict:
  # script called via URL receives its parameters in REQUEST.form
  property_dict.update(request.form)

field_default = {
  'default': '',
  'description': '',
  'css_class': '',
  'alternate_name': '',
  'display_width': '20',
  'display_maxwidth': '',
  'extra': '',
  'external_validator': '',
  'enabled': 'checked',
  'editable': 'checked',
  'required': '',
  'hidden': '',
  'whitespace_preserve': '',
}

default = {
  # feel free to add more fields from the comment bellow or on your own
  'my_lines_list': dict(
    title='Lines',
    view_separator='<br />',
    width='40',
    height='5',
    str='',
    max_linelength='',
    max_lines='',
    max_length='',
    **field_default
  )
}

# For now - control fields only which are needed
# If anyone wishes to control more feel free to move
# the desired field from the comment bellow to the dict above
'''
  'my_quantity': dict(
    title='Quantity',
    input_type='text',
    input_style='-1 234.5',
    precision='1',
    **field_default
  ),
  'listbox': dict(
    title='Foo Lines',
    lines=3,
    columns="""id | ID
title | Title
quantity | Quantity
start_date | Date
catalog.uid | Uid""",
    searchable_columns="""id | ID
title | Title
quantity | Quantity
start_date | Date""",
    sort="id | id",
    list_method="objectValues",
    count_method="countFolder",
    stat_method="portal_catalog",
    selection_name="foo_selection",
    portal_types="Foo Line | Foo Line",
    search="checked",
    select="checked",
    editable_columns="""id | ID
title | Title
quantity | quantity
start_date | Date""",
    stat_columns="quantity | Foo_statQuantity",
    page_navigation_template="ListBox_viewSliderPageNavigationRenderer",
    list_action="list",
    **field_default
  ),
  'listbox_quantity': dict(
    title='Quantity',
    input_type='text',
    input_style='-1 234.5',
    precision='',
    **field_default
  ),
}
'''

# update defaults with user defined values
for composed_key, value in list(property_dict.items()):
  field_name, property_name = composed_key.split('__')
  # to allow overriding only default values
  # throw an exception in case of non-existence of the field/property
  assert default[field_name][property_name], 'Uknown field {} and property {}'.format(field_name, property_name)
  default[field_name][property_name] = value

# update actual fields
for field_name in default:
  field = form.get_field(field_name)
  field.manage_edit_xmlrpc(
    field.form.validate(
      {'field_' + key: value
       for key, value in list(default[field_name].items())}
    )
  )

return 'Set Successfully.'
