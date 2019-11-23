"""
================================================================================
Save, download or return generated PDF Document
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
# doc_pdf_file                        pdf content to store
# doc_aggregate_list                  not applicable (only used for events)

from io import BytesIO

if doc_save:
  dms_module = getattr(context, 'document_module', None)
  if dms_module is not None:
    document = dms_module.newContent(
      portal_type="PDF",
      version=doc_version,
      follow_up=doc_relative_url,
      title=doc_title,
      language=doc_language,
      publication_date=doc_modification_date or None,
      reference=doc_reference
    )
    document.edit(
      source_reference=''.join([doc_reference, '.pdf']),
      file=BytesIO(doc_pdf_file)
    )
    document.setContentType("application/pdf")

    # setting aggregate in case context is an event
    if context.portal_type != 'Web Page' and not context.isModuleType():
      context.setAggregate(document.getRelativeUrl())

    # try setting predecessor/related document to later distinguish this
    # document from other documents related to the event
    try:
      document.setPredecessorValueList([context])
    except AttributeError:
      pass

    message = context.Base_translateString(
      '%(portal_type)s created successfully as PDF Document.' % {
        'portal_type': document.getTranslatedPortalType()
      }
    )

    # XXX redirect = true?
    return document.Base_redirect(
      keep_items=dict(portal_status_message=message)
    )
  #XXX else:

# download
elif doc_download:
  context.REQUEST.RESPONSE.setHeader("Content-Type", "application/pdf;")
  context.REQUEST.RESPONSE.setHeader("Content-Disposition", 'attachment; filename="' + doc_full_reference + '.pdf"')

# display in browser
else:
  context.REQUEST.RESPONSE.setHeader("Content-Type", "application/pdf;")
  context.REQUEST.RESPONSE.setHeader("Content-Disposition", 'filename="' + doc_full_reference + '.pdf"')
return doc_pdf_file
