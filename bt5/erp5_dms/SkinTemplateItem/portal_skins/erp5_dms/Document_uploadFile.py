"""
This script is called when a file is uploaded to an object via ERP5 standard interface.
It does the following:

- determines portal types appropriate for the file type uploaded, and checks if the context portal type
  is one of those (this is not a complete check, but all we can do at this stage)
- checks if context already has some data (we do not allow re-upload of files)
Otherwise it just uploads the file, bumps up revision number and calls metadata discovery script.

"""

translateString = context.Base_translateString
request = context.REQUEST
current_type = context.getPortalType()
file_name = file.filename

# we check for appropriate file type (by extension)
# ContributionTool_getCandidateTypeListByExtension script returns a tuple of
# one or more possible portal types for given extension
# we accept or suggest appropriate portal type
ext = file_name[file_name.rfind('.')+1:]
candidate_type_list = context.ContributionTool_getCandidateTypeListByExtension(ext)
if candidate_type_list == () and current_type != 'File':
  portal_status_message = translateString("Sorry, this is not one of ${portal_type}. This file should be uploaded into a file document.", 
                                    mapping = dict(portal_type = str(candidate_type_list)))
  return context.Base_redirect(dialog_id, keep_items = dict(portal_status_message=portal_status_message,cancel_url = kw['cancel_url']), **kw)
if candidate_type_list and current_type not in candidate_type_list:
  portal_status_message = translateString("Sorry, this is a ${portal_type}. This file should be uploaded into a ${appropriate_type} document.",
                                mapping = dict(portal_type = current_type, appropriate_type = str(candidate_type_list)))
  return context.Base_redirect(dialog_id, keep_items = dict(portal_status_message =portal_status_message, cancel_url = kw['cancel_url']), **kw)

context.edit(file=file)
context.activate().Document_convertToBaseFormatAndDiscoverMetadata(file_name=file_name)

msg = translateString('File uploaded.')

# Return to view mode
return context.Base_redirect(form_id, keep_items = {'portal_status_message' : msg},  **kw)
