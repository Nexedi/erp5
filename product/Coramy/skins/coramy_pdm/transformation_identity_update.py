## Script (Python) "transformation_identity_update"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id
##title=
##
l_items = context.getVLineItemList()
l_items = map(lambda x: x[0], l_items)
l_id = context.getVariationBaseCategoryLine()
c_items = context.getVColumnItemList()
c_items = map(lambda x: x[0], c_items)
c_id = context.getVariationBaseCategoryColumn()
t_items = context.getVTabItemList()
t_items = map(lambda x: x[0], c_items)

request = context.REQUEST

# We must still inlude the tab variations

for i in l_items:
  for j in c_items:
    cell = context.newCell(i, j, base_id='variation')
    cell.setCategoryMembership([l_id,c_id] + list(context.getVariationBaseCategoryList()) ,
               [i,j] + list(context.getVariationCategoryList()))

# Required to set Mapped Value Parameters
# This is a bit simple but it works
# Another method consists in setting by hand each cell, but that is a bit
# like repeating the same code again and again
context.fixConsistency()

redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Variation+Updated.'
                              )
return request[ 'RESPONSE' ].redirect( redirect_url )
