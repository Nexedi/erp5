import json

portal = context.getPortalObject()
software_product_list = portal.portal_catalog(portal_type='Software Product', validation_state='validated')
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
      data = json.loads(manifest.getData())
      src_icon = data['icons'][0]['src']
      logo = portal.portal_catalog.getResultValue(reference='%' + src_icon, version=version, portal_type='File')
      if logo is not None:
        logo_url_list.append('appstore/' + logo.getReference())
        # Future domain could be defined by user
        app_domain = software_product.getFollowUpId(portal_type="Web Section")
        appstore_data.append({
          "int_index": str(i),
          "application_image_type": 'image',
          "application_image_url": logo.getReference(),
          "application_toc_accept": 'true',
          "application_published": 'some_date',
          "application_submitted": 'other_date',
          "application_description": data["description"] if "description" in data else data["name"],
          "application_url": "https://%s.app.officejs.com/" % app_domain,
          "application_title": data['short_name'],
          "application_category": data['category'] if "category" in data else "Documents",
          "application_title_i18n": "application.custom.%s.title" % app_domain,
          "application_description_i18n": "application.custom.%s.description" % app_domain
        })
        i+=1
portal.document_module['store_officejs_data_application_sample_json'].setData(json.dumps(appstore_data))
manifest_content = portal.web_page_module['store_officejs_base_appcache'].getTextContent()
portal.web_page_module['store_officejs_appcache'].setTextContent(manifest_content.replace('${logo_list}', '\n'.join(logo_url_list)))
