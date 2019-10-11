import time
time.sleep(4)

project_title = context.getTitle()
portal_type='Benchmark Result'

state_list = ['failed', 'stopped', 'public_stopped']

#from DateTime import DateTime
#now = DateTime()
#now_minus_7 = now - 7
#catalog_kw = {'creation_date': {'query': (now_minus_7, now), 'range': 'minmax'}}
catalog_kw = {}
bug_list = [x for x in context.portal_catalog(portal_type=portal_type,
                                              source_project_title=project_title,
                                              #simulation_state=state_list,
                                              **catalog_kw)]

return "PASSED"

print bug_list
for x in bug_list:
  print x.getTitle()
  print x.getStringIndex()

return printed

if not bug_list:
  return "0"
count = len(bug_list)
return count

return last_finished_test.getStringIndex()
