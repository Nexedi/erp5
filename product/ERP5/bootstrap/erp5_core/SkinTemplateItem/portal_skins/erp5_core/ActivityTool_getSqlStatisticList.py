data = {}

for d, sql in [('SQLDict',context.ActivityTool_getCurrentActivities(table='message')),
               ('SQLQueue',context.ActivityTool_getCurrentActivities(table='message_queue'))]:
  data[d] = {'line_list':[]}
  for line in sql:
    tmp = {}
    for k in ['message','method_id','processing','node','min_pri','max_pri']:
      tmp[k] = line[k]
    data[d]['line_list'].append(tmp)

for d, sql in [('SQLDict2',context.ActivityTool_getSQLActivities(table='message')),
               ('SQLQueue2',context.ActivityTool_getSQLActivities(table='message_queue'))]:
  data[d] = {'line_list':[]}
  for line in sql:
    tmp = {'pri':line['pri']}
    for k in ['min','avg','max']:
      tmp[k] = str(line[k])
    data[d]['line_list'].append(tmp)

import json
return json.dumps(data)
