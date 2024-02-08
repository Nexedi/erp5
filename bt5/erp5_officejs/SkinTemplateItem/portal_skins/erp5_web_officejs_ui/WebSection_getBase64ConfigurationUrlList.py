import json
import base64
from erp5.component.module.Log import log

def getElementFromContent(key, content):
  before_template = '"%s" type="text/x-renderjs-configuration">'
  before = before_template % key
  after  = '</script>'
  start = content.find(before) + len(before)
  stop  = content.find(after, start)
  result = content[start:stop]
  if (not "<" in result) and (not ">" in result) and (result != ""):
    return result
  return None

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

try:

  hateoas_appcache = context.getLayoutProperty("hateoas_appcache", default="hateoas_appcache")

  router_file_reference = context.getLayoutProperty("configuration_router_gadget_url", default="")
  if router_file_reference is "":
    raise ValueError("Router Gadget Layout Property is missing")
  result_list = portal_catalog.getDocumentValueList(
    portal_type = 'Web Page',
    reference = router_file_reference,
    validation_state = 'published%')
  if len(result_list) == 0:
    raise ValueError("Router web page '%s' not found" % router_file_reference)
  router_content = result_list[0].getTextContent()

  portal_skin = getElementFromContent("portal_skin_folder", router_content)
  if portal_skin is None:
    raise KeyError("portal_skin_folder setting not found in router")

  app_action_string = getElementFromContent("app_actions", router_content)
  if app_action_string is None:
    raise KeyError("app_actions setting not found in router")

  app_action_list = []
  app_action_string = app_action_string.replace('(', '[').replace(')', ']').replace(',]', ']').replace("'", '"')
  app_action_raw_list = json.loads(app_action_string)
  for app_action in app_action_raw_list:
    pair = app_action.split(" | ")
    if len(pair) != 2:
      raise SyntaxError("Syntax error in app_action router setting")
    app_action_list.append(pair)

  portal_actions_dict = {}
  for app_action in app_action_list:
    portal_type = str(app_action[0])
    action = str(app_action[1])
    if portal_type in portal_actions_dict:
      portal_actions_dict[portal_type] = portal_actions_dict[portal_type] + [action]
    else:
      portal_actions_dict[portal_type] = [action]

  new_dialog_form_list = []
  for portal_type in portal_actions_dict:
    portal_type_dict_setting = portal_type.replace(" ", '_').lower() + "_dict"
    portal_type_dict = getElementFromContent(portal_type_dict_setting, router_content)
    if portal_type_dict is not None:
      portal_type_dict = json.loads(portal_type_dict)
      if "new_content_dialog_form" in portal_type_dict:
        new_dialog_form_list.append(str(portal_type_dict["new_content_dialog_form"]))

  configuration_path_list = []
  for key in portal_actions_dict:
    path = "portal_types/%s" % key
    configuration_path_list.append(base64.b64encode(path.encode()).decode())
    for action in portal_actions_dict[key]:
      path = "portal_types/%s/%s" % (key, action)
      configuration_path_list.append(base64.b64encode(path.encode()).decode())
      try:
        action_object = context.restrictedTraverse(path)
        form = action_object.getActionText().split('/')[-1]
        path = "portal_skins/%s/%s" % (portal_skin, form)
        configuration_path_list.append(base64.b64encode(path.encode()).decode())
      except KeyError as e:
        raise KeyError("Error getting portal action info: " + str(e))

  if new_dialog_form_list:
    for form in new_dialog_form_list:
      path = "portal_skins/%s/%s" % (portal_skin, form)
      configuration_path_list.append(base64.b64encode(path.encode()).decode())

  url_list = []
  for path in configuration_path_list:
    url_list.append(hateoas_appcache + "/definition_view/" + path)

  return url_list

except (ValueError, KeyError, SyntaxError, AttributeError) as e:
  if batch_mode == "0":
    raise e
  log('ERROR generating Base64 configuration url list: ' + str(e))
  return []
