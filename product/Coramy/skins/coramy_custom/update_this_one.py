## Script (Python) "update_this_one"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
for o in context.objectValues("CORAMY Transformation"):
  print o.id
  for t in o.objectValues("CORAMY Transformed Resource"):
    print t.id
    for c in t.objectValues("ERP5 Set Mapped Value"):
      if c.id[0:8] == 'quantity':
        atr_list = c.getMappedValueAttributeList()
        if len(atr_list) == 0:
          c.setMappedValueAttributeList(['quantity'])
          print c.getRelativeUrl()
      if c.id[0:9] == 'variation':
         var_bc = c.getMappedValueBaseCategoryList()
         if len(var_bc) == 0:
           print c.getRelativeUrl()
           c.setMappedValueBaseCategoryList(t.getResourceDefaultValue().getVariationBaseCategoryList())

return printed
