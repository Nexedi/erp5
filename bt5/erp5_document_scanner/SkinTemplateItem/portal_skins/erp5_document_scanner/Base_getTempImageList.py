"""
  Proxy role as Manager is required here to access getResultList
"""
from base64 import b64decode
if REQUEST:
  return RuntimeError("You cannot run this script in the url")

image_module = context.getPortalObject().image_module
pdf_data_list = []

for result in active_process.getResultList():
  if result.reference in image_list:
    pdf_data_list.append(
      image_module.newContent(data=b64decode(result.detail),
                              portal_type="Image",
                              temp_object=True).convert(format="pdf")[1])

return pdf_data_list
