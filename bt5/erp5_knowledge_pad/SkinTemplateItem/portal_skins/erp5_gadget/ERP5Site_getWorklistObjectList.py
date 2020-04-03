from Products.ERP5Type.Message import translateString
return_list = []
i = 1
portal = context.getPortalObject()
for worklist in context.portal_workflow.listActionInfos():
  title = worklist['title']
  if ' (' in title:
    # Worklist translation process is a bit tricky. We translate only the first part of "X to Validate (count)"
    title, count = title.split(' (', 1)
    title = "%s (%s" % ( translateString(title), count )
  o = portal.newContent(temp_object=True, portal_type='Document', id=str(i))
  o.edit(
    count=worklist['count'],
    title=title,
    worklist_url=worklist['url']
  )
  return_list.append(o)
  i+=1

return return_list
