"""
================================================================================
Upgrade image for the specific type of display
================================================================================
"""
# parameters:
# ------------------------------------------------------------------------------
# img_string                    required, <img src=... />
# img_wrap                      wrap image in a <p> tag and center it
# img_fullscreen_link           wrap image in a link to fullscreen version
# img_caption                   caption to use for this image/alt attribute
# img_svg_format                display image as svg (default png/None)

import re

if img_string is None or img_string == "":
  return img_string

img_src = re.findall("src=['\"](.*?)['\"]", img_string)
if not len(img_src):
  return img_string # There is no image source, return as is
img_src = img_src[0]

if img_src.startswith('data:image/') or img_src.startswith('data:application'):
  return img_string

# START user ignoring guidelines:
new_src = None

# Guideline: no relative links. we cover
if img_src.startswith("./"):
  new_src = img_src.replace("./", "")
  img_string = img_string.replace(img_src, new_src)
  img_src = new_src

# Guideline: include format. we cover
if img_src.find("format=") == -1:
  if img_src.find("?") == -1:
    new_src = img_src + "?format="
  else:
    new_src = img_src + "&amp;format="
  img_string = img_string.replace(img_src, new_src)
  img_src = new_src

# Guideline: images must be stored locally, don't complain if your pdf breaks
if not img_src.lower().startswith("http"):
#END user ignoring guidelines
  if img_src[0] == '/':
    img_src = img_src[1:]

  real_img_src = img_src.split("?")[0]
  img_obj = context.restrictedTraverse(real_img_src, None)

  # flag broken link until further notice
  if img_obj is None:
    return '<p style="color:red">The following image could not be found in erp5 OR is not following guidelines for links (eg no ./ prefix): <span style="font-weight:bold">%s</span></p>' % (real_img_src)

  # img_src = "image_module/3/getData"
  try:
    img_type = img_obj.getContentType()
  except AttributeError:
    real_img_src = '/'.join(real_img_src.split('/')[:-1])
    # img_obj is surely not None
    img_obj = context.restrictedTraverse(real_img_src, None)
    img_type = img_obj.getContentType()

  # ensure alt attributes are set
  if img_string.find('alt=') == -1:
    img_string.replace ("src=", 'alt="%s" src=' % img_caption or img_obj.getTitle())

  # force svg display as svg or png
  if img_type == "image/svg+xml":
    if img_svg_format == "png":
      img_string = img_string.replace('type="image/svg+xml"', '')
      img_string = img_string.replace("type='image/svg+xml'", '')
      img_string = img_string.replace('format=svg', 'format=png')
    elif img_svg_format == "svg":
      img_string = img_string.replace('src=', 'type="image/svg+xml" src=')
      img_string = img_string.replace('src=', "type='image/svg+xml' src=")
      img_string = img_string.replace('format=png', 'format=svg')

  # wrap image in fullscreen link
  if img_fullscreen_link:
    img_string = ''.join([
      '<a target="_blank" rel="noopener noreferrer" href="%s" title="%s">%s<a>' % (
        img_src,
        img_obj.getTitle(),
        img_string
      )
    ])

  # wrap image in <p> tag
  if img_wrap:
    img_string = '<p class="ci-book-img" style="text-align:center">' + img_string + '</p>'

return img_string
