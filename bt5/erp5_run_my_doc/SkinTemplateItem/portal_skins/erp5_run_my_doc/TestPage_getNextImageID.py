"""
  Generate an image name and check if it already exist
"""

path = context.getPath()
image_id = title.lower() + "_" + slide_type.lower()

# We replace all the whitespaces by dots
image_id = ''.join(c for c in ('_'.join(image_id.split(' '))) if c.isalnum() or c == '_')

found = True
while found:
  image_path = path + '/' + image_id
  image = context.restrictedTraverse(image_path, None)
  if image is None:
    found = False
    break
  # If there's already an image with the same url
  if found:
    # Check if the end is a number and increment in that case
    try:
      end_number = int(image_id.split('_')[-1])
    except IndexError:
      end_number = -1
    if end_number > 0:
      image_id = image_id.split('_')[0:-1]
      image_id.append(str(end_number+1))
      image_id = '_'.join(image_id)
    else:
      image_id += '_1'

return image_id
