## Script (Python) "testrc"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.setSourceAdministration('person/347')
return 'Done'


# set the source administration
local_user = context.portal_membership.getAuthenticatedMember()
local_user_name = string.replace(local_user.getUserName(), '_', ' ')
local_persons = context.item_by_title_sql_search(title = local_user_name, portal_type = 'Person')
if len(local_persons) > 0:
  print local_user.getUserName()
  print local_persons[0].relative_url
else:
  print 'couscous'
return printed


#
context.activate().buildDeliveryList()
return "Done"


"""
summary = context.getAggregatedAmountList()
#amount = summary[0]
#print amount['converted_quantity'], amount['efficiency']
print 'fin'
return printed
"""
"""
print float(context.getLaizeUtile())
return printed
"""
