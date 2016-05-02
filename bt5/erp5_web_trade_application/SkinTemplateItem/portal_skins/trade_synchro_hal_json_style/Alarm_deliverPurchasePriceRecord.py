portal = context.getPortalObject()

portal.portal_catalog.searchAndActivate(
      portal_type="Purchase Price Record", 
      simulation_state="stopped",
      method_id='PurchasePriceRecord_deliverIfTicketIsClosed',
      activate_kw={'tag': tag}
      )
context.activate(after_tag=tag).getId()
