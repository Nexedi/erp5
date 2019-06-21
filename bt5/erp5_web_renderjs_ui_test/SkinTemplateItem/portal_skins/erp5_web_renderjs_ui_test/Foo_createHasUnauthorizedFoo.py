activity_tag = 'Foo_createHasUnauthorizedFoo'
with context.foo_module.defaultActivateParameterDict({'tag': activity_tag}, placeless=True):
  foo1 = context.foo_module.newContent(portal_type='Foo')
  foo2 = context.foo_module.newContent(portal_type='Foo')
  foo1.setTitle('hasAccessUnauthorized')
  foo1.setSuccessorValue(foo2)

foo2.activate(after_tag=activity_tag).manage_permission('Access contents information', 'Manager', 0)
return 'Done'
