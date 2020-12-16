"""
  Get last Disccussion Post for a Discussion Thread.
"""
post_list = context.searchFolder(portal_type='Discussion Post',
                                 limit=1,
                                 sort_on=[('creation_date','descending')])
if len(post_list) == 0:
  return None
else:
  return post_list[0].getObject()
