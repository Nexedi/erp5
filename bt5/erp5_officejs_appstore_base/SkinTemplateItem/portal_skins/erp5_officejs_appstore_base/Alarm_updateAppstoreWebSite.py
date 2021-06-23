import json
from DateTime import DateTime

portal = context.getPortalObject()
preference_tool = portal.portal_preferences
software_product_list = portal.portal_catalog(portal_type='Software Product', validation_state='validated', sort_on='creation_date')
appstore_data = []
logo_url_list = []
i = 0
for software_product in software_product_list:
  web_site = software_product.SoftwareProduct_getRelatedWebSite()
  version = web_site.getLayoutProperty('configuration_latest_version')
  web_section =  web_site[version]
  manifest_url = web_section.getLayoutProperty('configuration_webapp_manifest_url', default=None)
  # allow to have application without web manifest
  if manifest_url is not None:
    manifest = portal.portal_catalog.getResultValue(reference=version + '/' + manifest_url)
    if manifest is not None:
      try:
        data = json.loads(manifest.getData())
      except ValueError:
        continue
      src_icon = data['icons'][0]['src']
      logo = portal.portal_catalog.getResultValue(reference='%' + src_icon, version=version, portal_type='File')
      if logo is not None:
        logo_url_list.append('appstore/' + logo.getReference())
        # Future domain could be defined by user
        app_domain = software_product.getFollowUpId(portal_type="Web Section")
        app_data = {
          "int_index": str(i),
          "application_image_type": 'image',
          "application_image_url": logo.getReference(),
          "application_toc_accept": 'true',
          "application_published": web_section.getModificationDate().strftime("%m/%d/%Y"),
          "application_submitted": web_section.getModificationDate().strftime("%m/%d/%Y"),
          "application_description": data["description"] if "description" in data else data["name"],
          "application_url": "%s://%s.%s/" % (preference_tool.getPreferredSystemAppstoreWildcardProtocol(),
                                              app_domain,
                                              preference_tool.getPreferredSystemAppstoreWildcardDomain()),
          "application_title": data['short_name'],
          "application_category": data['category'] if "category" in data else "Documents",
          "application_title_i18n": "application.custom.%s.title" % app_domain,
          "application_description_i18n": "application.custom.%s.description" % app_domain
        }
        appstore_data.append(app_data)
        i+=1

json_data = json.dumps(appstore_data)
json_document = portal.document_module['store_officejs_data_application_sample_json']

if (json_data != json_document.getData()):
  # Do not modify document history with edit if nothing changed
  json_document.edit(data=json.dumps(appstore_data))
  manifest_content = portal.web_page_module['store_officejs_base_appcache'].getTextContent()
  # Ensure the appcache content is modified when the json is too
  logo_url_list.append('# %s' % DateTime())
  portal.web_page_module['store_officejs_appcache'].edit(text_content=manifest_content.replace('${logo_list}', '\n'.join(logo_url_list)))
