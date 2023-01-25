"""
    Generate current document's information structure needed to be rendered
    by web widget Document_viewPopupTemplate.
"""
from zExceptions import Unauthorized

doc_info = {}
doc_info['owner_list'] = context.Base_getOwnerInfoList()

if context.getModificationDate() is not None:
  doc_info['modification_date'] = context.Base_getDiffBetweenDateAndNow(context.getModificationDate())

publication_date = context.Document_getLastWorkflowStateEntryDate(state=('public,'),
                                                                  state_name='validation_state')
if publication_date is not None:
  doc_info['publication_date'] = context.Base_getDiffBetweenDateAndNow(publication_date)

release_date = context.Document_getLastWorkflowStateEntryDate(state=('released,'),
                                                              state_name='validation_state')
if release_date is not None:
  doc_info['release_date'] = context.Base_getDiffBetweenDateAndNow(release_date)

try:
  doc_info['status'] = context.getTranslatedValidationStateTitle() or ''
except AttributeError:
  doc_info['status'] = ''

try:
  doc_info['group'] = context.getGroupTitle() or ''
except AttributeError:
  doc_info['group'] = ''

try:
  doc_info['project'] = context.getFollowUpTitle(checked_permission='View') or ''
except (AttributeError, Unauthorized):
  doc_info['project'] = ''

try:
  doc_info['language'] = context.getLanguage() or ''
except AttributeError:
  pass

try:
  doc_info['version'] = context.getVersion() or ''
except AttributeError:
  pass

try:
  doc_info['reference'] = context.getReference() or ''
except AttributeError:
  pass

doc_info['thumbnail_url'] = context.Base_getThumbnailAbsoluteUrl()

# add web sections document belongs too
if website is None:
  website = context.getWebSiteValue() or context.REQUEST.get('current_web_site')

doc_info['sections'] = []
if document_web_section_list is None:
  document_web_section_list = website.getWebSectionValueList(context)
for websection in document_web_section_list:
  doc_info['sections'].append({'title': websection.getCompactTranslatedTitle(),
                               'url': websection.absolute_url()})
doc_info['url'] = context.absolute_url()

return context.Document_viewPopupTemplate(**doc_info)
