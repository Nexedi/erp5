request=context.REQUEST
form = getattr(context, request.get('form_id'))
if str(context.getUid()) == request.get('object_uid'):
  context.log(request.get('default_editable_mode'))
  request.set('editable_mode', request.get('default_editable_mode'))
  request.set('handled', True)
  return form()
