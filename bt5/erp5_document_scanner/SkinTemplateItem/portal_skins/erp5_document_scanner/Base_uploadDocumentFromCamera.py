from StringIO import StringIO

class StringIOWithFileName(StringIO):
  filename =  "{}.pdf".format(
    kw.get("title") or DateTime().strftime('%d-%m-%Y_%Hh%M'))

portal = context.getPortalObject()
active_process = portal.restrictedTraverse(str(active_process_url))

pdf_data_list = context.Base_getTempImageList(active_process, image_list)
pdf_data = context.ERP5Site_mergePDFList(pdf_data_list=pdf_data_list)
file_object = StringIOWithFileName(pdf_data)

context.Base_contribute(
    file=file_object,
    batch_mode=True,
    redirect_to_document=False,
    follow_up_list=[context.getRelativeUrl(),],
    publication_state=publication_state,
    **kw)
