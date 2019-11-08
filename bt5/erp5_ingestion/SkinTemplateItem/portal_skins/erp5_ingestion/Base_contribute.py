"""
  Use to contribute file to ERP5.
"""
from ZTUtils import make_query

portal = context.getPortalObject()
translateString = portal.Base_translateString


MARKER = ['', None]
portal_contributions = portal.portal_contributions
context_url = context.getRelativeUrl()

if synchronous_metadata_discovery is None:
  synchronous_metadata_discovery = portal.portal_preferences.isPreferredSynchronousMetadataDiscovery(False)

if redirect_to_document is None:
  redirect_to_document = portal.portal_preferences.isPreferredRedirectToDocument(False)
if user_login is None:
  # get current authenticated user
  user_login = portal.portal_membership.getAuthenticatedMember().getId()

document_kw = {'user_login': user_login,
               'group': group,
               'publication_section': publication_section,
              }

if use_context_for_container:
  document_kw['container_path'] = context_url
if portal_type not in MARKER:
  document_kw['portal_type'] = portal_type
if classification not in MARKER:
  document_kw['classification'] = classification
if follow_up_list:
  document_kw['follow_up_list'] = follow_up_list


# FIXME: this list of properties should not be hardcoded.
for key in ('title', 'short_title', 'reference', 'language', 'version', 'description', ):
  value = kw.get(key, None)
  if value not in MARKER:
    document_kw[key] = value

if attach_document_to_context:
  # attach document to current context using follow_up
  follow_up_list = document_kw.setdefault('follow_up_list', [])
  if context_url not in follow_up_list:
    # attach to context only if not already attached
    follow_up_list.append(context_url)
  document_kw['follow_up_list'] = follow_up_list

document_kw.update({'discover_metadata': not synchronous_metadata_discovery})
if url is not None:
  # we contribute and URL, this happens entirely asynchronous
  document = portal_contributions.newContentFromURL(url = url, \
                                                    repeat = max_repeat, \
                                                    batch_mode = batch_mode, \
                                                    **document_kw)
  if document is None:
    # portal contributions could not upload it
    if cancel_url is not None:
      # we can assume we can redirect
      redirect_url= '%s?%s' %(cancel_url, 
                            make_query(dict(portal_status_message=translateString("Wrong or not accessible URL address."))))
      return context.REQUEST.RESPONSE.redirect(redirect_url)
else:
  # contribute file
  document_kw.update({'file': file})
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

if redirect_to_context or redirect_to_document or redirect_url is not None:
  # this is an UI mode where script should handle HTTP redirects and is likely used
  # by ERP5 form
  if redirect_to_document and document is not None:
    # explicitly required to view ingested document
    return document.Base_redirect('view',
                      keep_items={'portal_status_message': message,
                                  'editable_mode': editable_mode})
  elif redirect_url is not None:
    # redirect URL has been supplied by caller
    redirect_url= '%s?%s' %(redirect_url, 
                            make_query(dict(portal_status_message=message)))
    return context.REQUEST.RESPONSE.redirect(redirect_url)
  elif redirect_to_context:
    # explicitly required to view ingested document
    return context.Base_redirect('view',
                                 keep_items={'portal_status_message': message})

# return document (for non UI mode)
return document
