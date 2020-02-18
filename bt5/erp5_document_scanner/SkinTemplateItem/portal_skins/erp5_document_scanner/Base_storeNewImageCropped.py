import json
_, uuid = context.Base_postDataToActiveResult(
  active_process_url, input_value,
  generate_new_uid=True)
return json.dumps({"uuid": uuid})
