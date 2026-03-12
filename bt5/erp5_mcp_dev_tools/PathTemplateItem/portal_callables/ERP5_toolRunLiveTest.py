portal = context.getPortalObject()
return portal.portal_components.runLiveTest(
  test_list=test_list,
  run_only=run_only,
  debug=False,
  verbose=True
)
