result_list = context.portal_catalog(
  parent_specialise_reference="default_production_rule",
  delivery_uid=None,
  left_join_list=("delivery_uid",),
  select_list=("delivery_uid",),
  group_by=("uid",),
  **kw)
return result_list
