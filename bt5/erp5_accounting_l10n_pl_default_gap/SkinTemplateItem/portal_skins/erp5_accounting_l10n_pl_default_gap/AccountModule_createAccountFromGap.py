"""
Deployment script for crating initial accounts upon gap/pl/default structure
Warning: Before using this script as zope, edit account_workflow and give Manager permission to validate_action
"""

#This script will REMOVE any existing accounts!!!
#comment following if you are sure
print('Nothing done!')
return printed



gap_root = context.getPortalObject().portal_categories.gap.pl.default
account_module = context.getPortalObject().account_module
account_module.manage_delObjects(ids=[a.getId() for a in account_module.contentValues()])


for category in gap_root.getCategoryMemberValueList():
  category = category.getObject()
  if len(category.contentValues())==0:
    #jest lisciem
    acc = account_module.newContent(title='%s %s' % (category.getId(),category.getTitle()),\
                             gap_value = category)
    acc.validate()
    print('acc created')


return printed
