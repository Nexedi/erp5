r = ''

software_product = context.getFollowUpValue(portal_type='Software Product')
if software_product:
  r = software_product.getProductLineTitle('') + ' ' + software_product.getDescription('') + software_product.getTitle('')
return r
