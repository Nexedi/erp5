portal = context.getPortalObject()
N_ = portal.Base_translateString

# If we create one portal type per attachment... no need
# but if attachment can be text, image, etc. We can not
# A simple solution: use title to group
type_list = map(lambda x: x.getId(), context.allowedContentTypes())

file_type_list = ('Image', 'File')
sub_form_type_list = filter(lambda x: x not in file_type_list, type_list)

# A simple solution: use title to group
viewable_content_list = context.contentValues(portal_type=type_list, checked_permission='View',validation_state = 'embedded')

content_group_dict = {}
for content in viewable_content_list:
  if content.getValidationState() in ['embedded','draft']:
    title = content.getTitle()
    content_group_dict.setdefault(title, [])
    content_group_dict[title].append(content)

# Now sort every group by creation date (to be done)
# XXXX


# Define some hard coded values

attachement_method = getattr(context, 'PDFDocument_getApplicationIncomeDict')
attachement_type_dict = attachement_method()

# add other group title
for group_title in attachement_type_dict.keys():
  content_group_dict.setdefault(group_title,[])

# Now create a sorted list of titles of attachments
title_list = content_group_dict.keys()
title_list.sort()

# Now build the report sections
from Products.ERP5Form.Report import ReportSection
result = []
for title in title_list:
  if attachement_type_dict.has_key(title):
    description = attachement_type_dict[title].get('description', 'No description')
    requirement = attachement_type_dict[title].get('requirement', 'No requirement')
  else:
    description = 'No description'
    requirement = 'Requirement not found'

  selection_params={'title': title,
                    'description': N_(description),
                    'attachment_list' : content_group_dict[title]}

  # XXX display requirement word only on required attachments
  if requirement == 'Required':
    selection_params.update({'requirement': N_(requirement)})
  else:
    selection_params.update({'requirement': ''})
  

  result.append(
    ReportSection(
      path=context.getPhysicalPath(),
#      title=title,
      level=1,
      form_id='PDFDocument_viewAttachmentReportSection',
      selection_name='attachment_selection',
      selection_params=selection_params,
      listbox_display_mode='FlatListMode')
  )


return result
