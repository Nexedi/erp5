foo1 = context.foo_module.newContent(portal_type='Foo')
foo2 = context.foo_module.newContent(portal_type='Foo')
foo1.setTitle('hasAccessUnauthorized')
foo1.setSuccessorValue(foo2)

foo1.immediateReindexObject()
foo2.immediateReindexObject()



foo2.activate().manage_permission( 'Access contents information', 'Manager', 0)

return 'Done'
