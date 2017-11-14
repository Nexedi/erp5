"""
================================================================================
Upgrade image for the specific type of display
================================================================================
"""
import re

img_src = re.findall("src=['\"](.*?)['\"]", img_string)[0]
img_obj = context.restrictedTraverse(img_src.split("?")[0])
img_type = img_obj.getContentType()

# XXX flag broken link
# if img_obj is None:

# ensure alt attributes are set
if img_string.find('alt=') == -1:
  img_string.replace ("src=", 'alt="%s" src=' % img_obj.getTitle())

# force svg display as svg or png
if img_type == "image/svg+xml":
  if img_svg_format == "png":
    img_string = img_string.replace('type="image/svg+xml"', '')
    img_string = img_string.replace("type='image/svg+xml'", '')
    img_string = img_string.replace('format=svg', 'format=png')
  if img_svg_format == "svg":
    img_string = img_string.replace('src=', 'type="image/svg+xml" src=')
    img_string = img_string.replace('src=', "type='image/svg+xml' src=")
    img_string = img_string.replace('format=png', 'format=svg')

# wrap image in link
if img_wrap:
  img_string = ''.join([
    '<a target="_blank" rel="noopener noreferrer" href="%s" title="%s">%s<a>' % (
      img_src,
      img_obj.getTitle(),
      img_string
    )
  ])

return img_string
