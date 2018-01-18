"""Change the `current_content_script` property on accounting module, 
so that the next test knows that we have modified the test data.

XXX Kato: This is seriously wrong because test must not suppose anything
          about the other tests - especially that they did not modify the data.
"""
context.getPortalObject().accounting_module.setProperty(
                      'current_content_script', 'modified')
return 'Done.'
