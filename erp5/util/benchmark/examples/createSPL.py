from six.moves import range
# -*- coding: utf-8 -*-
def createSPL(result, browser):
  """
  Create a Sale Packing List & go until the stopped state
  This tests requires the bt5 erp5_simulation_performance_test
  to be installed & configured
  """
  # Open ERP5 homepage
  browser.open(sleep=(2, 6))

  # Log in unless already logged in by a previous test suite
  browser.mainForm.submitLogin(sleep=(2, 6))

  # Go to SPL module (person_module)
  result('Go to spl module',
         browser.mainForm.submitSelectModule(value='/sale_packing_list_module',
                                             sleep=(2, 6)))

  # Create a new person and record the time elapsed in seconds
  result('Add SPL', browser.mainForm.submitNew())

  # Check whether it has been successfully created
  assert browser.getTransitionMessage() == 'Object created.'

  # Fill the form
  browser.mainForm.getControl(name='field_my_source_section_title').value = 'Supplier'
  browser.mainForm.getControl(name='field_my_source_title').value = 'Supplier'
  browser.mainForm.getControl(name='field_my_source_administration_title').value = 'Supplier'
  browser.mainForm.getControl(name='field_my_price_currency').value = ['currency_module/euro']
  browser.mainForm.getControl(name='field_my_specialise_title').value = 'Test Sale Trade Condition'

  browser.mainForm.getControl(name='field_my_destination_section_title').value= 'Client'
  browser.mainForm.getControl(name='field_my_destination_title').value = "Recipient 1"
  browser.mainForm.getControl(name='field_my_destination_administration_title').value = "Recipient 2"
  browser.mainForm.getControl(name='field_my_comment').value = "Benchmark test"

  # Submit the changes, record the time elapsed in seconds
  result('Save', browser.mainForm.submitSave(sleep=(5, 15)))

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'
  spl_url = browser.url
  spl_url = '/'.join(spl_url.split('/')[:-1])

  # Use fast input
  result("Open fast input", browser.open(spl_url+'/Delivery_checkConsistencyForDeliveryFastInputDialog'))
  for i in range(1,10):
    browser.mainForm.getControl(name='field_listbox_title_new_%s' %(i,)).value = 'Luxury %s' %(i,)
    browser.mainForm.getControl(name='field_listbox_quantity_new_%s' %(i,)).value = '%s' %(i,)
  result("Update fast input", browser.mainForm.submitDialogUpdate(sleep=(10, 30)))
  result("Save fast input", browser.mainForm.submitDialogConfirm(sleep=(3, 9)))
  assert browser.getTransitionMessage() ==   "Sale Packing List Line Created."

  # Go back to the SPL page before validating
  browser.open(spl_url)

  # Confirm it (as the workflow action may not be available yet, try 5 times
  # and sleep 5s between each attempts before failing)
  show_confirm_time, waiting_for_confirm_action = \
      browser.mainForm.submitSelectWorkflow(value='confirm_action',
                                            maximum_attempt_number=5,
                                            sleep_between_attempt=5,
                                            sleep=(2, 6))

  result('Waiting for confirm_action', waiting_for_confirm_action)
  result('Show confirm', show_confirm_time)
  result('Confirmed', browser.mainForm.submitDialogConfirm())
  assert browser.getTransitionMessage() == 'Status changed.'

  # Ship it
  show_start_time, waiting_for_start_action = \
      browser.mainForm.submitSelectWorkflow(value='start_action',
                                            maximum_attempt_number=5,
                                            sleep_between_attempt=5,
                                            sleep=(2, 6))

  result('Waiting for start_action', waiting_for_start_action)
  result('Show start', show_start_time)
  result('Started', browser.mainForm.submitDialogConfirm())

  assert browser.getTransitionMessage() == 'Status changed.'

  # Receive it
  show_stop_time, waiting_for_stop_action = \
      browser.mainForm.submitSelectWorkflow(value='stop_action',
                                            maximum_attempt_number=5,
                                            sleep_between_attempt=5,
                                            sleep=(2, 6))

  result('Waiting for stop_action', waiting_for_stop_action)
  result('Show stop', show_stop_time)
  result('Stopped', browser.mainForm.submitDialogConfirm())

  assert browser.getTransitionMessage() == 'Status changed.'
