# this script has an `format` argument
# pylint: disable=redefined-builtin
from erp5.component.document.Document import VALID_IMAGE_FORMAT_LIST

if format in VALID_IMAGE_FORMAT_LIST:
  # we do not have any data so we can allow conversion to proceed and lead to a
  # different conversion errorrather than raise Unautorized
  if not context.hasData():
    return True

  # Check if PDF size is not too large for conversion tool
  content_information = context.getContentInformation()
  size = content_information.get('Page size')
  if not size:
    # If we can not extract the size,
    # We do not take any risk and disallow conversion
    return False

  width = float(size.split(' ')[0])
  height = float(size.split(' ')[2])
  # The default resolution is 72 dots per inch,
  # which is equivalent to one point per pixel (Macintosh and Postscript standard)

  # Max surface allowed to convert an image,
  # value is surface of A3 (11.7 inchs * 72 dpi * 16.5 inchs * 72 dpi)
  maximum_surface = 1000772

  if (width * height) > maximum_surface:
    return False

return True
