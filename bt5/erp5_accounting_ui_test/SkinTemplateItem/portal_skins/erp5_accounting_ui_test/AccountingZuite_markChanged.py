"""Change the `current_content_script` property on accounting module, 
so that the next test knows that we have modified the test data.
"""
context.getPortalObject().accounting_module.setProperty(
                      'current_content_script', 'modified')
return 'Done.'
