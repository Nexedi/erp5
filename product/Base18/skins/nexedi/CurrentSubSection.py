## Script (Python) "change_language"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Modify the language cookie
##

request = context.REQUEST
PARENTS = request.PARENTS
portal_root = context.portal_url.getPortalObject()
portal_root_path = portal_root.getPhysicalPath()
lang_list = context.gettext.get_available_languages()

if len(PARENTS) >= (2 + len(portal_root_path)):
  section = PARENTS[len(PARENTS) - 1
         - len(portal_root.getPhysicalPath())]
  subsection = PARENTS[len(PARENTS) - 2
         - len(portal_root.getPhysicalPath())]
  if section.id in lang_list:
    if len(PARENTS) >= (3 + len(portal_root_path)):
      subsection = PARENTS[len(PARENTS) - 3
         - len(portal_root_path)]
    else:
      subsection = context
else:
  subsection = context

return subsection