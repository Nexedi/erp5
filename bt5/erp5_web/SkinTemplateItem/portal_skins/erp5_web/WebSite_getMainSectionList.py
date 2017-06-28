"""
  Returns the list of alls visible Web Sections for Web Site.
  This script is used to generate the memus.
"""
site = context.getWebSiteValue()
section_list = site.contentValues(portal_type='Web Section', sort_on='int_index', checked_permission='View')
return [x for x in section_list if x.isVisible()]
