## Script (Python) "ERP5Site_getObjectPathListAsText"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
site = context.portal_url.getPortalObject()
object_list = []
for o in site.objectValues():
  if hasattr(o,'getMetaType'):
    if o.getMetaType()=='ERP5 Folder':
      path = o.getPhysicalPath()
      object_ids = o.objectIds()
      for id in object_ids:
        object_list += [path + (id,)]
path = site.portal_simulation.getPhysicalPath()
for id in site.portal_simulation.objectIds():
  object_list += [path + (id,)]
object_list.sort()
for path in object_list:
  print '/'.join(path)
return printed
