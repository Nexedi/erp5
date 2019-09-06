can_delete = False
document_id = context.getId()
try:
  can_delete = (document_id == str(int(document_id)))
except:
  pass

if can_delete:
  context.getParentValue().manage_delObjects(ids=[document_id])
  return 'deleted'
return 'not deleted'
