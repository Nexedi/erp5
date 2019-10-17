project_title = context.getTitle()
portal_type='Bug'

import time
time.sleep(5)

state_list = ['confirmed']
if (closed):
  state_list = ['delivered', 'stopped']

from DateTime import DateTime
now = DateTime()
now_minus_7 = now - 7
catalog_kw = {}#{'creation_date': {'query': (now_minus_7, now), 'range': 'minmax'}}
bug_list = [x for x in context.portal_catalog(portal_type=portal_type,
                                              destination_project_title=project_title,
                                              simulation_state=state_list,
                                              **catalog_kw)]

'''
print bug_list
for x in bug_list:
  print x.getTitle()

return printed
'''
if not bug_list:
  return "0"
count = len(bug_list)
return count
