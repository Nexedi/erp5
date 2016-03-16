obj_len = len(context.objectValues(portal_type=("Task Line", "Task Report Line")))
return (obj_len == 0) or ((obj_len == 1) and context.has_key('default_task_line'))
