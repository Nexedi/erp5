portal = context.getPortalObject()

portal.portal_catalog.searchAndActivate(
  portal_type='Artificial Task',
  simulation_state='started',
  method_id="ArtificialTask_runHarnessAgent",
  activate_kw={
    'tag':tag,
    'priority': 8
  }
)

context.activate(after_tag=tag).getId()
