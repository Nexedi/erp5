project_uid = context.project_uid

title_dict = container.REQUEST.get(
                'Movement_getProjectTitle.project_title_dict') or {}
if project_uid in title_dict:
  return title_dict[project_uid]

movement = context.getObject()
if movement.getSourceProjectUid() == project_uid:
  reference = movement.getSourceProjectReference()
  if reference:
    return '%s - %s' % (reference, movement.getSourceProjectTranslatedTitle())
  return movement.getSourceProjectTranslatedTitle()

reference = movement.getDestinationProjectReference()
if reference:
  return '%s - %s' % (reference, movement.getDestinationProjectTranslatedTitle())
return movement.getDestinationProjectTranslatedTitle()
