# -*- coding: utf-8 -*-
def createWebPage(result, browser):
  """
  Create a minimal web page with some content & submit it

  Note : you need your user to have Assignor role to do workflow transition
  """
  # Open ERP5 homepage
  browser.open()

  # Log in unless already logged in by a previous test suite
  browser.mainForm.submitLogin()
  browser.randomSleep(2, 6)
  # Go to WebPage module (person_module)
  result('Go to Web Page module',
         browser.mainForm.submitSelectModule(value='/web_page_module'))
  browser.randomSleep(2, 6)
  # Create a new person and record the time elapsed in seconds
  result('Add Web Page', browser.mainForm.submitNew())

  # Check whether it has been successfully created
  assert browser.getTransitionMessage() == 'Object created.'

  # Fill the form
  browser.mainForm.getControl(name='field_my_title').value = 'Web Page Bench'
  browser.mainForm.getControl(name='field_my_short_title').value = 'test'
  browser.mainForm.getControl(name='field_my_reference').value = '001'
  browser.mainForm.getControl(name='field_my_version').value = "001"
  browser.mainForm.getControl(name='field_my_language').value = 'en'
  browser.mainForm.getControl(name='field_my_int_index').value = '10'
  browser.mainForm.getControl(name='field_my_description').value= 'Benchmark test'
  browser.randomSleep(5, 15)
  # Submit the changes, record the time elapsed in seconds
  result('Save', browser.mainForm.submitSave())

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'
  WebPage_url = browser.url

  # Edit content
  WebPage_url = '/'.join(WebPage_url.split('/')[:-1])
  browser.open(WebPage_url+"/WebPage_viewEditor")
  browser.mainForm.getControl(name='field_my_text_content'). value = '<html><body><h1>Test</h1><p>Content if test</p></body></html>'
  # Submit the changes, record the time elapsed in seconds
  browser.randomSleep(10, 30)
  result('Save', browser.mainForm.submitSave())

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'

  # Publish it
  browser.randomSleep(2, 6)
  show_publish_time, waiting_for_publish_action = \
      browser.mainForm.submitSelectWorkflow(value='publish_action',
                                            maximum_attempt_number=5,
                                            sleep_between_attempt=5)

  result('Waiting for publish_action', waiting_for_publish_action)
  result('Show publish', show_publish_time)
  result('Published', browser.mainForm.submit(name='Base_callDialogMethod:method'))

  assert browser.getTransitionMessage() == 'Status changed.'


