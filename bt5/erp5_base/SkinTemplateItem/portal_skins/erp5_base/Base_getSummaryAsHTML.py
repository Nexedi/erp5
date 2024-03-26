"""
  Generate a HTML Summary of an object.
  Use "No ZODB" approach if possible.
"""
import six
request = context.REQUEST
portal = context.getPortalObject()
is_temp_object = context.isTempObject()

if not is_temp_object:
  web_site = request.get('current_web_site', context.getWebSiteValue())
else:
  web_site = portal.restrictedTraverse(context.web_site)
web_site_url = web_site.absolute_url()

if is_temp_object:
  uid = context.uid
  url = context.path
  title = context.title
  path = context.path
  version = context.version
  language = context.language
  modification_date = context.modification_date
  found = context.text
  portal_type = context.object_portal_type
  # empty as we still have no ZODB object to render it (it will be done with AJAX
  inline_popup = None
  owner_url = "Base_redirectToPersonByReference?reference=%s" %context.owner
  owner_title = context.owner
  reference = context.reference
  reference_url = '%s/%s' %(web_site_url, path)
  document_web_section_list = [web_site.restrictedTraverse(x) for x in context.section_list]
else:
  # a real ZODB object
  uid = context.getUid()
  url = context.absolute_url()
  title = context.getTitle() or (hasattr(context, 'getReference') and context.getReference()) or context.getId()
  path = context.getRelativeUrl()
  version = context.getVersion()
  language = context.getLanguage()
  modification_date = context.modification_date
  document_web_section_list = web_site.getWebSectionValueList(context)
  inline_popup = context.Document_getPopupInfo(web_site, document_web_section_list)
  if six.PY2 and not isinstance(inline_popup, str):
    inline_popup = inline_popup.encode('utf-8')
  found = context.Base_showFoundText()
  portal_type = context.getTranslatedPortalType()
  owner_list = context.Base_getOwnerInfoList()
  if len(owner_list):
    owner_url = owner_list[0]["url"]
    owner_title = owner_list[0]["title"]
  else:
    owner_url = None
    owner_title = None
  reference = context.getReference
  reference_url = web_site.getPermanentURL(context)

local_parameter_dict = {
  'uid': uid,
  'url': url,
  'title': title,
  'portal_type': portal_type,
  'found': found,
  'modification_date': modification_date,
  'path': path,
  'version': version,
  'language': language,
  'owner_url': owner_url,
  'owner_title': owner_title,
  'reference': reference,
  'reference_url': reference_url,
  'document_web_section_list': document_web_section_list,
  'inline_popup': inline_popup}

html = context.Base_viewSummaryAsHTML(**local_parameter_dict)
return html
