##parameters=form_id, field_id, selection_index, selection_name, uids, object_uid, listbox_uid

# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from Products.Formulator.Errors import ValidationError, FormValidationError

request=context.REQUEST

o = context.portal_catalog.getObject(object_uid)

if o is None:
  return "Sorrry, Error, the calling object was not catalogued. Do not know how to do ?"

if listbox_uid is not None:
  selected_uids = context.portal_selections.updateSelectionCheckedUidList(selection_name,listbox_uid,uids)
  uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)

if request.has_key('previous_form_id'):
  previous_form_id = request.get('previous_form_id')
  if previous_form_id != '':
    form_id = previous_form_id

form = getattr(context, form_id)
field = form.get_field(field_id)
base_category = field.get_value('base_category')
relation_setter_id = field.get_value('relation_setter_id')
if relation_setter_id: relation_setter = getattr(o, relation_setter_id)
portal_type = map(lambda x:x[0],field.get_value('portal_type'))

if uids != []:
  if relation_setter_id:
    # Clear the relation
    relation_setter((), portal_type=portal_type)
    # Warning, portal type is at strange value because of form
    # And update it
    relation_setter(uids, portal_type=portal_type)
  else:
    # Clear the relation
    o.setValueUids(base_category, (), portal_type=portal_type)
    # Warning, portal type is at strange value because of form
    # And update it
    o.setValueUids(base_category, uids, portal_type=portal_type)
else:
  if relation_setter_id:
    # Clear the relation
    relation_setter((), portal_type=portal_type)
  else:    
    # Clear the relation
    o.setValueUids(base_category,  (), portal_type=portal_type)

if not selection_index:
  redirect_url = '%s/%s?%s' % ( o.absolute_url()
                            , form_id
                            , 'portal_status_message=Data+Updated.'
                            )
else:
  redirect_url = '%s/%s?selection_index=%s&selection_name=%s&%s' % ( o.absolute_url()
                            , form_id
                            , selection_index
                            , selection_name
                            , 'portal_status_message=Data+Updated.'
                            )


request[ 'RESPONSE' ].redirect( redirect_url )
