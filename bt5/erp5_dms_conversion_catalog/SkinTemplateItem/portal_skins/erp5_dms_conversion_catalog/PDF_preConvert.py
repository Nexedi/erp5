"""
  Do actual conversion of PDF documents.
  As such documents contains frames do convert them too.
"""

portal = context.getPortalObject()

format_kw = {'format': format,
             'quality': quality}

# only PDF uses large images in its navigation
if 'large' not in display_list:
  display_list.append('large')

# support frames
frames = int(context.getContentInformation().get('Pages', 0))
if frames==0:
  frame_list = [0]
else:
  frame_list = range(0, frames)

for frame in frame_list:
  format_kw['frame'] = frame
  for display in display_list:
    format_kw['display'] = display
    if context.checkConversionFormatPermission(**format_kw):
      # in some rare cases especially with PDF some very large files are denied to be converted
      # as this check happens in convert as well do not allow to be raised there and stop if
      # required processing here
      context.convert(**format_kw)
