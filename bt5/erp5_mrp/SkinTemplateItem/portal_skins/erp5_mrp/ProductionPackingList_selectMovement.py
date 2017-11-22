return context.portal_catalog(
  explanation_portal_type="Production Order",
  parent_specialise_portal_type="Delivery Simulation Rule",
  delivery_uid=None,
  left_join_list=("delivery_uid",),
  select_list=("delivery_uid",),
  group_by=("uid",),
  **kw)
