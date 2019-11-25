from Products.Formulator.Errors import FormValidationError
from ZTUtils import make_query
portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

request=context.REQUEST

# We stop doing this
#base_category = context.getBaseCategoryId()
base_category = None

o = context.restrictedTraverse(object_path)

# XXX We should not use meta_type properly,
# XXX We need to discuss this problem.(yusei)
def checkFieldType(field, field_type):
  if field.meta_type==field_type:
    return True
  elif field.meta_type=='ProxyField':
    template_field = field.getRecursiveTemplateField()
    if template_field.meta_type==field_type:
      return True
  return False

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
    key = context.portal_catalog(uid=uid)[0].getObject().getProperty(catalog_index)
    value_to_uid[key] = uid
  uids = []
  for value in values:
    uids.append(value_to_uid[value])
  return uids

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
      if v in (None, '', 'None', [], ()) and context.getProperty(k[3:]) in (None, '', 'None', [], ()):
        # The old value is None and the new value is not significant
        # This bug fix is probably temporary since '' means None
        pass
      elif v != context.getProperty(k[3:]):
        old_value = context.getProperty(k[3:])
        my_field = f
        new_value = v
        base_category = f.get_value( 'base_category')
  if my_field and base_category is not None:
    if new_value == '':
      new_value = []
    if same_type(new_value,'a'):
      new_value = [new_value]
    same_keys = 0
    if checkFieldType(my_field, 'MultiRelationStringField'):
      # The checkProperty sometimes does not provide an
      # acceptable value - XXXX - see vetement_id in Modele View
      if old_value is '' or old_value is None:
        old_value = []
      try:
        old_value = list(old_value)
      except TypeError:
        old_value = [old_value]
      #return str((context.getProperty('vetement_id_list'),my_field.id, new_value, old_value))
      if checkSameKeys(new_value, old_value):
        # Reorder keys
        same_keys = 1
    portal_type = [x[0] for x in my_field.get_value('portal_type')]
    # We work with strings - ie. single values
    kw ={}
    kw[my_field.get_value('catalog_index')] = new_value
    context.portal_selections.setSelectionParamsFor('Base_viewRelatedObjectList', kw.copy())
    kw['base_category'] = base_category
    kw['portal_type'] = portal_type
    request.set('base_category', base_category)
    request.set('portal_type', portal_type)
    request.set(my_field.get_value('catalog_index'), new_value)
    request.set('field_id', my_field.id)
    previous_uids = o.getValueUidList(base_category, portal_type=portal_type)
    relation_list = context.portal_catalog(**kw)
    relation_uid_list = [x.uid for x in relation_list]
    uids = []
    for uid in previous_uids:
      if uid in relation_uid_list:
        uids.append(uid)
    context.portal_selections.setSelectionCheckedUidsFor('Base_viewRelatedObjectList', uids)
    if len(new_value) == 0:
      # Clear the relation
      o.setValueUidList(base_category,  (), portal_type=portal_type)
    elif same_keys:
      uids = getOrderedUids(uids, new_value, my_field.get_value('catalog_index'))
      return o.Base_editRelation( form_id = form_id,
                                  field_id = my_field.id,
                                  selection_index = selection_index,
                                  selection_name = selection_name,
                                  uids = uids,
                                  object_uid = object_uid,
                                  listbox_uid=None)
    elif len(relation_list) > 0:
      # If we have only one in the list, we don't want to lose our time by
      # selecting it. So we directly do the update
      if len(relation_list) == 1:
        selection_index=None
        uids = [relation_list[0].uid]
        return o.Base_editRelation( form_id = form_id,
                                    field_id = my_field.id,
                                    selection_index = selection_index,
                                    selection_name = selection_name,
                                    uids = uids,
                                    object_uid = object_uid,
                                    listbox_uid=None)
      # This is just added when we want to just remove
      # one item inside a multiRelationField
      else:
        if len(relation_uid_list) == len(new_value):
          complete_value_list = []
          # We have to find the full value, for example instead of
          # /foo/ba% we should have /foo/bar
          for value in new_value:
            catalog_index = my_field.get_value('catalog_index')
            kw[catalog_index] = value
            complete_value = context.portal_catalog(**kw)[0].getObject().getProperty(catalog_index)
            complete_value_list.append(complete_value)
          new_value = complete_value_list
          uids = getOrderedUids(relation_uid_list, new_value, my_field.get_value('catalog_index'))
          selection_index=None
          return o.Base_editRelation( form_id = form_id,
                                    field_id = my_field.id,
                                    selection_index = selection_index,
                                    selection_name = selection_name,
                                    uids = uids,
                                    object_uid = object_uid,
                                    listbox_uid=None)

      kw = {}
      kw['form_id'] = 'Base_viewRelatedObjectList'
      kw['selection_index'] = selection_index
      kw['object_uid'] = object_uid
      kw['field_id'] = my_field.id
      kw['portal_type'] = portal_type
      kw['base_category'] = base_category
      kw['selection_name'] = 'Base_viewRelatedObjectList'
      kw['cancel_url'] = request.get('HTTP_REFERER')
      redirect_url = '%s/%s?%s' % ( o.absolute_url()
                                , 'Base_viewRelatedObjectList'
                                , make_query(kw)
                                )
    else:
      request.set('catalog_index', my_field.get_value('catalog_index'))
      if checkFieldType(my_field, 'MultiRelationStringField'):
        request.set('relation_values', request.get( my_field.id, None))
      else:
        request.set('relation_values', [request.get( my_field.id, None)])
      request.set('default_module', my_field.get_value('default_module'))
      request.set('portal_type', portal_type[0])
      return o.Base_viewCreateRelationDialog( REQUEST=request )
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)
else:
  message = Base_translateString('Relation unchanged.')

if redirect_url is None:
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
