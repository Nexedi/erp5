"""Uninstall business template"""
# Uninstall test business templates before the test
bt_list = context.portal_templates.getInstalledBusinessTemplatesList()
for bt in bt_list:
  if bt.getTitle().startswith('test_'):
    bt.uninstall()

# modify repository list information
if end:
  # set default repository list when test is finished
  repository_list = ['http://www.erp5.org/dists/snapshot/bt5']
else:
  # just used test repository to not display to many bt and thus have listbox
  # with many pages
  repository_list = ['http://www.erp5.org/dists/snapshot/test_bt5']

context.portal_templates.updateRepositoryBusinessTemplateList(repository_list)

return 'Reset Successfully.'
