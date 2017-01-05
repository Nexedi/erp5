active_process = context.portal_activities.newActiveProcess()

active_process_id = active_process.getId()
path = active_process.getPhysicalPath()
context.portal_activities.activate(activity="SQLQueue", active_process=active_process).Base_joblibRandomForestFunction(path)
return path
