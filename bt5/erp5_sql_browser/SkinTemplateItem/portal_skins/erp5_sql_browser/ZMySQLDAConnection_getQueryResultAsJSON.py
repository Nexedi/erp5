from decimal import Decimal
import datetime
import time
import json
from DateTime import DateTime
import six

request = container.REQUEST
if request['REQUEST_METHOD'] != 'POST':
  from zExceptions import BadRequest
  raise BadRequest

response = request.RESPONSE
start = time.time()
try:
  results = context.manage_test(query)
except Exception as e:
  response.setStatus(500)
  try:
    response.write(str(e[1]).encode())
  except Exception:
    response.write(str(e).encode())
  return

# https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/isSafeInteger
MAX_SAFE_INTEGER = 2**53 - 1
def isSafeInteger(num):
  return (- MAX_SAFE_INTEGER) < num < MAX_SAFE_INTEGER

data = [ results.names() ]
for line in results.tuples():
  new_line = []
  # handle non JSON serializable data
  for v in line:
    if isinstance(v, DateTime):
      v = v.ISO()
    elif isinstance(v, datetime.datetime):
      v = v.isoformat()
    elif isinstance(v, Decimal):
      v = float(v)
    elif isinstance(v, six.integer_types + (float,)) and not isSafeInteger(v):
      # if numbers are too large to be handled by javascript, we simply return them
      # as string, this will still not work for pivot table, but at least the spreadsheet
      # will not display truncated values.
      v = str(v)

    new_line.append(v)
  data.append(new_line)

response.setHeader("Server-Timing", 'db;dur=%s;desc="SQL query"' % (1000 * (time.time() - start)))
response.setHeader('Content-Type', 'application/json')
return json.dumps(data, indent=2)
