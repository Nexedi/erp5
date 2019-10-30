from decimal import Decimal
import datetime
import time
import json
from DateTime import DateTime

response = container.REQUEST.RESPONSE
start = time.time()
try:
  results = context.manage_test(query)
  data = [ results.names() ]
  data.extend(results.tuples())
except Exception, e:
  response.setStatus(500)
  try:
    data = e[1]
  except IndexError:
    data = e
  return str(data)

# handle non JSON serializable data
new_data = [data[0]]
for line in data[1:]:
  new_line = []
  for v in line:
    if isinstance(v, DateTime):
      v = v.ISO()
    elif isinstance(v, datetime.datetime):
      v = v.isoformat()
    elif isinstance(v, Decimal):
      v = float(v)
    new_line.append(v)
  new_data.append(new_line)

response.setHeader("Server-Timing", "db=%s;" % (time.time() - start))
response.setHeader('Content-Type', 'application/json')
return json.dumps(new_data, indent=2)
