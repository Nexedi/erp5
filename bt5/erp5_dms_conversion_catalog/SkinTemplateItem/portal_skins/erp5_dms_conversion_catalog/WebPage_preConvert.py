"""
  Do actual conversion of Web Page. As it involves cloudoo use serialization tag and activity.
"""
portal = context.getPortalObject()

format_kw = {'format': format,
            'quality': quality}
for display in display_list:
  format_kw['display'] = display
  context.activate(activity='SQLDict', serialization_tag='pre_convert').convert(**format_kw)

# try to convert all relative referenced (i.e. by <img> tag) documents
context.activate(activity='SQLDict').WebPage_preConvertReferencedImageList(**format_kw)
