portal = context.getPortalObject()
search_kw = {'portal_type': 'Loyalty Transaction',
             'simulation_state': 'confirmed',
            }
portal.portal_catalog.searchAndActivate(
           method_id='deliver',
           activate_kw={'tag':"deliver_loyalty_transaction", 'priority': 8},
           **search_kw)
