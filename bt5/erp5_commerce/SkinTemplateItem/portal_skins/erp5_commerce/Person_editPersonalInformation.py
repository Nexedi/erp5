# Only save basic personal information for an ecommerce website
translateString = context.Base_translateString

context.Base_edit(form_id='Person_viewAsWeb')

context.ERP5Site_redirect('%s/account' % context.getWebSiteValue().absolute_url(), \
                          keep_items={'portal_status_message': translateString("Your personal informations are updated.", mapping={})})
