"""Answer the role of one Artificial Task Report Line.

The property `text_content` of one line holds one JSON object. That
object holds the key `role`. The value of the key `role` is `user`,
`llm_request`, `assistant`, `tool`, `tool_request` or `error`.

The script answers the value of the key `role`. The script answers the
empty text when the line holds no text content. The script answers the
empty text when the text content is not one JSON object. The script
answers the empty text when the JSON object holds no key `role`.

The script never raises. One ERP5 Form calls this script as the default
of one read-only field. One listbox calls this script as one column. A
raise there stops the render of the whole page.

PARAMETER LIST: empty. This script takes no parameter.
"""
import json

text_content = context.getTextContent()
if not text_content:
  return ''

try:
  payload = json.loads(text_content)
except Exception:
  return ''

if not isinstance(payload, dict):
  return ''

role = payload.get('role', '')
if not role:
  return ''
return role
