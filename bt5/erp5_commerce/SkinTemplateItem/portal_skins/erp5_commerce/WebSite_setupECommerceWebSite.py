translateString = context.Base_translateString

if (context.getPortalType() != 'Web Site'):
  context.Base_redirect('', keep_items={
   'portal_status_message': translateString("You can only launch this script on a web site.", mapping={})
                                       })

# creation the default sections
object_id_list = ['cart', 'account', 'register']
for id in object_id_list:
  if id in context.objectIds():
    context.manage_delObjects([id])

cart_section = context.newContent(portal_type='Web Section', title='Cart', id='cart')
account_section = context.newContent(portal_type='Web Section', title='My account', id='account')
register_section = context.newContent(portal_type='Web Section', title='Register', id='register')
checkout_section = context.newContent(portal_type='Web Section', title='Checkout', id='checkout')

# make some visible by default
cart_section.setVisible(True)

# setup site properties
context.setContainerLayout('erp5_web_multiflex5_commerce_layout')
context.setLayoutConfigurationFormId('WebSection_viewMultiflex5Configuration')
context.setProperty('layout_right_column', True)
context.setSiteMapSectionParent(True)
context.setContentLayout(None)
context.setProperty('layout_additional_css', 'mf54_commerce.css')

# setup default render method
cart_section.setCustomRenderMethodId('SaleOrder_viewAsWeb')
cart_section.setProperty('ecommerce_default_content', True)
cart_section.setProperty('ecommerce_product_list', False)
account_section.setCustomRenderMethodId('WebSection_viewCurrentPersonAsWeb')
account_section.setProperty('ecommerce_default_content', True)
account_section.setProperty('ecommerce_product_list', False)
register_section.setCustomRenderMethodId('WebSite_viewRegistrationDialog')
register_section.setProperty('ecommerce_default_content', True)
register_section.setProperty('ecommerce_product_list', False)
checkout_section.setCustomRenderMethodId('SaleOrder_viewConfirmAsWeb')
checkout_section.setProperty('ecommerce_default_content', True)
checkout_section.setProperty('ecommerce_product_list', False)

context.Base_redirect('', keep_items={
   'portal_status_message': translateString("Your web site is now an ecommerce plateform.", mapping={})
                                       })
