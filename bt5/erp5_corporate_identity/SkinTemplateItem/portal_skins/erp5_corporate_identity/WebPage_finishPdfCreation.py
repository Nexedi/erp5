"""
================================================================================
Save, download or return generated PDF Document
================================================================================
"""
if doc_save == 1:
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
      file=doc_pdf_file
    )
    
    context.setAggregate(document.getRelativeUrl())
    message = context.Base_translateString(
      '%(portal_type)s created successfully as PDF Document.' % {
        'portal_type': document.getTranslatedPortalType()
      }
    )
    return document.Base_redirect(
      keep_items=dict(portal_status_message=message)
    )
  #XXX else:

# download
elif doc_download == 1:
  context.REQUEST.RESPONSE.setHeader("Content-Type", "application/pdf;")
  context.REQUEST.RESPONSE.setHeader("Content-Disposition", 'attachment; filename="' + doc_full_reference + '.pdf"')

# display in browser
else:
  context.REQUEST.RESPONSE.setHeader("Content-Type", "application/pdf;")
  context.REQUEST.RESPONSE.setHeader("Content-Disposition", 'filename="' + doc_full_reference + '.pdf"')
return doc_pdf_file
