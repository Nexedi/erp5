# -*- coding: utf-8 -*-

import datetime
import random
import time
import string
from utils import *

PREFIX_TITLE = ""

TMIN_SLEEP_SHORT = 1
TMAX_SLEEP_SHORT = 3
TMIN_SLEEP = 2
TMAX_SLEEP = 6
TMIN_SLEEP_LONG = 4
TMAX_SLEEP_LONG = 8
NUMMAX_FOLLOW_UP = 1
NUMMAX_CONTRIBUTORS = 1

def createWebPage(result, browser):
  """
  Create a minimal web page with some content & submit it

  Note : you need your user to have Assignor role to do workflow transition
  you must select the source code editor (plain text) on the preference
  """
  # Open ERP5 homepage
  browser.open(sleep=(TMIN_SLEEP_SHORT, TMAX_SLEEP_SHORT))
 
  # Log in unless already logged in by a previous test suite
  browser.mainForm.submitLogin(sleep=(TMIN_SLEEP_SHORT, TMAX_SLEEP_SHORT))

  # Go to WebPage module (person_module)
  result('Go to Web Page module',
         browser.mainForm.submitSelectModule(value='/web_page_module',
                                             sleep=(TMIN_SLEEP_SHORT, TMAX_SLEEP_SHORT)))

  # Create a new person and record the time elapsed in seconds
  result('Add Web Page', browser.mainForm.submitNew())

  # Check whether it has been successfully created
  assert browser.getTransitionMessage() == 'Object created.'

  # Fill the form
  browser.mainForm.getControl(name='field_my_title').value = PREFIX_TITLE+'Web Page Bench'
  browser.mainForm.getControl(name='field_my_short_title').value = 'test'
  browser.mainForm.getControl(name='field_my_reference').value = '001'
  browser.mainForm.getControl(name='field_my_version').value = "001"
  browser.mainForm.getControl(name='field_my_language').value = 'en'
  browser.mainForm.getControl(name='field_my_int_index').value = '10'
  date = datetime.datetime.now()
  browser.mainForm.getControl(name='subfield_field_my_effective_date_day').value = str(date.day)
  browser.mainForm.getControl(name='subfield_field_my_effective_date_month').value = str(date.month)
  browser.mainForm.getControl(name='subfield_field_my_effective_date_year').value = str(date.year)
  selectRandomOption(browser, "subfield_field_my_publication_section_list_default:list")
  browser.mainForm.getControl(name='field_my_description').value = 'Benchmark test'
  selectRandomOption(browser, "subfield_field_my_group_list_default:list")
  selectRandomOption(browser, "subfield_field_my_site_list_default:list")
  selectRandomOption(browser, "subfield_field_my_function_list_default:list")
  browser.mainForm.getControl(name='field_my_subject_list').value = generateString(30)
 
  
  ## Fill the Follow-up input
  fillRelatedObjects(browser, result,
      "portal_selections/viewSearchRelatedDocumentDialog0:method", NUMMAX_FOLLOW_UP,
               "FollowUp", TMIN_SLEEP_SHORT, TMAX_SLEEP_SHORT)                                        
  
  # Submit the changes, record the time elapsed in seconds
  result('Save', browser.mainForm.submitSave(sleep=(TMIN_SLEEP, TMAX_SLEEP)))

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'
  web_page_url = browser.url
  
  
  ## Edit the relations with other existing documents
  # Go to the Related Documents view
  browser.open(web_page_url+"/Document_viewRelated")
    
  # Fill the Referenced Documents input
  fillRelatedObjects(browser, result,
      "portal_selections/viewSearchRelatedDocumentDialog0:method", 3,
               "ReferencedDocument", TMIN_SLEEP_SHORT, TMAX_SLEEP_SHORT)

  ## Edit content
  web_page_url = '/'.join(web_page_url.split('/')[:-1])
  browser.open(web_page_url+"/WebPage_viewEditor")
  browser.mainForm.getControl(name='field_my_text_content').value = '<html><body><h1>Test</h1><p>Content of test</p></body></html>'
  # Submit the changes, record the time elapsed in seconds
  result('Save', browser.mainForm.submitSave(sleep=(TMIN_SLEEP_LONG, TMAX_SLEEP_LONG)))
  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'


  # Publish it
  show_publish_time, waiting_for_publish_action = \
      browser.mainForm.submitSelectWorkflow(value='submit_action',
                                            maximum_attempt_number=5,
                                            sleep_between_attempt=5,
                                            sleep=(TMIN_SLEEP_SHORT, TMAX_SLEEP_SHORT))

  result('Waiting for publish_action', waiting_for_publish_action)
  result('Show publish', show_publish_time)
  result('Published', browser.mainForm.submitDialogConfirm())
  
  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Status changed.'
