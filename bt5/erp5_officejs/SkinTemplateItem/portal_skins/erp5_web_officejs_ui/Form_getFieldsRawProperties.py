from Products.ERP5Type.Log import log

def getRealRelativeUrl(document):
  return '/'.join(context.getPortalObject().portal_url.getRelativeContentPath(document))

def getFieldRawProperties(field, meta_type=None, key=None, key_prefix=None):
  """ Return the raw properties of the field """
  if meta_type is None:
    meta_type = field.meta_type
  if key is None:
    key = field.generate_field_key(key_prefix=key_prefix)
  if meta_type == "ProxyField":
    meta_type = field.getRecursiveTemplateField().meta_type
  result = {
    "type": meta_type,
    "key": key,
    "values": {},
    "overrides": field.overrides,
    "message_values": field.message_values
  }
  # these patchs change the field property names as are required by js rendering
  form_list_patch = False
  gadget_field_patch = False
  for key in field.values.keys():
    # sometimes, field.values returns a key as string and also as a tuple
    if type(key) is str:
      result["values"][key] = field.values[key]
      if key == "columns":
        form_list_patch = True
      if key == "gadget_url":
        gadget_field_patch = True
  if form_list_patch:
    try:
      result["values"]["column_list"] = result["values"]["columns"]
      result["values"]["sort_column_list"] = result["values"]["sort_columns"]
      result["values"]["search_column_list"] = result["values"]["search_columns"]
      portal_type = result["values"]["portal_types"][0][0] if "portal_types" in result["values"] else False
      if not portal_type:
        portal_type = result["values"]["portal_type"][0][0] if "portal_type" in result["values"] else False
      query = "portal_type%3A%22" + portal_type + "%22" if portal_type else ""
      full_query = "urn:jio:allDocs?query=" + query
      result["values"]["query"] = full_query
    except KeyError:
      log("error while patching form list definition")
  if gadget_field_patch:
    try:
      result["values"]["url"] = result["values"]["gadget_url"]
      result["values"]["renderjs_extra"] = result["values"]["renderjs_extra"][0][0]
    except (ValueError, KeyError, IndexError):
      log("error while patching form gadget list definition")
  return result

if REQUEST.get("view") == "definition_view":
  traversed_document = context
  traversed_document_portal_type = traversed_document.getPortalType()
  fields_raw_properties = {}
  if traversed_document_portal_type in ("ERP5 Form", "ERP5 Report"):
    custom_action_script = False
    for group in traversed_document.Form_getGroupTitleAndId():
      if 'hidden' in group["gid"]:
        for field in traversed_document.get_fields_in_group(group["goid"]):
          if field.id == "gadget_field_action_js_script":
            custom_action_script = True
            fields_raw_properties[field.id] = getFieldRawProperties(field, key_prefix=None)
        continue
      for field in traversed_document.get_fields_in_group(group["goid"]):
        if field.id == "gadget_field_action_js_script":
          custom_action_script = True
        fields_raw_properties[field.id] = getFieldRawProperties(field, key_prefix=None)
    if custom_action_script:
      fields_raw_properties['_actions'] = {
        'put': {
          "href": "%(traversed_document_url)s/%(action_id)s" % {
            "traversed_document_url": context.getPortalObject().absolute_url() + "/" + getRealRelativeUrl(traversed_document),
            "action_id": "Base_edit"
          },
          "action": "Base_edit",
          "method": "POST",
        }
      }
  if fields_raw_properties:
    return fields_raw_properties
