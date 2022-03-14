"""(Re)Sets properties of chosen Fields in Foo_viewDummyMultiListFieldDialog.

Use this in your tests to alter for example Float Field configuration
instead of copy&pasting new form and changing such property manualy.

Usage: input parameters are supposed to have key <field-name>__<property_name> (please
note double underscore being separator). Those field/property combination will get
propagated into the view IF we already have default value for it.

To modify TALES expression, add "_tales" in the property name as shown in the example below.

Example: in your test, call ${base_url}/FooViewDummyMultiListFieldDialog_setFieldPropertyList?your_dummy__items=first%7CFirst%20second%7CSecond&your_dummy__default_tales=python%3A%20%5B%5D
"""
portal = context.getPortalObject()
form = portal.Foo_viewDummyMultiListFieldDialog
request = context.REQUEST

if not property_dict:
  # script called via URL receives its parameters in REQUEST.form
  property_dict.update(request.form)

field_default = {
  'description': '',
  'css_class': '',
  'alternate_name': '',
  'enabled': 'checked',
  'editable': 'checked',
  'required': '',
  'unicode': '',
  'hidden': '',
  'external_validator': '',
}

default = {
  'your_dummy': dict(
    title='Your Dummy',
    default="",
    items="""A | a
B | b""",
    view_separator='<br />',
    size='5',
    extra='',
    extra_item='',
    **field_default
  )
}

# Copy structure of fields but set all TALES expressions to empty
"""
tales_default = {field_name: {} for field_name in default}
"""
tales_default = {}
for field_name in default:
  tales_default[field_name] = {prop_name: '' for prop_name in default[field_name]}


# update defaults with user defined values
for composed_key, value in list(property_dict.items()):
  field_dict = default
  field_name, property_name = composed_key.split('__')
  if property_name.endswith('_tales'):
    property_name = property_name[:-len('_tales')]
    field_dict = tales_default
  # to allow overriding only default values
  # throw an exception in case of non-existence of the field/property
  assert property_name in default[field_name], 'Uknown field {} and property {} for {!s}'.format(field_name, property_name, field_dict)
  field_dict[field_name][property_name] = value

# update actual fields
for field_name in default:
  field = form.get_field(field_name)
  field.manage_edit(
    {'field_' + key: value
     for key, value in list(default[field_name].items())}
  )

# update actual fields TALES expressions
for field_name in tales_default:
  field = form.get_field(field_name)
  field.manage_tales(  # this function actually eats ValidationError exceptions
    {'field_' + key: value
     for key, value in list(tales_default[field_name].items())}
  )

return 'Set Successfully.'
