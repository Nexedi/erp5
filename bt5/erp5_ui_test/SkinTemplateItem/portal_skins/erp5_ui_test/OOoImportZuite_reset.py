"""
    Reset all datas
"""
module = context.getPortalObject().foo_module

dummy_foo_list = module.contentValues(portal_type = 'Foo')

for foo in dummy_foo_list:
  module.manage_delObjects(foo.getId())

return "Reset Successfully."
