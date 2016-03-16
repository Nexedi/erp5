from Products.ERP5Type.Message import translateString
from Products.ERP5Type.Document import newTempDocument
return_list = []
i = 1
portal = context.getPortalObject()
for worklist in context.portal_workflow.listActionInfos():
  # XXX worklist translation process is a bit tricky. We translate only the first part of "XXX to Validate (count)"
  title = worklist['title']
  title, count = title.split(' (', 1)
  title = "%s (%s" % ( translateString(title), count )
  o = newTempDocument(portal, str(i))
  o.edit(
    count=worklist['count'],
    title=title,
    worklist_url=worklist['url']
  )
  return_list.append(o)
  i+=1

return return_list
