# -*- coding: utf-8 -*-
def createPerson(result, browser):
  """
  Create a Person and add a  telephone number.  It can be ran infinitely (e.g.
  until it  is interrupted by  the end user)  with 1 concurrent  user, through
  performance_tester_erp5 with the following command:

  performance_tester_erp5 http://foo.bar:4242/erp5/ 1 createPerson

  Please note that  you must run this command from the  same directory of this
  script  and userInfo.py.  Further information  about performance_tester_erp5
  options and arguments are available by specifying ``--help''.

  This tests requires the bt5 erp5_simulation_performance_test
  to be isntalled for relation with organisation
  """
  # Open ERP5 homepage
  browser.open()

  # Log in unless already logged in by a previous test suite
  browser.mainForm.submitLogin()
  browser.randomSleep(2, 6)
  # Go to Persons module (person_module)
  result('Go to person module',
         browser.mainForm.submitSelectModule(value='/person_module'))
  browser.randomSleep(2, 6)
  # Create a new person and record the time elapsed in seconds
  result('Add Person', browser.mainForm.submitNew())

  # Check whether it has been successfully created
  assert browser.getTransitionMessage() == 'Object created.'

  # Fill the first and last name of the newly created person
  browser.mainForm.getControl(name='field_my_first_name').value = 'Create'
  browser.mainForm.getControl(name='field_my_last_name').value = 'Person'
  # Link to organisation, this will add subobjects
  browser.mainForm.getControl(name='field_my_career_subordination_title').value = 'Supplier'
  browser.randomSleep(5, 15)

  # Submit the changes, record the time elapsed in seconds
  result('Save', browser.mainForm.submitSave())

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'
  person_url = browser.url

  # Add phone number
  browser.randomSleep(2, 6)

  result('Add telephone',
         browser.mainForm.submitSelectAction(value='add Telephone'))

  # Fill telephone title and number
  browser.mainForm.getControl(name='field_my_title'). value = 'Personal'
  browser.mainForm.getControl(name='field_my_telephone_number').value = '0123456789'

  # Submit the changes, record the time elapsed in seconds
  browser.randomSleep(3, 9)

  result('Save', browser.mainForm.submitSave())

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'

  # Go back to the Person page before validating
  browser.open(person_url)

  # Validate it (as the workflow action may not be available yet, try 5 times
  # and sleep 5s between each attempts before failing)
  browser.randomSleep(2, 6)
  show_validate_time, waiting_for_validate_action = \
      browser.mainForm.submitSelectWorkflow(value='validate_action',
                                            maximum_attempt_number=5,
                                            sleep_between_attempt=5)

  result('Waiting for validate_action', waiting_for_validate_action)
  result('Show validate', show_validate_time)
  result('Validated', browser.mainForm.submitDialogConfirm())
  assert browser.getTransitionMessage() == 'Status changed.'
