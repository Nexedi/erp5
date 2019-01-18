import json

return json.dumps({
  q + ('2' if i else ''): {
    'line_list': [dict(zip(results.names(), row)) for row in results]
  }
  for i, q in enumerate((context.ActivityTool_getCurrentActivities,
                         context.ActivityTool_getSQLActivities))
  for q, results in (('SQLDict', q(table='message')),
                     ('SQLQueue', q(table='message_queue')))
})
