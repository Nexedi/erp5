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
  """
  # Go to Persons module (person_module)
  result('Go to person module',
         browser.mainForm.submitSelectModule(value='/person_module'))

  # Create a new person and record the time elapsed in seconds
  result('Add Person', browser.mainForm.submitNew())

  # Check whether it has been successfully created
  assert browser.getTransitionMessage() == 'Object created.'

  # Fill the first and last name of the newly created person
  browser.mainForm.getControl(name='field_my_first_name').value = 'Create'
  browser.mainForm.getControl(name='field_my_last_name').value = 'Person'

  # Submit the changes, record the time elapsed in seconds
  result('Save', browser.mainForm.submitSave())

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'

  # Add phone number
  result('Add telephone',
         browser.mainForm.submitSelectAction(value='add Telephone'))

  # Fill telephone title and number
  browser.mainForm.getControl(name='field_my_title'). value = 'Personal'
  browser.mainForm.getControl(name='field_my_telephone_number').value = '0123456789'

  # Submit the changes, record the time elapsed in seconds
  result('Save', browser.mainForm.submitSave())

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'

  # Validate it
  result('Validate', browser.mainForm.submitSelectWorkflow(value='validate_action'))
  result('Validated', browser.mainForm.submitDialogConfirm())
  assert browser.getTransitionMessage() == 'Status changed.'
