"""
  Launch Test Embedded at the Test Page.
"""
reference = context.getReference()
if reference not in [None, '']:
  zuite_id = reference

test_script = getattr(context, 'Zuite_createAndLaunchSeleniumTest', None)
if test_script is None:
  raise ValueError("Unable to Launch the Test. Please install erp5_ui_test_core business template.")

return test_script(test_list=((context.TestPage_viewSeleniumTest(),context.getTitle()),),
                   zuite_id=zuite_id)
