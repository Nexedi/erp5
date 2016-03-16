#from decimal import Decimal
import datetime
import json
from DateTime import DateTime

response = container.REQUEST.RESPONSE

try:
  results = context.manage_test(query)
  data = [ results.names() ]
  data.extend(results.tuples())
except Exception, e:
  response.setStatus(500)
  try:
    response.write(str(e[1]))
  except Exception:
    response.write(str(e))
  return

# handle non JSON serializable data
new_data = [data[0]]
for line in data[1:]:
  new_line = []
  for v in line:
    if isinstance(v, DateTime):
      v = v.ISO()
    elif isinstance(v, datetime.datetime):
      v = v.isoformat()
    elif "Decimal" in repr(v): # XXX decimal is not allowed in restricted environment
      v = float(v)
    new_line.append(v)
  new_data.append(new_line)

response.setHeader('Content-Type', 'application/json')
return json.dumps(new_data, indent=2)
