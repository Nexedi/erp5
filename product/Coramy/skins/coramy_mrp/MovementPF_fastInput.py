## Script (Python) "MovementPF_fastInput"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=product_reference_list=[], supplier_list=[]
##title=Add Lines to a movement
##
from Products.Formulator.Errors import ValidationError, FormValidationError

inventory_line_portal_type = "Movement PF Line"
product_list = []
request=context.REQUEST

try:

  if product_reference_list <> '' :
    product_list += product_reference_list

  for line_product in product_list :

    new_id = str(context.generateNewId())
    context.portal_types.constructContent(type_name=inventory_line_portal_type,
                                                            container=context,
                                                            id=new_id)
    resource_list = context.portal_catalog(title=line_product, portal_type=('Modele','Assortiment'), Title=line_product)
    if len(resource_list) > 0:
      resource_value = resource_list[0].getObject()
      if resource_value is not None:

        if resource_value.getPortalType() == 'Modele' :
          my_variation_base_category_list = ['coloris']
        else :
          my_variation_base_category_list = []

        context[new_id].edit(description=line_product ,
                                     resource_value = resource_value,
                                     variation_base_category_list = my_variation_base_category_list )
#        my_variation_category_list = []
#        for category_tuple in context[new_id].getVariationRangeCategoryItemList() :
#          my_variation_category_list.append(category_tuple[0])
#        context[new_id].setVariationCategoryList(my_variation_category_list)
    else:
      context[new_id].edit(description=line_product)
    context.Folder_reindexAll()
except FormValidationError, validation_errors:
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=La+saisie+a+échoué.'
                                  )
else:
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=Data+Updated.'
                                  )

request[ 'RESPONSE' ].redirect( redirect_url )
