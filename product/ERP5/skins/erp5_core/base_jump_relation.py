##parameters=form_id, field_id, selection_index=0, selection_name=''

# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from Products.Formulator.Errors import ValidationError, FormValidationError

request=context.REQUEST

#return request

form = getattr(context,form_id)
field = form.get_field(field_id)
base_category = field.get_value('base_category')
portal_type = map(lambda x:x[0],field.get_value('portal_type'))
jump_reference = context.getDefaultValue(base_category, portal_type=portal_type)

return request[ 'RESPONSE' ].redirect( '%s/view' % jump_reference.absolute_url() )

