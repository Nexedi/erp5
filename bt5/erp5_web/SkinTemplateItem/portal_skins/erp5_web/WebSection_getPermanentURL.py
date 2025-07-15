"""
 This script is part of ERP5 Web

 ERP5 Web is a business template of ERP5 which provides a way
 to create web sites which can display selected
 ERP5 contents through multiple custom web layouts.

 This script returns the absolute URL of the current
 document in a pretty way and taking into account
 virtual hosting. The purpose of this script is to be
 able to access documents through a URL such as:

 www.mysite.com/mysection/a-document-reference

 even if the physical path of the document is

 /erp5/web_page_module/33

 This script can be considered as the reverse of
 WebSection_getDocumentValue.

 The default script looks in the acquisition context
 for the first relevant section and builds a URL
 based on the section absolute_url and on the
 document reference.

 The document parameter is required.

 More sophisticated behaviours are possible.

 SUGGESTIONS:

 - change the behaviour of WebSection_getPermanentURL
   for non anonymous

 - change the behaviour of WebSection_getPermanentURL
   for documents which are not published.
"""
portal_type = document.getPortalType()

# If no reference is defined, no way to build a permanent URL.
reference = document.getReference()
if not reference:
  return document.absolute_url()

# Return absolute URL if this is not an appropriate portal_type
portal = context.getPortalObject()
valid_portal_type_list = portal.getPortalDocumentTypeList()
portal_type = document.getPortalType()
if portal_type not in valid_portal_type_list:
  return document.absolute_url()

# Return absolute URL if this is not a 'live' document
validation_state = ('released', 'released_alive', 'published', 'published_alive',
                    'shared', 'shared_alive', 'public', 'validated')
if document.getValidationState() not in validation_state:
  return document.absolute_url()

# Return the URL
web_section = context.getWebSectionValue()
if web_section is None:
  web_section = context
return "%s%s" % (web_section.absolute_url(), reference)
