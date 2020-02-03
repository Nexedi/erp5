import json

_, uuid = context.Base_postDataToActiveResult(
  active_process_url, input_value)
return json.dumps({"uuid": uuid})
