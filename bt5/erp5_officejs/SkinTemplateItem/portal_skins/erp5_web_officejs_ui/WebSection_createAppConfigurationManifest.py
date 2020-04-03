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
date = datetime.now().strftime("%c")

try:

  hateoas_appcache = context.getLayoutProperty("hateoas_appcache", default="hateoas_appcache")

  router_file_reference = context.getLayoutProperty("configuration_router_gadget_url", default="")
  if router_file_reference is "":
    raise ValueError("Router Gadget Layout Property is missing")

  router_file = portal_catalog.getResultValue(
      portal_type = 'Web Page',
      reference = router_file_reference)
  if router_file is None:
    raise ValueError("Router web page '%s' not found" % router_file_reference)
  router_content = router_file.getTextContent()

  configuration_file_reference = getElementFromContent("configuration_manifest", router_content)
  if configuration_file_reference is None or configuration_file_reference is "":
    raise ValueError("configuration_manifest router setting is missing")
  configuration_manifest = portal_catalog.getResultValue(
      portal_type = 'Web Manifest',
      reference = configuration_file_reference)
  if configuration_manifest is None:
    module = portal.getDefaultModule('Web Page')
    configuration_manifest = module.newContent(portal_type='Web Manifest',
                                               reference=configuration_file_reference)
    configuration_manifest.publish()

  url_list = context.WebSection_getBase64ConfigurationUrlList(batch_mode=0)
  configuration_element_lines_string = ""
  for path in url_list:
    configuration_element_lines_string += hateoas_appcache + "/definition_view/" + path + "\n"
  content = "CONFIGURATION MANIFEST\n# generated on %s\nCACHE:\n\n" % date
  content += configuration_element_lines_string
  content += "\nNETWORK:\n*"
  configuration_manifest.setTextContent(content)

except (ValueError, KeyError, SyntaxError, AttributeError) as e:
  if batch_mode:
    return 'ERROR: ' + str(e)
  return context.Base_redirect('view', keep_items=dict(portal_status_message='ERROR creating configuration manifest: ' + str(e)))

if batch_mode:
  return 'done'
return context.Base_redirect('view', keep_items=dict(portal_status_message="Configuration manifest created: " + configuration_file_reference))
