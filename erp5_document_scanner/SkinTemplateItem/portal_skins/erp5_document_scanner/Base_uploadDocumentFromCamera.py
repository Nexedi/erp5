from StringIO import StringIO

class StringIOWithFileName(StringIO):
  filename =  "{}.pdf".format(
    kw.get("title") or DateTime().strftime('%d-%m-%Y_%Hh%M'))


portal = context.getPortalObject()
pdf_data_list = []
image_module = portal.image_module
active_process = portal.restrictedTraverse(active_process_url)

for result in active_process.getResultList():
  pdf_data_list.append(
    image_module.newContent(data=result.detail,
                            portal_type="Image",
                            temp_object=True).convert(format="pdf")[1])

pdf_data = context.ERP5Site_mergePDFList(pdf_data_list=pdf_data_list)
file_object = StringIOWithFileName(pdf_data)

doc = context.Base_contribute(file=file_object,
                              batch_mode=True,
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

portal.portal_activities.manage_delObjects(ids=[active_process.getId(),])
