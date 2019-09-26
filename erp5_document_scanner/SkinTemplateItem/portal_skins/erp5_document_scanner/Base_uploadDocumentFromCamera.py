"""
  Use to contribute file to ERP5.
"""
portal = context.getPortalObject()
translateString = portal.Base_translateString

MARKER = ['', None]
portal_contributions = portal.portal_contributions

if synchronous_metadata_discovery is None:
  synchronous_metadata_discovery = portal.portal_preferences.isPreferredSynchronousMetadataDiscovery(False)

user_login = portal.portal_membership.getAuthenticatedMember().getId()

document_kw = {'user_login': user_login,
               'group': group,
               'publication_section': publication_section}

if portal_type not in MARKER:
  document_kw['portal_type'] = portal_type

document_kw['default_follow_up_uid'] = context.getUid()

for key in ('title', 'short_title', 'reference', 'language', 'version', 'description'):
  value = kw.get(key, None)
  if value not in MARKER:
    document_kw[key] = value

document_kw.update({'discover_metadata': not synchronous_metadata_discovery})

pdf_data_list = []
image_module = context.getPortalObject().image_module
active_process = portal.restrictedTraverse(active_process_url)

for result in active_process.getResultList():
  pdf_data_list.append(
    image_module.newContent(data=result.detail,
                            temp=True).convert(format="pdf")[1])

pdf_data = context.ERP5Site_mergePDFList(pdf_data_list=pdf_data_list)

# contribute file
document_kw.update({
  'data': pdf_data,
  "filename": "{}.pdf".format(
    document_kw.get("title") or DateTime().strftime('%d-%m-%Y_%Hh%M'))
})
document = portal_contributions.newContent(**document_kw)

is_existing_document_updated = False
if synchronous_metadata_discovery:
  # we need to do all synchronously, in other case portal_contributions will do
  # this in an activity
  if document.isSupportBaseDataConversion():
    document.processFile()
  filename = document.getFilename()
  merged_document = document.Document_convertToBaseFormatAndDiscoverMetadata(
                               filename=filename,
                               user_login=user_login,
                               input_parameter_dict=document_kw)
  is_existing_document_updated = (merged_document!=document)
  document = merged_document

document_portal_type = document.getTranslatedPortalType()
if not is_existing_document_updated:
  message = translateString('${portal_type} created successfully.',
              mapping=dict(portal_type=document_portal_type))
else:
  message = translateString('${portal_type} updated successfully.',
              mapping=dict(portal_type=document_portal_type))

if batch_mode:
  return document

return document.Base_redirect('view',
                              keep_items={'portal_status_message': message,
                              'editable_mode': editable_mode})
