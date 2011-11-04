#!/usr/bin/env python
# -*- coding: utf-8 -*-

from erp5.util.testbrowser.browser import Browser

ITERATION = 20

def benchmarkAddPerson(iteration_counter, result_dict):
  """
  Benchmark adding a person.
  """
  # Create a browser instance
  browser = Browser('http://localhost:18080/', 'erp5',
                    username='zope', password='zope')

  # Open ERP5 homepage and log in
  browser.open()
  browser.mainForm.submitLogin()

  # Go to Persons module (person_module)
  browser.mainForm.submitSelectModule(value='/person_module')

  # Create a new person and record the time elapsed in seconds
  result_dict.setdefault('Create', []).append(
    browser.mainForm.submitNew())

  # Check whether it has been successfully created
  assert browser.getTransitionMessage() == 'Object created.'

  # Fill the first and last name of the newly created person
  browser.mainForm.getControl(name='field_my_first_name').value = 'Foo%d' % \
      iteration_counter

  browser.mainForm.getControl(name='field_my_last_name').value = 'Bar%d' % \
      iteration_counter

  # Submit the changes, record the time elapsed in seconds
  result_dict.setdefault('Save', []).append(
    browser.mainForm.submitSave())

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'

  # Validate the person (as the workflow action may not be available yet, try
  # 5 times and sleep 5s between each attempts before failing) and record
  # time spent on confirmation
  browser.mainForm.submitSelectWorkflow(value='validate_action',
                                        maximum_attempt_number=5,
                                        sleep_between_attempt=5)
  result_dict.setdefault('Validate', []).append(
    browser.mainForm.submitDialogConfirm())

  # Check whether it has been successfully validated
  assert browser.getTransitionMessage() == 'Status changed.'


  ## Go to the new person from the Persons module, showing how to use
  ## listbox API
  # Go to Persons module first (person_module)
  browser.mainForm.submitSelectModule(value='/person_module')

  # Select all the persons whose Usual Name starts with Foo
  browser.mainForm.getListboxControl(2, 2).value = 'Foo%'

  result_dict.setdefault('Filter', []).append(
    browser.mainForm.submit())

  # Get the line number
  line_number = browser.getListboxPosition("Foo%(counter)d Bar%(counter)d" % \
                                             {'counter': iteration_counter},
                                           column_number=2)

  # From the column and line_number, we can now get the Link instance
  link = browser.getListboxLink(line_number=line_number, column_number=2)

  # Click on the link
  link.click()

  assert browser.mainForm.getControl(name='field_my_first_name').value == \
      'Foo%d' % iteration_counter

if __name__ == '__main__':
  # Run benchmarkAddPerson ITERATION times and compute the average time it
  # took for each operation
  result_dict = {}
  counter = 0
  while counter != ITERATION:
    benchmarkAddPerson(counter, result_dict)
    counter += 1

  for title, time_list in result_dict.iteritems():
    print "%s: %.4fs" % (title, float(sum(time_list)) / ITERATION)
