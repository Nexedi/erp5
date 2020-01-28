import json

_, reference = context.Base_postDataToActiveResult(
  active_process_url, input_value)
return json.dumps({"reference": reference})
