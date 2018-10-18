"""
================================================================================
Save, download or return generated HTML Document
================================================================================
"""
# parameters:
# ------------------------------------------------------------------------------
# doc_download                        download this document in HTML format
# doc_save                            save this web page in HTML format
# doc_version                         version of the document
# doc_title                           title of the document
# doc_relative_url                    relative url to set as follow-up
# doc_language                        language of the document
# doc_reference                       reference of the document
# doc_full_reference                  full reference with version/language
# doc_modification_date               date to set as initial date
# doc_html_file                       text content for document
# doc_aggregate_list                  not applicable (only used for events)

if doc_save:
  web_page_module = getattr(context, 'web_page_module', None)
  if web_page_module is not None:
    web_page = web_page_module.newContent(
      portal_type="Web Page",
      version=doc_version,
      follow_up=doc_relative_url,
      title=doc_title,
      language=doc_language,
      publication_date=doc_modification_date or None,
      reference=doc_reference
    )
    web_page.edit(
      text_content=doc_html_file
    )
    if not context.isModuleType():
      context.setAggregate(web_page.getRelativeUrl())
    message = context.Base_translateString(
      '%(portal_type)s created successfully as Web Page.' % {
        'portal_type': context.getTranslatedPortalType()
      }
    )
    return web_page.Base_redirect(
      keep_items=dict(portal_status_message=message)
    )
  #XXX else:

# download
elif doc_download:
  context.REQUEST.RESPONSE.setHeader("Content-Type", "text/html;")
  context.REQUEST.RESPONSE.setHeader("Content-Disposition", 'attachment; filename="' + doc_full_reference + '.html"')

# display in browser
else:
  context.REQUEST.RESPONSE.setHeader("Content-Type", "text/html;")
  context.REQUEST.RESPONSE.setHeader("Content-Disposition", 'filename="' + doc_full_reference + '.html"')
return doc_html_file
