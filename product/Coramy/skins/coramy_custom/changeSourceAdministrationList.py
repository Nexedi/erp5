## Script (Python) "changeSourceAdministrationList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
order_list = context.changeSourceAdministrationSQL()
i = 1
for order in order_list:


  order_object = order.getObject()
  source_admin = order_object.getSourceAdministration()
  
  if source_admin != 'person/347':
    print order_object.getId(), order_object.getComment()
    i += 1

print 'fin'
return printed
