##parameters=form_id, selection_index, selection_name, object_uid

# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from Products.Formulator.Errors import ValidationError, FormValidationError



request=context.REQUEST

# We stop doing this
#base_category = context.getBaseCategoryId()
base_category = None

o = context.portal_catalog.getObject(object_uid)

if o is None:
  return "Sorrry, Error, the calling object was not catalogued. Do not know how to do ?"

def checkSameKeys(a , b):
  """
    Checks if the two lists contain
    the same values
  """
  same = 1
  for ka in a:
    if not ka in b:
      same = 0
  for kb in b:
    if not kb in a:
      same = 0
  return same

def getOrderedUids(uids, values, catalog_index):
  value_to_uid = {}
  for uid in uids:
    key = context.portal_catalog.getMetadataForUid(uid)[catalog_index]
    value_to_uid[key] = uid
  uids = []
  for value in values:
    uids.append(value_to_uid[value])
  return uids

  field.get_value('base_category')

try:
  # Validate the form
  form = getattr(context,form_id)
  form.validate_all_to_request(request)
  my_field = None
  # XXXXXXXXXXXXXXXXX
  # we should update data here if we want to be clever
  # Find out which field defines the relation
  for f in form.get_fields():
    if f.has_value( 'base_category'):
        #if f.get_value('base_category') == base_category:
        k = f.id
        v = getattr(request,k,None)
        if v in (None, '', 'None', []) and context.getProperty(k[3:]) in (None, '', 'None', []):
          # The old value is None and the new value is not significant
          # This bug fix is probably temporary since '' means None
          pass
        elif v != context.getProperty(k[3:]):
          old_value = context.getProperty(k[3:])
          my_field = f
          new_value = v
          base_category = f.get_value( 'base_category')
  if my_field and base_category is not None:
    same_keys = 0
    if my_field.meta_type == 'MultiRelationStringField':
      # The checkProperty sometimes does not provide an
      # acceptable value - XXXX - see vetement_id in Modele View
      if old_value is '' or old_value is None:
        old_value = []
      try:
        old_value = list(old_value)
      except:
        old_value = [old_value]
      #return str((context.getProperty('vetement_id_list'),my_field.id, new_value, old_value))
      if checkSameKeys(new_value, old_value):
        # Reorder keys
        same_keys = 1
    portal_type = map(lambda x:x[0],my_field.get_value('portal_type'))
    # We work with strings - ie. single values
    kw ={}
    kw[my_field.get_value('catalog_index')] = new_value
    context.portal_selections.setSelectionParamsFor('search_relation', kw.copy())
    kw['base_category'] = base_category
    kw['portal_type'] = portal_type
    request.set('base_category', base_category)
    request.set('portal_type', portal_type)
    request.set(my_field.get_value('catalog_index'), new_value)
    request.set('field_id', my_field.id)
    uids = o.getValueUids(base_category, portal_type=portal_type)
    context.portal_selections.setSelectionCheckedUidsFor('search_relation', uids)
    relation_list = context.portal_catalog(**kw)
    if len(new_value) == 0:
      # Clear the relation
      o.setValueUids(base_category,  (), portal_type=portal_type)
    elif same_keys:
      uids = getOrderedUids(uids, new_value, my_field.get_value('catalog_index'))
      return o.update_relation( form_id,
                                my_field.id,
                                selection_index,
                                selection_name,
                                uids,
                                object_uid)
    elif len(relation_list) > 0:
      # If we have only one in the list, we don't want to lost our time by
      # selecting it. So we directly do the update
      if len(relation_list) == 1:
          selection_index=None
          uids = [relation_list[0].uid]
          return o.update_relation( form_id = form_id,
                                    field_id = my_field.id,
                                    selection_index = selection_index,
                                    selection_name = selection_name,
                                    uids = uids,
                                    object_uid = object_uid)
      return o.search_relation( REQUEST=request )
    else:
      request.set('catalog_index', my_field.get_value('catalog_index'))
      if my_field.meta_type == 'MultiRelationStringField':
        request.set('relation_values', request.get( my_field.id, None))
      else:
        request.set('relation_values', [request.get( my_field.id, None)])
      request.set('default_module', my_field.get_value('default_module'))
      request.set('portal_type', portal_type[0])
      return o.create_relation_dialog( REQUEST=request )
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)
else:
  message = 'Relation+Unchanged.'

if not selection_index:
  redirect_url = '%s/%s?%s' % ( o.absolute_url()
                            , form_id
                            , 'portal_status_message=%s' % message
                            )
else:
  redirect_url = '%s/%s?selection_index=%s&selection_name=%s&%s' % ( o.absolute_url()
                            , form_id
                            , selection_index
                            , selection_name
                            , 'portal_status_message=%s' % message
                            )

request[ 'RESPONSE' ].redirect( redirect_url )
