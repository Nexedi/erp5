"""
  Do actual conversion of any Image type.
"""
if quality is None:
  # it's required so fall back to system preferences as
  # directly accessed over URL will do the same
  quality = context.getDefaultImageQuality(format)

if not context.getContentType("").startswith('image/'):
  context.log('Image_preConvert', '%s is not an image, skipping preconversion' % context.getRelativeUrl())
  return

# UI uses 'large' display
display_list.append('large')
# Usually links in web page contain image as <img src="url?format=png"> without display
display_list.append(None)

context.Base_preConvert(format, quality, display_list)
