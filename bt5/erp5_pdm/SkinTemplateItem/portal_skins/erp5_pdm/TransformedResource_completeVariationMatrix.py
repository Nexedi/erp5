request = context.REQUEST

cell_key_list = context.getCellKeyList( base_id = 'variation')

for cell_key in cell_key_list:
  
  # If cell exists, do not modify it
  if not context.hasCell(base_id='variation', *cell_key ):

    cell = context.newCell(base_id='variation', *cell_key)
    cell.setCategoryList( context.getVariationCategoryList() )
    cell.setMembershipCriterionCategoryList( cell_key )
    cell.setMembershipCriterionBaseCategoryList( context.getVVariationBaseCategoryList() )
          
redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Variation+matrix++updated.'
)
return request[ 'RESPONSE' ].redirect( redirect_url )
