# this script has an `format` argument
# pylint: disable=redefined-builtin
"""
  Generic method to handle conversion failures ans still return something to use
  to explain what when wrong, etc.
"""
VALID_IMAGE_FORMAT_LIST = ('jpg', 'jpeg', 'png', 'gif', 'pnm', 'ppm', 'tiff')

# some good defaults
mimetype = "text/plain"
data = "Conversion failure"

if format in VALID_IMAGE_FORMAT_LIST:
  # default image is an OFSImage so even if conversion engine is down
  # we are still able to deliver it
  default_image = getattr(context, "default_conversion_failure_image", None)
  if default_image is not None:
    mimetype = default_image.getContentType()
    data = default_image.index_html(context.REQUEST, context.REQUEST.RESPONSE)

return mimetype, data
