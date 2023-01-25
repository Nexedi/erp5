result = []
if include_empty :
  result = [['', ''],]

om = getattr(context.getPortalObject(),'organisation_module')

lst=[o for o in om.objectValues() if 'group/usk' in o.getCategoryList()]

for u in lst :
  result.append((u.getTitle(), u.getRelativeUrl()))
return result
