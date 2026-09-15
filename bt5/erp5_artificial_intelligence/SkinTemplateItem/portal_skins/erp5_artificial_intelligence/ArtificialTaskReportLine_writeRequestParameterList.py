"""Write the send parameters on one Artificial Task Report Line.

The send path reads the line only. This script is the one writer of the send
parameters. `ArtificialTask_startAgent` calls this script for every new line.
`ArtificialTaskReportLine_processRequest` calls this script for every line that
one round creates. The test suite calls this script too.

The script writes the quantity 0 on every line. ERP5 gives every new Movement
the default `quantity=1.0`, and 1.0 is one false token count.

The script writes the send parameters on one request line only. A request line
holds the role `llm_request` or the role `tool_request`.

The script writes the categories `connector` and `resource`. The script writes
the properties `model`, `request_parameter` and `is_background_enabled`. The
script writes the keys `model`, `tools` and `system` in the JSON payload of the
line.

The parameter `artificial_task` names the Artificial Task of the run. With no
value the script reads the Artificial Task of the parent report.

The parameter `source_line` names one earlier request line of the same run.
With one source line the script copies the parameters of that line. The script
then reads no Artificial Task. Every line of one run therefore holds the same
parameters.

The script also copies the base category `aggregate`. The aggregate names one
document of the run.

The property `request_parameter` can hold the key `file_id`. That key names
one file at the provider. The copy of `request_parameter` carries the key to
the next line, so every round of the run reuses the same file.

The script returns the line.
"""
import json

TOOL_NAME_CHARACTER_SET = (
  'abcdefghijklmnopqrstuvwxyz'
  'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  '0123456789_')
REQUEST_ROLE_TUPLE = ('llm_request', 'tool_request')

line = context
portal = line.getPortalObject()


def getQuantityDict():
  """Return the quantity of one new line.

  No business template of this repository holds the quantity unit `token`,
  so the unit can be absent. A write of one unit that does not exist raises.
  """
  quantity_dict = {'quantity': 0}
  try:
    if portal.portal_categories.quantity_unit.restrictedTraverse(
        'unit/token', None) is not None:
      quantity_dict['quantity_unit'] = 'unit/token'
  except Exception:
    pass
  return quantity_dict


def getPayload():
  """Return the JSON payload of the line. Return one empty map on a defect."""
  try:
    payload = json.loads(line.getTextContent() or '{}')
  except Exception:
    return {}
  if not isinstance(payload, dict):
    return {}
  return payload


def getModelResource(model_reference):
  """Return the validated Service of one model, or None.

  The base category `resource` holds the model of one line. The Service of one
  model can be absent. The Service can also be draft or cancelled. A draft
  Service and a cancelled Service are not one usable resource. The caller then
  writes no resource, and the text property `model` stays the only record.
  """
  if not model_reference:
    return None
  try:
    service_brain_list = list(portal.portal_catalog(
      portal_type='Service', reference=model_reference,
      validation_state='validated', limit=2))
  except Exception:
    return None
  for service_brain in service_brain_list:
    return service_brain.getObject()
  return None


def resolveTool(tool_name):
  """Return the Python Script of one tool name, or None.

  The checks are the checks of `resolveTool` in
  `ArtificialTaskReportLine_processRequest`. A name that the send path refuses
  must reach no model.
  """
  if not tool_name:
    return None
  for character in tool_name:
    if character not in TOOL_NAME_CHARACTER_SET:
      return None
  callable_tool = portal.portal_callables
  if tool_name not in list(callable_tool.objectIds()):
    return None
  for candidate in callable_tool.objectValues():
    if candidate.getId() != tool_name:
      continue
    get_callable_type = getattr(candidate, 'getCallableType', None)
    if get_callable_type is None or get_callable_type() != 'script':
      return None
    if candidate.getPortalType() != 'Python Script':
      return None
    return candidate
  return None


def buildToolDefinitionList(task):
  """Return the tool definitions that this run sends to the provider.

  The line holds the definitions. A later change of one tool description
  therefore does not change the meaning of one old line.
  """
  tool_definition_list = []
  for tool_id in (task.getToolList() or []):
    tool_document = resolveTool(tool_id)
    if tool_document is None:
      continue
    try:
      tool_definition_list.append(json.loads(tool_document.getDescription()))
    except Exception:
      continue
  return tool_definition_list


def buildSystemRecordList(task):
  """Return the record of the system pages of this run.

  One record holds the reference and the character count of one skill page.
  The record holds no text. A skill page can be large.
  """
  system_record_list = []
  for skill_reference in (task.getSkillList() or []):
    try:
      skill_page = portal.web_page_module.get(skill_reference, None)
    except Exception:
      skill_page = None
    if skill_page is None:
      continue
    system_record_list.append({
      'reference': skill_reference,
      'character_count': len(skill_page.getTextContent() or ''),
    })
  return system_record_list


def copyAggregate(source_document):
  """Copy the aggregate of one document to the line. This function never raises.

  A source document with no aggregate writes nothing.
  """
  try:
    aggregate_value = source_document.getAggregateValue()
  except Exception:
    return
  if aggregate_value is None:
    return
  try:
    line.setAggregateValue(aggregate_value)
  except Exception:
    pass


line.edit(**getQuantityDict())

payload = getPayload()
if payload.get('role') not in REQUEST_ROLE_TUPLE:
  return line

if source_line is not None:
  source_payload = {}
  try:
    source_payload = json.loads(source_line.getTextContent() or '{}')
  except Exception:
    source_payload = {}
  if not isinstance(source_payload, dict):
    source_payload = {}
  model = source_line.getModel()
  parameter_dict = {
    'connector_value': source_line.getConnectorValue(),
    'model': model,
    'request_parameter': source_line.getRequestParameter(),
    'is_background_enabled': source_line.getIsBackgroundEnabled(),
  }
  record_dict = {
    'model': model,
    'tools': source_payload.get('tools') or [],
    'system': source_payload.get('system') or [],
  }
  resource_value = source_line.getResourceValue()
  # The next line of the run holds the same document.
  copyAggregate(source_line)
else:
  if artificial_task is None:
    artificial_task = line.getParentValue().getFollowUpValue(
      portal_type='Artificial Task')
  if artificial_task is None:
    return line
  model = artificial_task.getModel()
  parameter_dict = {
    'connector_value': artificial_task.getConnectorValue(),
    'model': model,
    'request_parameter': artificial_task.getRequestParameter(),
    'is_background_enabled': artificial_task.getIsBackgroundEnabled(),
  }
  record_dict = {
    'model': model,
    'tools': buildToolDefinitionList(artificial_task),
    'system': buildSystemRecordList(artificial_task),
  }
  resource_value = getModelResource(model)
  # The first line of the run holds the document of the Artificial Task.
  copyAggregate(artificial_task)

line.edit(**parameter_dict)
if resource_value is not None:
  line.setResourceValue(resource_value)

for record_key, record_value in record_dict.items():
  payload[record_key] = record_value
line.setTextContent(json.dumps(payload, indent=1))

return line
