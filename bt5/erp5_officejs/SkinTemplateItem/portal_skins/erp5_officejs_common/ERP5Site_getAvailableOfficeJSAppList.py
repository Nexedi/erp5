"""
Return a list of available OfficeJS applications installed on this ERP5 instance.

Discovers apps by querying web_site_module for Web Sites whose
container_layout, content_layout, or custom_render_method_id is
WebSection_renderOfficeJSApplicationPage (the distinguishing marker
of an OfficeJS app bootloader).

Returns a JSON list of {title, url, id} dicts.
"""
import json

portal = context.getPortalObject()
base_url = portal.absolute_url()
result = []
marker = "WebSection_renderOfficeJSApplicationPage"

for web_site in portal.web_site_module.contentValues(portal_type="Web Site"):
  container_layout = web_site.getProperty("container_layout", "")
  content_layout = web_site.getProperty("content_layout", "")
  custom_render_method_id = web_site.getProperty("custom_render_method_id", "")
  if marker in (container_layout, content_layout, custom_render_method_id):
    result.append({
      "title": web_site.getTitle(),
      "url": base_url + "/web_site_module/" + web_site.getId() + "/",
      "id": web_site.getId(),
    })

if REQUEST is not None:
  REQUEST.RESPONSE.setHeader("Content-Type", "application/json")
return json.dumps(result)
