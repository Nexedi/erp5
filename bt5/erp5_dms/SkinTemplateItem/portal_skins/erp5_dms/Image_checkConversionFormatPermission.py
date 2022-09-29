# this script has an `format` argument
# pylint: disable=redefined-builtin
if format in ('svg',):
  image_pixels = context.getHeight()* context.getWidth()
  max_pixels = 128*128 # default thumbnail size
  if image_pixels > max_pixels:
    # image is too big to be handled safely by ERP5 as it can lead to
    # really high memory consumptions
    return 0
return 1
