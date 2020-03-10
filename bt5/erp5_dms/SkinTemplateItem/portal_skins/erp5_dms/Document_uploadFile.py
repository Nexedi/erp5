# this script has an `file` argument
# pylint: disable=redefined-builtin
"""
This script is called when a file is uploaded to an object via ERP5 standard interface.
It does the following:

- determines portal types appropriate for the file type uploaded, and checks if the context portal type
  is one of those (this is not a complete check, but all we can do at this stage)
- checks if context already has some data (we do not allow re-upload of files)
Otherwise it just uploads the file, bumps up revision number and calls metadata discovery script.

"""
from Products.ERP5Type.Log import log, WARNING
from Products.ERP5Type.Message import translateString

translate = context.Base_translateString
current_type = context.getPortalType()
file_name = file.filename

# we check for appropriate file type (by extension)
# ContributionTool_getCandidateTypeListByExtension script returns a tuple of
# one or more possible portal types for given extension
# we accept or suggest appropriate portal type
ext = file_name[file_name.rfind('.')+1:]
candidate_type_list = context.ContributionTool_getCandidateTypeListByExtension(ext)

if not candidate_type_list and current_type != 'File':
  log("Document {!s} does not support extension {!s}. Use generic 'File' document.".format(current_type, ext), level=WARNING)
  return context.Base_redirect(dialog_id, keep_items={
    'portal_status_message': translate("Current document does not support ${ext} file extension.", mapping={'ext': ext}),
    'cancel_url': cancel_url})

if candidate_type_list and current_type not in candidate_type_list:
  log("File extension {!s} is supported only by {!s}, not by current document {!s}.".format(ext, candidate_type_list, current_type), level=WARNING)
  return context.Base_redirect(dialog_id, keep_items={
    'portal_status_message': translate("Current document does not support ${ext} file extension.", mapping={'ext': ext}),
    'cancel_url': cancel_url})

context.edit(file=file)
context.activate().Document_convertToBaseFormatAndDiscoverMetadata(file_name=file_name)

# Return to view mode
return context.Base_redirect(form_id, keep_items={'portal_status_message': translateString('File uploaded.')})
