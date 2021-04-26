from Products.ERP5Type.Document import newTempBase
portal = context.getPortalObject()
getobject = portal.portal_catalog.getobject
request = context.REQUEST
integration_site = context
result = []
line_list = context.getCategoryMappingChildValueList()
len_line_list = len(line_list)
if len_line_list!=0:
  for line in line_list:
    container = integration_site
    parent = line.getParentValue()
    if line.getPortalType() == "Integration Category Mapping" and parent is not None:
      container = parent
    obj=container.newContent(portal_type=line.getPortalType(),
                          id= "%s" % "_".join(line.getRelativeUrl().split("/")[2:]),
                          uid="new_%s" % "_".join(line.getRelativeUrl().split("/")[2:]),
                          temp_object=1,
                          is_indexable=0,)
    obj.edit(source_reference=line.getSourceReference(),
          destination_reference=line.getDestinationReference())
    result.append(obj)
return result
