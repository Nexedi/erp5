resource = context.getResourceValue()

result = []
if include_empty:
  result.append(('',''))

if resource is not None:
  portal = context.getPortalObject()
  kw = {'validation_state': '!=invalidated'} if skip_invalidated else {}
  result.extend((transformation.title, transformation.relative_url)
    for transformation in portal.portal_catalog(
      select_list=('title', 'relative_url'),
      portal_type=portal.getPortalTransformationTypeList(),
      strict_resource_uid=resource.getUid(),
      sort_on=('title', 'relative_url'),
      **kw))

return result
