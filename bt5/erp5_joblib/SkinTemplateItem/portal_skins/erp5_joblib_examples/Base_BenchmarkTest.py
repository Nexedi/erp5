active_process = context.portal_activities.newActiveProcess()
path = active_process.getPhysicalPath()
context.Base_simpleBenchmarkTest(path)
