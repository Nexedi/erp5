portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

for data_analysis in portal_catalog(portal_type = "Data Analysis",
                                    simulation_state = "planned"):
  data_analysis.start()
  data_analysis.activate(serialization_tag=str(data_analysis.getUid()))\
    .DataAnalysis_executeDataOperation()
