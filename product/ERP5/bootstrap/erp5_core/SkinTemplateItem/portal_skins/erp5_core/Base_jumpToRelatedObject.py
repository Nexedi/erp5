# from ZTUtils import make_query
portal = context.getPortalObject()
Base_translateString = portal.Base_translateString
checkPerm = portal.portal_membership.checkPermission

redirect_context = context

if jump_from_relative_url is None:
  relation = context
else:
  relation = portal.restrictedTraverse(jump_from_relative_url)

# FIXME: performance problem getting *all* related documents URL is not scalable.
getter_base_name = ''.join([x.capitalize() for x in base_category.split('_')])

if same_type(portal_type, ''):
  portal_type = [portal_type]

if related:
  # Try to see if we have already many visible results with the catalog and if we are
  # in the case we should jump to a module (in which case we would also use the catalog
  # to display result). This can avoid retrieving all objects. It would be better to have
  # get[Category]RelatedList returning a lazy list directly.
  if len(portal_type) == 1:
    catalog_list = portal.portal_catalog(portal_type=portal_type, limit=2,
                                       **{'default_%s_uid' % base_category: relation.getUid()})
    if len(catalog_list) == 2:
      related_list = catalog_list
      module_id = portal.getDefaultModuleId(portal_type[0], None)
      if module_id is not None:
        module = portal.getDefaultModule(portal_type[0])
        message = Base_translateString(
          # first, try to get a full translated message with portal types
          "Documents related to %s." % context.getPortalType(),
           # if not found, fallback to generic translation
          default=Base_translateString('Documents related to ${that_portal_type} : ${that_title}.',
            mapping={"that_portal_type": context.getTranslatedPortalType(),
                     "that_title": context.getTitleOrId() }),)
        return module.Base_redirect(
                 'view', keep_items={'default_%s_uid' % base_category: relation.getUid(),
                                     'ignore_hide_rows': 1,
                                     'reset': 1,
                                     'portal_status_message': message})
  search_method = getattr(relation, 'get%sRelatedList' % getter_base_name)
else:
  search_method = getattr(relation, 'get%sList' % getter_base_name)

related_list = search_method(portal_type = portal_type)

relation_found = 0
if len(related_list) == 0:
  message = Base_translateString(
    'No %s Related' % portal_type[0],
    default=Base_translateString('No ${portal_type} related.',
                                 mapping={'portal_type': Base_translateString(portal_type[0])}))

elif len(related_list) == 1:
  relation_found = 1
  related_object = portal.restrictedTraverse(related_list[0], None)
  if related_object is None:
    # this might be a category
    related_object = portal.portal_categories.resolveCategory(
                           "%s/%s" % (base_category, related_list[0]))

  if related_object is not None and checkPerm("View", related_object) :
    if target_form_id is not None:
      form_id = target_form_id
    else:
      form_id = 'view'
    redirect_context = related_object
    message = Base_translateString(
      # first, try to get a full translated message with portal types
      "%s related to %s." % (related_object.getPortalType(), context.getPortalType()),
       # if not found, fallback to generic translation
      default=Base_translateString('${this_portal_type} related to ${that_portal_type} : ${that_title}.',
        mapping={"this_portal_type": related_object.getTranslatedPortalType(),
                 "that_portal_type": context.getTranslatedPortalType(),
                 "that_title": context.getTitleOrId() }),)
  else :
    message = Base_translateString("You are not authorised to view the related document.")
    relation_found = 0

else:
  # jump to the module if we can guess it
  if len(portal_type) == 1:
    module_id = portal.getDefaultModuleId(portal_type[0], None)
    if module_id is not None:
      module = portal.getDefaultModule(portal_type[0])
      # related case already done, we have to do the non related case
      # We can not pass parameters through url, otherwise we might have too long urls (if many uids).
      # Therefore check if we are in usual case of module form having a listbox, and update
      # selection for it
      get_uid_method = getattr(relation, 'get%sUidList' % getter_base_name)
      portal_type_object = portal.portal_types[module.getPortalType()]
      module_form = portal_type_object.getDefaultViewFor(module)
      if "listbox" in [x for x in module_form.objectIds()]:
        listbox = module_form.listbox
        selection_name = listbox.get_value("selection_name")
        portal.portal_selections.setSelectionToAll(selection_name)
        uid_list = get_uid_method(portal_type=portal_type, checked_permission="View")
        portal.portal_selections.setSelectionParamsFor(selection_name, {"uid": uid_list})
        return module.Base_redirect('view', keep_items=dict(ignore_hide_rows=1))

  # compute the list of objects we are actually authorised to view
  related_object_list = []
  for path in search_method(portal_type=portal_type) :
    obj = portal.restrictedTraverse(path, None)
    if obj is None:
      # this might be a category
      obj = portal.portal_categories.resolveCategory(
                           "%s/%s" % (base_category, path))

    if obj is not None and checkPerm("View", obj):
      related_object_list.append(obj)
  if len(related_object_list) == 0 :
    message = Base_translateString("You are not authorised to view any related document.")
    relation_found = 0
  else :
    selection_uid_list = [x.getUid() for x in related_object_list]
    message = Base_translateString(
      # first, try to get a full translated message with portal types
      "Documents related to %s." % context.getPortalType(),
       # if not found, fallback to generic translation
      default=Base_translateString('Documents related to ${that_portal_type} : ${that_title}.',
        mapping={"that_portal_type": context.getTranslatedPortalType(),
                 "that_title": context.getTitleOrId() }),)
    return context.Base_redirect(relation_form_id,
                keep_items=dict(reset=1,
                                uid=selection_uid_list,
                                portal_status_message=message))

query_params = dict(portal_status_message=message)
if selection_name and not relation_found:
  query_params['selection_name'] = selection_name
  query_params['selection_index'] = selection_index

return redirect_context.Base_redirect(
         form_id, keep_items=query_params)
