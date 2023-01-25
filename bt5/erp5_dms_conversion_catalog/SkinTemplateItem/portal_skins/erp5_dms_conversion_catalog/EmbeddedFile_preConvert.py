"""
  Embedded file can be an Image of a File so it needs special
  handling  base on content type.
"""
if 'image' in context.getContentType():
  return context.Image_preConvert(format=format,
                                  quality=quality,
                                  display_list = display_list)
