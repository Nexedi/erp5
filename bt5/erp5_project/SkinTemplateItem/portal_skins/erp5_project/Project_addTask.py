# Add a task in task_module. 
context_obj = context.getObject()
task = context.task_module.newContent( portal_type = 'Task')

# Set the source_project 
task.setSourceProjectValue(context_obj)

return context.REQUEST.RESPONSE.redirect(task.absolute_url() + '?portal_status_message=Created+Task.')
