"""
  This script returns all possible projects or tickets
  which can be used a follow up to a CRM event.
"""
type_list = context.getPortalTicketTypeList() + context.getPortalProjectTypeList()
node_list = context.portal_catalog(portal_type=type_list, simulation_state=['draft', 'open', 'validated', 'contacted'])
return map(lambda x:(x.getTitle(), x.getRelativeUrl()), node_list)
