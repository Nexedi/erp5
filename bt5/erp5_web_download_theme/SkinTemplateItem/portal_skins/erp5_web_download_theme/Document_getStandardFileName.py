"""
  Show documentation in standard script.
  This is different because it try to give a extension in all situation
  and we don't get the extension from the reference.
"""
if context.hasReference():
  file_name = context.getReference()
elif context.hasSourceReference():
  file_name = context.getSourceReference()
else:
  file_name = context.getTitleOrId()

original_extension = None
if context.hasSourceReference():
  source_reference = context.getSourceReference()
  try:
    if '.tar.' in source_reference:
      name_list = source_reference.rsplit('.', 2)
      original_extension = '.'.join(name_list[1:])
    else:
      dummy, original_extension = source_reference.rsplit('.', 1)
  except ValueError:
    #no . in source reference
    pass

try:
  if context.getVersion():
    file_name = '%s-%s' % (file_name, context.getVersion(),)
except AttributeError:
  pass

if context.getLanguage():
  file_name = '%s-%s' % (file_name, context.getLanguage(),)


#Try to provide an extension in relation with portal type
if format is None and original_extension is None:
  standard_extension = {'Web Page': 'html', 'PDF': 'pdf', 'Text': 'odt'};
  original_extension = standard_extension.get(context.getPortalType(),None)

if format or original_extension:
  if format:
    extension = format.split('.')[-1]
  else:
    extension = original_extension
  file_name = '%s.%s' % (file_name, extension,)

return file_name
