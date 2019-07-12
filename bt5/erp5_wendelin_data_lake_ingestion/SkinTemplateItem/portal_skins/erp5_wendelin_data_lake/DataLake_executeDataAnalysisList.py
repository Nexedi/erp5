from Products.ERP5Type.Log import log
portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
complex_files = portal.getIngestionReferenceDictionary()["complex_files_extensions"]

for data_analysis in portal_catalog(portal_type = "Data Analysis",
                                    simulation_state = "planned"):
  try:
    if data_analysis.getSimulationState() == "planned":
      process = True
      complex_file = False
      for ext in complex_files:
        if data_analysis.getReference().endswith(ext):
          complex_file = True
      if complex_file:
        # if server is bussy and file to process is complex, leave for next alarm
        if portal.portal_activities.countMessage() > 50:
          log("There are more than 50 activities running, so leaving data processing of file '%s' for next alarm" % data_analysis.getReference())
          process = False
      if process:
        data_analysis.start()
        data_analysis.activate(serialization_tag=str(data_analysis.getUid()))\
          .DataLake_executeDataOperation()
  except Exception as e:
    context.logEntry("[ERROR] Error executing Data Analysis for '%s': %s" % (data_analysis.getId(), str(e)))
