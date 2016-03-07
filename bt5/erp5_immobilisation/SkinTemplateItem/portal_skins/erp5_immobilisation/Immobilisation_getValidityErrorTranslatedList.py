# Return a list of translated strings corresponding to errors for this movement validity
Base_translateString = context.Base_translateString

def translateString(msg):
  try:
    msg = msg.get('msg')
    mapping = msg.get('mapping')
  except AttributeError:
    mapping = None
  if translate is None:
    return msg
  translate_kw = {'catalog':'content'}
  if mapping is not None:
    translate_kw['mapping'] = mapping
  return Base_translateString(msg, **translate_kw)


error_list = context.checkImmobilisationConsistency(to_translate=1)
if len(error_list) == 0:
  return [Base_translateString('Valid')]

translated_list = []
for error in error_list:
  object = context.getPortalObject().restrictedTraverse(error[0])
  string = translateString(error[3])
  object_title = object.getTitle() or object.getId()
  translated_list.append('%s : %s' % (object_title, string))
return translated_list
