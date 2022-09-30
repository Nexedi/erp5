"""
  Returns the section this document is part.
  When selecting the section we return the highest
  possible root section the current document belongs to.
  So if  we have:
    - 'WebSite/S1/S2/S3/Document1'
  script will return 'S1'

  This script is used to generate the menus.
"""
site = context.getWebSiteValue()
section = context.getWebSectionValue()

# document isn't part of section but accessed from the root of the site
if section is site:
  return None

# This document is part of a section. Look for all parents and
# return the last one before the site root
current_section = section
while current_section.getPortalType() != "Web Site":
  section = current_section
  current_section = current_section.getParentValue()
return section
