"""
  This script returns all possible projects or tickets
  which can be used a follow up to a CRM event.
"""
portal = context.getPortalObject()
type_list = portal.getPortalTicketTypeList() + portal.getPortalProjectTypeList()
node_list = portal.portal_catalog(portal_type=type_list, simulation_state=['draft', 'open', 'validated', 'contacted'])
return [(x.getTitle(), x.getRelativeUrl) for x in node_list]
