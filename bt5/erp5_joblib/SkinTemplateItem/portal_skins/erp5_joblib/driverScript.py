import time

from Products.ERP5Type.Log import log

timeout = 10
active_process = context.portal_activities.newActiveProcess()
active_process_id = active_process.getId()
path = active_process.getPhysicalPath()
context.portal_activities.activate(activity="SQLQueue", after_method_id="Base_callSafeFunction", active_process=active_process, tag='abc').Base_joblibFunction(path)
return path
