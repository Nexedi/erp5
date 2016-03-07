"""
Return the amount of valid created documents
"""
portal = context.getPortalObject()

person_len = len(portal.person_module.searchFolder(validation_state='validated'))
sale_order_len = len(portal.sale_order_module.searchFolder(simulation_state='planned'))
web_page_len = len(portal.web_page_module.searchFolder(validation_state='submitted'))

return person_len + sale_order_len + web_page_len
