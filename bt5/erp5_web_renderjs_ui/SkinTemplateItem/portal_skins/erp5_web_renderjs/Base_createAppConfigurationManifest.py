import re
import json
import base64
from datetime import datetime

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

  router_file_reference = context.getLayoutProperty("configuration_router_gadget_url", default="")
  if router_file_reference is "":
    raise ValueError("Router Gadget Layout Property is missing")
  appcache_file_reference = context.getLayoutProperty("configuration_manifest_url", default="")
  if appcache_file_reference is "":
    raise ValueError("Manifest URL Layout Property is missing")
  configuration_file_reference = context.getLayoutProperty("configuration_app_configuration", default="")
  if configuration_file_reference is "":
    raise ValueError("Configuration URL Layout Property is missing")
  #configuration_file_reference = "testmanifest.configuration" # TODO DELETE THIS WHEN FINISH so configuration_manifest var is used
  #appcache_file_reference = "testmanifest.appcache"

  router_file = portal_catalog.getResultValue(
      portal_type = 'Web Page',
      reference = router_file_reference)
  if router_file is None:
    raise ValueError("Router web page '%s' not found" % router_file_reference)

  appcache_manifest = portal_catalog.getResultValue(
      portal_type = 'Web Manifest',
      reference = appcache_file_reference)
  if appcache_manifest is None:
    raise ValueError("Appcache manifest '%s' not found" % appcache_file_reference)

  configuration_manifest = portal_catalog.getResultValue(
      portal_type = 'Web Manifest',
      reference = configuration_file_reference)
  if configuration_manifest is None:
    #TODO create it
    raise ValueError("Configuration manifest '%s' not found" % configuration_file_reference)

  router_content = router_file.getTextContent()

  hateoas_appcache = "hateoas_appcache" #HARDCODED - get from hateoas static web section (here.parent.lines[hateoas_appcache])
  portal_skin = getElementFromContent("portal_skin_folder", router_content)
  if portal_skin is None:
    raise KeyError("portal_skin_folder setting not found in router")
  app_action_string = getElementFromContent("app_actions", router_content)
  if app_action_string is None:
    raise KeyError("app_actions setting not found in router")
  new_dialog_form = getElementFromContent("new_content_action", router_content)
  date = datetime.now().strftime("%c")
  app_action_list = []

  app_action_string = app_action_string.replace('(', '[').replace(')', ']').replace(',]', ']').replace("'", '"')
  app_action_raw_list = json.loads(app_action_string)
  for app_action in app_action_raw_list:
    pair = app_action.split(" | ");
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

  configuration_path_list = []

  for key in portal_actions_dict:
    path = "portal_types/%s" % key
    configuration_path_list.append(base64.b64encode(path))
    for action in portal_actions_dict[key]:
      path = "portal_types/%s/%s" % (key, action)
      configuration_path_list.append(base64.b64encode(path))
      try:
        action_object = context.restrictedTraverse(path)
        form = action_object.getActionText().split('/')[-1]
        path = "portal_skins/%s/%s" % (portal_skin, form)
        configuration_path_list.append(base64.b64encode(path))
      except KeyError as e:
        raise KeyError("Error getting portal action info: " + str(e))

  if new_dialog_form is not None:
    path = "portal_skins/%s/%s" % (portal_skin, new_dialog_form)
    configuration_path_list.append(base64.b64encode(path))

  configuration_element_lines = ""
  for path in configuration_path_list:
    configuration_element_lines += hateoas_appcache + "/definition_view/" + path + "\n"

  content = "CONFIGURATION MANIFEST\n# generated on %s\nCACHE:\n\n" % date
  content += configuration_element_lines
  content += "\nNETWORK:\n*"
  configuration_manifest.setTextContent(content)

  appcache_configuration_elements = "#app_configuration_resources\n"
  appcache_configuration_elements += "#CONFIGURATION ELEMENTS generated on %s. Same as in configuration manifest\n" % date
  appcache_configuration_elements += configuration_element_lines
  appcache_configuration_elements += "#/app_configuration_resources\n\n"
  token_found = False
  configuration_added = False
  appcache_content = ""
  appcache_line_list = appcache_manifest.getTextContent().split('\n')
  for line in appcache_line_list:
    if "#app_configuration_resources" in line:
      token_found = True
    if "NETWORK:" in line and not configuration_added:
      appcache_content += appcache_configuration_elements
      configuration_added = True
    if "#/app_configuration_resources" in line:
      appcache_content += appcache_configuration_elements
      configuration_added = True
      token_found = False
    if not token_found:
      if not "#/app_configuration_resources" in line:
        appcache_content += line + '\n'
  appcache_manifest.setTextContent(appcache_content)


except Exception as e:
  if batch_mode:
    return 'ERROR: ' + str(e)
  return context.Base_redirect('view', keep_items=dict(portal_status_message='ERROR creating configuration manifest: ' + str(e)))

return printed

if batch_mode:
  return 'done'
return context.Base_redirect('view', keep_items=dict(portal_status_message="Configuration manifest created: " + configuration_file_reference))
