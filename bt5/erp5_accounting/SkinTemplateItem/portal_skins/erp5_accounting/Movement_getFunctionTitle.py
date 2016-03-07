movement = context.getObject()
function_uid = context.function_uid

title_dict = container.REQUEST.get(
      'Movement_getFunctionTitle.function_title_dict') or {}
if function_uid in title_dict:
  return title_dict[function_uid]

if movement.getSourceFunctionUid() == function_uid:
  reference = movement.getSourceFunctionReference()
  if reference:
    return '%s - %s' % (reference, movement.getSourceFunctionTranslatedTitle())
  return movement.getSourceFunctionTranslatedTitle()

reference = movement.getDestinationFunctionReference()
if reference:
  return '%s - %s' % (reference, movement.getDestinationFunctionTranslatedTitle())
return movement.getDestinationFunctionTranslatedTitle()
