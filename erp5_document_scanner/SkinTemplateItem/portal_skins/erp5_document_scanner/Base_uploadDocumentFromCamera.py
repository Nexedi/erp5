from cStringIO import StringIO

portal = context.getPortalObject()

pdf_data_list = []
image_module = portal.image_module
active_process = portal.restrictedTraverse(active_process_url)

for result in active_process.getResultList():
  pdf_data_list.append(
    image_module.newContent(data=result.detail,
                            temp=True).convert(format="pdf")[1])

pdf_data = context.ERP5Site_mergePDFList(pdf_data_list=pdf_data_list)
file_object = StringIO(pdf_data)

extra_document_kw = {
  "filename": "{}.pdf".format(
    kw.get("title") or DateTime().strftime('%d-%m-%Y_%Hh%M'))
}

return context.Base_contribute(file=file_object,
                               extra_document_kw=extra_document_kw,
                               **kw)
