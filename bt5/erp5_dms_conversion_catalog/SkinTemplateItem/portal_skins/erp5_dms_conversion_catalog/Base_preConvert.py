"""
  Do actual conversion of any Base type.
"""
portal = context.getPortalObject()

format_kw = {'format': format,
            'quality': quality}

for display in display_list:
  format_kw['display'] = display
  if display is None:
    format_kw.pop('display')
  context.convert(**format_kw)
