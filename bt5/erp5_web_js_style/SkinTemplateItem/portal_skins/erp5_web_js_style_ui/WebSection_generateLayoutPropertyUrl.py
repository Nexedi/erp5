web_section = context

layout_property_value = web_section.getLayoutProperty(layout_property, default='')

# If nothing defined, nothing to change
if layout_property_value == '':
  return layout_property_value

relative_url_prefix = web_section.WebSection_generateRelativeUrlPrefix()

if relative_url_prefix and ('/' in layout_property_value):
  raise NotImplementedError('Add correct URL calculation if gadget is not a reference')

return relative_url_prefix + layout_property_value
