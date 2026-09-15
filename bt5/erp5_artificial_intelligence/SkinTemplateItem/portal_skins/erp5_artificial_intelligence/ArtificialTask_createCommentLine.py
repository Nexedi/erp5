import json
artificial_task = context

line = artificial_task.newContent(portal_type='Artificial Task Line', text_content=data)
line.stop()

return json.dumps({
  "post": {
    "date": line.getCreationDate().ISO8601(),
    "text": data,
    "response": False
  }
})
