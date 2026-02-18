portal = context.getPortalObject()
analysis_request = portal.restrictedTraverse(follow_up)
object_list = analysis_request.Base_getRelatedObjectList()

image = None
for item in object_list:
  if item.getPortalType() == "Image":
    image = item

image_as_array = container.DocumentCleaning_convertImageToNumpyArray(image.getData())
## From there, a classification algorithm could be run to figure how the image
## should be treated
text = container.TextRecognition_getReceiptValue(image_as_array)

container.document_analysis_module.newContent(
  follow_up = follow_up,
  extracted_text = text
)
