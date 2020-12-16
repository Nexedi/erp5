result = []

def getContentValues(item, parent_id):
  cv_list = item.contentValues()
  for cv in cv_list:
    custom_id = "%s-%s"%(parent_id, cv.id)
    result.append((cv,custom_id))
    getContentValues(cv, custom_id )

getContentValues(context, str(context.id) )

return result
