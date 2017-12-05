# -*- coding: utf-8 -*-

TMIN_SLEEP_SHORT = 2
TMAX_SLEEP_SHORT = 6
TMIN_SLEEP = 5
TMAX_SLEEP = 15
TMIN_SLEEP_LONG = 10
TMAX_SLEEP_LONG = 30

def createPerson(result, browser):
  """
  Create a Person with some details.
  """
  # Open ERP5 homepage
  browser.open(sleep=(TMIN_SLEEP_SHORT, TMAX_SLEEP_SHORT))

  # Log in unless already logged in by a previous test suite
  browser.mainForm.submitLogin(sleep=(TMIN_SLEEP_SHORT, TMAX_SLEEP_SHORT))
  
  # Go to Persons module (person_module)
  result('Go to person module',
         browser.mainForm.submitSelectModule(value='/person_module', #value='/erp5/person_module', 
                                             sleep=(TMIN_SLEEP_SHORT, TMAX_SLEEP_SHORT)))

  # Create a new person and record the time elapsed in seconds
  result('Add Person', browser.mainForm.submitNew())

  # Check whether it has been successfully created
  assert browser.getTransitionMessage() == 'Object created.'

  # Fill the first and last name of the newly created person
  browser.mainForm.getControl(name='field_my_first_name').value = 'Create'
  browser.mainForm.getControl(name='field_my_last_name').value = 'Person'

  result('Save', browser.mainForm.submitSave(sleep=(TMIN_SLEEP, TMAX_SLEEP)))

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'
  person_url = browser.url

  # Go back to the Person page before validating
  browser.open(person_url)

  # Validate it (as the workflow action may not be available yet, try 5 times
  # and sleep 5s between each attempts before failing)
  show_validate_time, waiting_for_validate_action = \
      browser.mainForm.submitSelectWorkflow(value='validate_action',
                                            maximum_attempt_number=5,
                                            sleep_between_attempt=5,
                                            sleep=(TMIN_SLEEP_SHORT, TMAX_SLEEP_SHORT))

  result('Waiting for validate_action', waiting_for_validate_action)
  result('Show validate', show_validate_time)
  result('Validated', browser.mainForm.submitDialogConfirm())
  assert browser.getTransitionMessage() == 'Status changed.'
