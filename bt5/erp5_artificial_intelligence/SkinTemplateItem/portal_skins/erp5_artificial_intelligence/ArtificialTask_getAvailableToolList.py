"""Return the selectable tools for the my_tool_list field.

The field TALES is `python: [('', '')] + here.ArtificialTask_getAvailableToolList()`,
so this script must return (title, value) pairs.

A callable is a tool only when the `description` property holds the
OpenAI tool definition as JSON.

WARNING: `portal_callables` can hold scripts whose description is not JSON.
The JSON test removes them.
"""
import json

result = []

for script in context.getPortalObject().portal_callables.objectValues(
    portal_type='Python Script'):
  try:
    specification = json.loads(script.getDescription())
    name = specification['function']['name']
  except Exception:
    continue

  if name != script.getId():
    # The harness resolves the tool by id. A different name in the schema
    # would make the model call a tool that does not answer.
    continue

  result.append((name, name))

result.sort()
return result
