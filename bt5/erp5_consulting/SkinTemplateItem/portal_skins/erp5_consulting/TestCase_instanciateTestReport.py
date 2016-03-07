test_report = context.getPortalObject().test_report_module.newContent(portal_type = 'Test Report'
  , specialise_value = context
  , title = context.getTitle()
  , description = context.getDescription()
  , requirement_value_list = context.getRequirementValueList()
)

translate_actors = {}

for o in context.contentValues(filter={'portal_type': 'Test Case Actor'}):
  test_report_actor = test_report.newContent(portal_type = 'Test Report Actor'
    , description = o.getDescription()
    , group = o.getGroup()
    , group_free_text = o.getGroupFreeText()
    , int_index = o.getIntIndex()
    , site_free_text = o.getSiteFreeText()
    , title = o.getTitle()
    , use_case_actor_role_list = o.getUseCaseActorRoleList()
    )
  translate_actors[o] = test_report_actor

for o in context.contentValues(filter={'portal_type': 'Test Case Step'}):
  test_report.newContent(portal_type = 'Test Report Step'
    , description = o.getDescription()
    , int_index = o.getIntIndex()
    , requirement_list = o.getRequirementList()
    , title = o.getTitle()
    , source_section_value = translate_actors[o.getSourceSectionValue()]
    )

return context.REQUEST.RESPONSE.redirect("%s?portal_status_message=Test+Report+Created." % (test_report.absolute_url(), ))
