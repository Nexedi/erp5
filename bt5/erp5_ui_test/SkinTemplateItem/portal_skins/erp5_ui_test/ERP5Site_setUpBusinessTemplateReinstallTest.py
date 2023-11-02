"""Installs test_core and make local change, so that later we can reinstall
and see that our local changes are gone.
"""
portal = context.getPortalObject()
portal.portal_templates.installBusinessTemplateListFromRepository(['test_core'])
bt = portal.portal_templates.getInstalledBusinessTemplate('test_core')

portal.portal_skins.erp5_test.test_file.manage_edit(
  title='',
  content_type='text/plain',
  filedata='modified !'
)

return bt.Base_redirect('view', keep_items={'portal_status_message': 'Setup OK'})
