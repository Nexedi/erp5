import json
portal = context.getPortalObject()

software_publication = context
return_dict = {
  "status": 1,
  "message": "Wait for Submit"
}

if software_publication.getSimulationState() == 'draft':
  return return_dict

software_publication_line = software_publication.objectValues(
  portal_type="Software Publication Line",
)[0]
software_product = software_publication_line.getResourceValue(portal_type="Software Product")

web_site = software_product.SoftwareProduct_getRelatedWebSite()
version = software_publication.getReference().replace("SP-", "")
try:
  web_section =  web_site[version]
except KeyError:
  return_dict["message"] = 'Not found'
  return return_dict

manifest_url = web_section.getLayoutProperty('configuration_webapp_manifest_url', default=None)
if manifest_url is None:
  return_dict["message"] = 'Configuration webapp manifest url not found'
  return return_dict

manifest = portal.portal_catalog.getResultValue(reference=version + '/' + manifest_url)
if manifest is None:
  return_dict["message"] = 'Configuration webapp manifest not found'
  return return_dict

try:
  data = json.loads(manifest.getData())
except ValueError:
  return_dict["message"] = 'Invalid configuration webapp manifest JSON'
  return return_dict

src_icon = data['icons'][0]['src']
logo = portal.portal_catalog.getResultValue(reference='%' + src_icon, version=version, portal_type='File')
if not logo:
  return_dict["message"] = "App logo '%s' not found" % src_icon
  return return_dict

return_dict["status"] = 0
return_dict["message"] = "OK"
return return_dict
