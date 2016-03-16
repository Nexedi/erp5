"""Check the tracking history of all items.
"""

item_portal_type_list = context.getProperty('item_portal_type_list')

if item_portal_type_list:
  active_process = context.newActiveProcess().getRelativeUrl()

  context.getPortalObject().portal_catalog.searchAndActivate(
     method_id='Item_checkTrackingList',
     method_kw=dict(fixit=fixit, active_process=active_process),
     activate_kw=dict(tag=tag, priority=5),
     portal_type=item_portal_type_list)
