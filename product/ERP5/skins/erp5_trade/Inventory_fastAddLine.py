## Script (Python) "Inventory_fastAddLine"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=fast_input
##title=Add Lines to an Inventory
##
from Products.Formulator.Errors import ValidationError, FormValidationError

request=context.REQUEST

try:
  for line in fast_input:
    line_items = line.split()
    if len(line_items) > 1:
      # Product and quantity
      line_product = ' '.join(line_items[0:-1])
      line_quantity = line_items[-1]
    else:
      # Product 
      line_product = line
    new_id = str(context.generateNewId())
    context.portal_types.constructContent(type_name="Inventory Line",
                                                            container=context,
                                                            id=new_id)
    resource_list = context.portal_catalog(title=line_product, portal_type='Product', Title=line_product)
    if len(resource_list) > 0:
      resource_value = resource_list[0].getObject()
      if resource_value is not None:
        context[new_id].edit(inventory=line_quantity ,
                                     description=line_product ,
                                     resource_value = resource_value)
    else:
      context[new_id].edit( inventory=line_quantity ,
                                     description=line_product ,
                                                           )
except FormValidationError, validation_errors:
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=Failed+Fast+Input.'
                                  )
else:
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=Data+Updated.'
                                  )

request[ 'RESPONSE' ].redirect( redirect_url )
