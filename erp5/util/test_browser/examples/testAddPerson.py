#!/usr/bin/env python
# -*- coding: utf-8 -*-

from erp5.utils.test_browser.browser import Browser

ITERATION = 20

def benchmarkAddPerson(result_dict):
  """
  Benchmark adding a person
  """
  # Create a browser instance
  browser = Browser('http://localhost:18080/', 'erp5',
                    username='zope', password='zope')

  # Open ERP5 homepage
  browser.open()

  # Go to Persons module (person_module)
  browser.mainForm.submitSelectModule(label='Persons')

  # Create a new person and record the time elapsed in seconds
  result_dict.setdefault('Create new person', []).append(
    browser.mainForm.timeSubmitNewInSecond())

  # Check whether it has been successfully created
  assert browser.getTransitionMessage() == 'Object created.'

  # Fill the first and last name of the newly created person
  browser.mainForm.getControl(name='field_my_first_name').value = 'Foo'
  browser.mainForm.getControl(name='field_my_last_name').value = 'Bar'

  # Submit the changes, record the time elapsed in seconds
  result_dict.setdefault('Save', []).append(
    browser.mainForm.timeSubmitSaveInSecond())

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'

  # Validate the person and record confirmation
  browser.mainForm.submitSelectWorkflow(label='Validate')
  result_dict.setdefault('Validate', []).append(
    browser.mainForm.timeSubmitDialogConfirmInSecond())

  # Check whether it has been successfully validated
  assert browser.getTransitionMessage() == 'Status changed.'

if __name__ == '__main__':
  # Run benchmarkAddPerson ITERATION times and compute the average time it
  # took for each operation
  result_dict = {}
  counter = 0
  while counter != ITERATION:
    benchmarkAddPerson(result_dict)
    counter += 1

  for title, time_list in result_dict.iteritems():
    print "Average: %s: %.4fs" % (title, float(sum(time_list)) / ITERATION)
