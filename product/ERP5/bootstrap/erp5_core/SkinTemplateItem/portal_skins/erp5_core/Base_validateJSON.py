import json
result = True
try:
  json.loads(json_string)
except ValueError:
  result = False
return result
