"""
  This script will create all knowledge pads user may need in using
  ERP5 and respective web sites. This script should be integrated through
  an interaction workflow on Assignment so when the first assignment for user is
  opened this script will be called and everything will be created.
"""
portal = context.getPortalObject()

# ERP5 front
context.ERP5Site_createDefaultKnowledgePadListForUser(default_pad_group=None,
                                                      mode='erp5_front',
                                                      owner=owner)
web_site = None
# Customize this to respective needs
default_website_id = None
if default_website_id is not None:
  web_site = getattr(portal.web_site_module, default_website_id, None)

if web_site is not None:
  # Web front
  web_site.ERP5Site_createDefaultKnowledgePadListForUser(default_pad_group=None,
                                                         mode='web_front',
                                                         owner=owner)
  # web section
  web_site.ERP5Site_createDefaultKnowledgePadListForUser(default_pad_group='default_section_pad',
                                                         mode='web_section',
                                                         owner=owner)
  # web section content
  web_site.ERP5Site_createDefaultKnowledgePadListForUser(default_pad_group='default_content_pad',
                                                         mode='web_section',
                                                         owner=owner)
