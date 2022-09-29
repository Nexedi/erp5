"""
Returns a random page in a given Web Section. This Gadget
renderer can be used asynchronously only for now.

web_section_url -- a relative URL to the web section
                    (relative to portal or to site)
"""
import random
request = context.REQUEST
portal = context.getPortalObject()

# Find the box if this gadget is asynchronous
#   XXX-JPS: this could show that the script is
#            not called on the appropriate context
#            ie. the box. Discussion is needed here
#            in order to make widgets and gadgets
#            consistent (ie. develop once)
#            --
#            The biggest issue in current design
#            is that all calls are made at the level
#            of the site or at the level of the portal
#            by passing a parameter to the object to
#            edit. This is clearly againt object orientation
if box_relative_url:
  box = portal.restrictedTraverse(box_relative_url)

# Get the preferences (some casting of preferences would
# probably be a good thing here so that there is no need
# to cas them later)
#
# Prevent fail if no box is provided.
if box is not None:
  preferences = box.KnowledgeBox_getDefaultPreferencesDict()
else:
  preferences = {}

if web_section_url is None:
  web_section_url = preferences.get('web_section_url', '') # XXX-JPS - Why do we have to do casting ? (used to be str()

# Try to find the web site else use the portal
current_web_site = request.get('current_web_site', None)
if current_web_site is None and parent_web_section_url is not None:
  # XXX-JPS This shows inconsistent API between async and non async mode
  #          Some unification is needed
  current_web_site = portal.restrictedTraverse(parent_web_section_url).getWebSiteValue()

if current_web_site is None:
  current_web_site = context.getWebSiteValue()

if current_web_site is None:
  current_web_site = portal

# Try to find the real section
web_section = current_web_site.restrictedTraverse(web_section_url)

# Select a random page in the web section
if web_section is not None:
  web_page_list = web_section.getDocumentValueList()
  web_page_len = len(web_page_list)
  if web_page_len:
    web_page_index = random.randint(0, web_page_len - 1)
    return web_page_list[web_page_index].asStrippedHTML()

return '' # Nothing to display
