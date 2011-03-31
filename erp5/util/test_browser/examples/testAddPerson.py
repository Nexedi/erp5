#!/usr/bin/env python
# -*- coding: utf-8 -*-

from erp5.utils.test_browser.browser import Browser

ITERATION = 20

def benchmarkAddPerson(iteration_counter, result_dict):
  """
  Benchmark adding a person.
  """
  # Create a browser instance
  browser = Browser('http://localhost:18080/', 'erp5',
                    username='zope', password='zope')

  # Open ERP5 homepage
  browser.open()

  # Go to Persons module (person_module)
  browser.mainForm.submitSelectModule(value='/person_module')

  # Create a new person and record the time elapsed in seconds
  result_dict.setdefault('Create', []).append(
    browser.mainForm.timeSubmitNewInSecond())

  # Check whether it has been successfully created
  assert browser.getTransitionMessage() == 'Object created.'

  # Fill the first and last name of the newly created person
  browser.mainForm.getControl(name='field_my_first_name').value = 'Foo%d' % \
      iteration_counter

  browser.mainForm.getControl(name='field_my_last_name').value = 'Bar%d' % \
      iteration_counter

  # Submit the changes, record the time elapsed in seconds
  result_dict.setdefault('Save', []).append(
    browser.mainForm.timeSubmitSaveInSecond())

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'

  # Validate the person and record confirmation
  browser.mainForm.submitSelectWorkflow(value='validate_action')
  result_dict.setdefault('Validate', []).append(
    browser.mainForm.timeSubmitDialogConfirmInSecond())

  # Check whether it has been successfully validated
  assert browser.getTransitionMessage() == 'Status changed.'


  ## Go to the new person from the Persons module, showing how to use
  ## listbox API
  # Go to Persons module first (person_module)
  browser.mainForm.submitSelectModule(value='/person_module')

  # Select all the persons whose Usual Name starts with Foo
  browser.mainForm.getListboxControl(2, 2).value = 'Foo%'

  result_dict.setdefault('Filter', []).append(
    browser.mainForm.timeSubmitInSecond())

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
