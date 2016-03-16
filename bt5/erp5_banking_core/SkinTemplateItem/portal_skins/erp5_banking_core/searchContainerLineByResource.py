sourceline_list = context.searchFolder(portal_type="Container Line")
if len(sourceline_list) == 0 :
   return None

resource_list = context.portal_catalog(portal_type = ('Banknote','Coin') ,id = resourceId)
resource_list = resource_list[0].getObject().getId()
sourceline_list = [x.getObject() for x in sourceline_list if x.getObject().getResourceId() == resource_list]
if len(sourceline_list) == 0 :
   return None
else:
   return sourceline_list[0]
