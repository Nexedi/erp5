# this script has an `format` argument
# pylint: disable=redefined-builtin
"""
  This script returns a standard file name, build from reference, version and
  language (this is only the base part of the name, the extension should be appended
  in another place). It does the reverse of getPropertyDictFromFilename, so changes in
  filename parsing regular expression should be reflected here.
  It is used as a type-based method.
"""
original_filename = context.getFilename('')
original_extension = None
if '.' in original_filename:
  original_filename, original_extension = original_filename.rsplit('.', 1)
if context.hasReference():
  filename = context.getReference()
elif original_filename:
  filename = original_filename
else:
  filename = context.getTitleOrId()
if context.hasVersion():
  filename = '%s-%s' % (filename, context.getVersion(),)
if context.hasLanguage():
  filename = '%s-%s' % (filename, context.getLanguage(),)
if format or original_extension:
  extension = (format or original_extension).split('.')[-1]
  filename = '%s.%s' % (filename, extension,)
return filename
