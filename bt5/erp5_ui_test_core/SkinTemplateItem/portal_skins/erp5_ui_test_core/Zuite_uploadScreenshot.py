"""
  Upload a screenshot taken by the test to ERP5
"""
import base64
data_uri = context.REQUEST.form.get('data_uri', 'default')

image_module = getattr(context, "image_module", None)
if image_module is None:
  return "erp5_dms is not Installed"

image = image_module.getPortalObject().WebSection_getDocumentValue(
                                                   name=image_reference)

if image is None or image.getPortalType() != "Image":
  # Image is an embedded file or not an image
  return "Image: " + str(image_reference) + " not found"

image.setContentType('image/png')
data_text = data_uri.read()
data = base64.b64decode(data_text)

image.edit(data=data,
           filename=str(image_reference) + '.png',
           content_type = 'image/png')

context.Zuite_updateImage(image)
