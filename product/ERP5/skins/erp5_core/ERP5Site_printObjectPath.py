##parameters=
site = context.portal_url.getPortalObject()
object_list = []
for o in site.objectValues():
  if hasattr(o,'getMetaType'):
    if o.getMetaType()=='ERP5 Folder':
      path = o.getPhysicalPath()
      object_ids = o.objectIds()
      for id in object_ids:
        object_list += [path + (id,)]
object_list.sort()
for path in object_list:
  print '/'.join(path)
return printed

