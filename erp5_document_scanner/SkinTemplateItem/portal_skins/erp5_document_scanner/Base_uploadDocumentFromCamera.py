from StringIO import StringIO

class StringIOWithFileName(StringIO):
  filename =  "{}.pdf".format(
    kw.get("title") or DateTime().strftime('%d-%m-%Y_%Hh%M'))

portal = context.getPortalObject()
active_process = portal.restrictedTraverse(active_process_url)

pdf_data_list = context.Base_getTempImageList(active_process)
pdf_data = context.ERP5Site_mergePDFList(pdf_data_list=pdf_data_list)
file_object = StringIOWithFileName(pdf_data)

doc = context.Base_contribute(file=file_object,
                              batch_mode=True,
                              redirect_to_document=False,
                              follow_up_list=[context.getRelativeUrl(),],
                              **kw)

publication_state = kw.get("field_your_publication_state")

if publication_state == "shared":
  action_list = ["share",]
elif publication_state == "released":
  action_list = ["share", "release"]
else:
  action_list = []

for action in action_list:
  getattr(doc, action)()

context.Base_removeActiveProcessFromActivityTool(active_process)
