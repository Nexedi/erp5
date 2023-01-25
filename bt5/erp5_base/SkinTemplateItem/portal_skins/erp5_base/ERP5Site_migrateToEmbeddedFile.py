"""
  This script when triggered will migrate all embedded "File" and "Image"
  objects to an unified "Embedded File".
"""
active_process = context.getPortalObject().portal_activities.newActiveProcess()
context.ERP5Site_checkDataWithScript("Base_migrateToEmbeddedFile",
                                     tag="migrate",
                                     active_process=active_process.getPath(),
                                     method_kw=dict(force=1))

print "Migration started with process id: %s" %active_process.getPath()
return printed
