# WARNING: this tool writes no business document and takes no model name
# from the model. The harness writes the two relative URL arguments.
# A refusal answers one text. The harness catches a raise as a tool failure.
ESCALATION_PATH = 'portal_callables/ArtificialTask_escalateToStrongModel'
NO_RUN_TEXT = 'escalation refused. the harness named no run.'

portal = context.getPortalObject()

reason = kw.get('reason') or ''
task_url = kw.get('artificial_task_relative_url') or ''
line_url = kw.get('report_line_relative_url') or ''

if not reason:
  return 'escalation refused. the parameter reason is empty.'
if not task_url or not line_url:
  return NO_RUN_TEXT

try:
  artificial_task = portal.restrictedTraverse(task_url, None)
  source_line = portal.restrictedTraverse(line_url, None)
except Exception:
  return NO_RUN_TEXT
if artificial_task is None or source_line is None:
  return NO_RUN_TEXT
if artificial_task.getPortalType() != 'Artificial Task':
  return NO_RUN_TEXT
if source_line.getPortalType() != 'Artificial Task Report Line':
  return NO_RUN_TEXT

strong_model = artificial_task.ArtificialTask_getStrongModel()
if not strong_model:
  return 'escalation refused. no strong model is configured.'

if source_line.getModel() == strong_model:
  return 'escalation refused. this run already uses the strong model.'

# No property holds the counter. Count the escalation lines.
escalation_count = 0
for task_line in artificial_task.objectValues(
    portal_type='Artificial Task Line'):
  if task_line.getSpecialise() == ESCALATION_PATH:
    escalation_count += 1
if escalation_count >= 1:
  return 'escalation refused. this run already escalated one time.'

request_line = source_line.getParentValue(
  ).ArtificialTaskReport_startStrongModelRound(
    source_line=source_line, model=strong_model, reason=reason)
if request_line is None:
  return 'escalation refused. this run cannot start one new round now.'

return ('escalation accepted. the model of this run is now %s. answer again '
        'with the same tools.' % (strong_model, ))
