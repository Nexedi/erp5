'''This script return the list of all groups that is possible to assign the application'''

# XXX we must make filter using informations from the request form

return context.portal_categories.group.getCategoryChildTitleItemList()
