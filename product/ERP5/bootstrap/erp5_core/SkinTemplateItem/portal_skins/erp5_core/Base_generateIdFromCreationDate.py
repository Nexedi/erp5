# retrieve a date from object and return the new id
if obj is None:
  obj = context

# don't change custom (non-int) ids
old_id = obj.getId()
if not old_id.isdigit():
  return old_id

date = obj.getCreationDate()
if date is None:
  from DateTime import DateTime
  date = DateTime()

date = date.Date().replace('/', '')
return "%s-%s" %(date, old_id)
