import json

response_success = {
    "jsonrpc": "2.0",
    "result": 42,   # can be any data type: number, string, object, array
    "id": 1         # must match the request ID
}

return json.dumps(response_success)
