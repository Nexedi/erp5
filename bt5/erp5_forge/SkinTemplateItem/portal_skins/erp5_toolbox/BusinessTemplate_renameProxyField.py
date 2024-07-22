"""
This dialog allows to change massively the template used by many
proxy fields. In the top listbox of the dialog, inforations are
entered like this :

  original id                                  new id
  Base_viewFieldLibrary.my_title Base_viewFieldLibrary.my_view_mode_title

Then all proxy of this business template using the template described
by the original id will use the new template described by the new id.

Note that we do not directly change proxy fields, we first unproxify
them, them proxify them again with the new template. Like this we should
not loose informations
"""
message = "Proxy fields updated"
portal_skins = context.getPortalObject().portal_skins

# to_rename_dict contains user information about template change
to_rename_dict = {}
for line in listbox:
  new_id = line['new_id']
  original_id = line['original_id']
  if '' not in (new_id, original_id):
    to_rename_dict[original_id] = new_id

# selected_dict contains the list of selected fields that needs
# to change of template. The user can select or unselect any field
# in the preview_listbox
selected_dict = {}
if preview_listbox is not None:
  for line in preview_listbox:
    if line['selected']:
      selected_dict[line['hidden_field_path']] = None

next_preview_listbox = []

# Parse a document and it's sub objects in order to find all
# ProxyField
def iterate(document, skin_path):
  for sub_object in document.objectValues():
    if sub_object.meta_type == "ERP5 Form":
      unproxify_dict = {}
      proxify_dict = {}
      for field in sub_object.objectValues():
        if field.meta_type == "ProxyField":
          form_id = field.get_value('form_id')
          field_id = field.get_value('field_id')
          key = "%s.%s" % (form_id, field_id)
          if key in to_rename_dict:
            field_path =  "%s/%s/%s" % (skin_path, sub_object.id, field.id)
            if field_path in selected_dict:
              unproxify_dict[field.id] = None
              proxify_dict[field.id] = to_rename_dict[key]
            next_preview_listbox.append(
                {"original_id":key,
                 "new_id":to_rename_dict[key],
                 "field_path": field_path,
                 "hidden_field_path": field_path,
                  })

      if len(unproxify_dict):
        if not update:
          # In order to not loose information, we unproxify, then proxify
          # with new template
          sub_object.unProxifyField(field_dict=unproxify_dict)
          sub_object.proxifyField(field_dict=proxify_dict)

    if sub_object.meta_type == "Folder":
      skin_path = "%s/%s" % (skin_path, sub_object.getId())
      iterate(sub_object, skin_path=skin_path)

# Only search ProxyFields within skin folder defined by this business template
if len(to_rename_dict):
  for skin_folder in [getattr(portal_skins, x) for x in \
      context.getTemplateSkinIdList()]:
    iterate(skin_folder, skin_path = skin_folder.getId())

if update:
  # Prepare data in order to display the preview listbox
  count = 1
  next_preview_listbox.sort(key=lambda x: (x['original_id'], x['field_path']))
  extra_kw = {}
  for line in next_preview_listbox:
    line["preview_listbox_key"] = "%03i" % count
    line["selected"] = line["hidden_field_path"] in selected_dict or preview_listbox is None
    extra_kw["field_preview_listbox_hidden_field_path_new_%03i" % count] = line["hidden_field_path"]
    extra_kw["field_preview_listbox_selected_new_%03i" % count] = line["selected"]
    count += 1
  # This is awfull hack, we should improve Base_updateDialogForm in
  # order to handle data stored in REQUEST.form
  for key, value in extra_kw.items():
    context.REQUEST.form[key] = value
  context.Base_updateDialogForm(listbox=listbox,
      preview_listbox=next_preview_listbox)
  return context.BusinessTemplate_renameProxyFieldDialog(**kw)
else:
  return context.Base_redirect(keep_items={"portal_status_message":message})
