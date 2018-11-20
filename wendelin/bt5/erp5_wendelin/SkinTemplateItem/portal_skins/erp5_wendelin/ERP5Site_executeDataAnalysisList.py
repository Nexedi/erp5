portal = context.getPortalObject()

#search_kw = {
#  'simulation_state': 'started',
#  'portal_type': 'Data Analysis',
#}

#method_kw = {
#  'active_process': this_portal_type_active_process,
#}

#activate_kw = {
#  'tag': tag,
#  'priority': priority,
#}

#portal.portal_catalog.searchAndActivate(
#  method_id='DataAnalysis_executeDataOperation',
#  method_kw=method_kw,
#  activate_kw=activate_kw,
#  **search_kw)

for data_analysis in portal.portal_catalog(portal_type = "Data Analysis",
                                           simulation_state = "started"):
  if not data_analysis.hasActivity():
    if data_analysis.getRefreshState() == "current":
      data_analysis.activate(serialization_tag=str(data_analysis.getUid()))\
        .DataAnalysis_executeDataOperation()

for data_analysis in portal.portal_catalog(portal_type = "Data Analysis",
                                           refresh_state = "refresh_planned"):
  if data_analysis.getRefreshState() == "refresh_planned":
    if not data_analysis.hasActivity():
      data_analysis.activate(serialization_tag=str(data_analysis.getUid()))\
        .DataAnalysis_clearAndReprocessFromScratch()
