return [(x.getTitle(), x.relative_url) for x in context.getPortalObject().portal_catalog(
  portal_type="Software Product",
  # Is validation state necessary here?
  # validation_state="validated",
  select_list=("relative_url")
  )]
