if reset:
  value = dict(selection_name='')
else:
  value = dict(selection_name='python: "foo_selection" if here.getPortalType()=="Foo Module" else "wrong_selection"')
context.getPortalObject().foo_module.FooModule_viewFooList.listbox.manage_tales_xmlrpc(value)
return 'ok'
