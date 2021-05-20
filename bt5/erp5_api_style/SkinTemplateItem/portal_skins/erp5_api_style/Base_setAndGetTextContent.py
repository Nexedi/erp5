if text_content:
  context.edit(text_content=text_content)

if response_schema:
  import json
  data = json.loads(context.getTextContent())
  data["$schema"] = response_schema
  data["id"] = context.getRelativeUrl()
  return json.dumps(data, indent=2)
return context.getTextContent()
