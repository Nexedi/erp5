from erp5.component.module.Log import log
log('task_list','starting')
task_module = context.getDefaultModule('Task Report')
log('task_list','next1')
task_list = []
if 'parent_uid' not in kw:
  kw['parent_uid'] = task_module.getUid()
log('task_list','next2')
log('context.getPath()',context.getPath())

task_list = [x.getObject() for x in context.portal_catalog(**kw)]
log('task_list',task_list)
#return context.searchFolder(**kw)
return task_list
