from DateTime import DateTime
import json

if REQUEST is None:
  REQUEST = context.REQUEST
if response is None:
  response = REQUEST.RESPONSE

# The vanilla HTML is wanted
response.setBase(None)

# Allow any external app to download the source code
response.setHeader("Access-Control-Allow-Origin", "*")

web_page = context
web_section = context.getWebSectionValue()
# Must-Revalidate caching policy uses Base_getWebSiteDrivenModificationDate
modification_date_string = web_page.Base_getWebSiteDrivenModificationDate().rfc822()

modified_since = REQUEST.getHeader('If-Modified-Since', '')
if modified_since:
  if DateTime(modified_since).rfc822() == modification_date_string:
    response.setStatus(304)
    return ""

portal_type = web_page.getPortalType()
web_content = web_page.getTextContent()

# set headers depending on type of script
if (portal_type == "Web Script"):
  response.setHeader('Content-Type', 'application/javascript; charset=utf-8')
  if web_page.getTextContentSubstitutionMappingMethodId():
    web_content = web_page.TextDocument_substituteTextContent(web_content, mapping_dict={
      'modification_date': modification_date_string,
      # Make JSLint happy for the service worker code
      'required_url_list': json.dumps(
        getattr(web_section, web_section.getLayoutProperty("configuration_precache_manifest_script",
                                                           default="WebSection_getPrecacheManifest"))()
      )
    })

elif (portal_type == "Web Style"):
  response.setHeader('Content-Type', 'text/css; charset=utf-8')

elif (portal_type == "Web Manifest"):
  response.setHeader('Content-Type', 'text/cache-manifest; charset=utf-8')

else:
  content_security_policy = "default-src 'self' data: blob:"
  x_frame_options = "SAMEORIGIN"
  if (web_section):
    content_security_policy = web_section.getLayoutProperty("configuration_content_security_policy", default=content_security_policy).replace('"', "'")
    x_frame_options = web_section.getLayoutProperty("configuration_x_frame_options", default=x_frame_options)

  if (mapping_dict is not None):
    mapping_dict['content_security_policy'] = content_security_policy
    web_content = web_page.TextDocument_substituteTextContent(web_content, mapping_dict=mapping_dict)

  # Do not allow to put inside an iframe
  if not x_frame_options == "ALLOW-FROM-ALL":
    response.setHeader("X-Frame-Options", x_frame_options)
  response.setHeader("X-Content-Type-Options", "nosniff")

  # Only fetch code (html, js, css, image) and data from this ERP5, to prevent any data leak as the web site do not control the gadget's code
  response.setHeader("Content-Security-Policy", content_security_policy)

  response.setHeader('Content-Type', '%s; charset=utf-8' % web_page.getContentType('text/html'))


return web_content
