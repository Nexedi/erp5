portal_catalog = context.getPortalObject().portal_catalog

source_project_list = portal_catalog(portal_type='Project',
                                     title=dict(query=test_suite,
                                                key='ExactMatch'))
if source_project_list:
  return source_project_list[0].getObject()
