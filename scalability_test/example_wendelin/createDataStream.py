# -*- coding: utf-8 -*-

import datetime
import random
import time
import string
from utils import *

TMIN_SLEEP = 2
TMAX_SLEEP = 6

PREFIX_TITLE = ""
MAX_PRODUCT = 5


def createDataStream(result, browser):
  """
  Create a Data Stream and upload some data.
  """
  # Open ERP5 homepage and log in
  result('Open', browser.open())

  # Log in unless already logged in by a previous test suite
  result('Login', browser.mainForm.submitLogin(
                            sleep=(TMIN_SLEEP, TMAX_SLEEP)))

  # Go to sale Order module
  result('GotoModule',
      browser.mainForm.submitSelectModule(value='/data_stream_module',
                                       sleep=(TMIN_SLEEP, TMAX_SLEEP)))

  # Create a newData Stream (XXX: this will create Data Stream Bucket!) 
  result('Create',
    browser.mainForm.submitNew(sleep=(TMIN_SLEEP, TMAX_SLEEP)))

  # Check whether it has been successfully created
  assert browser.getTransitionMessage() == 'Object created.'
  my_order_sale_url = browser.url.split("?")[0]

  # Fill the title
  my_title = PREFIX_TITLE + generateString(6)
  browser.mainForm.getControl(name='field_my_title').value = my_title

  # Set some random informations
  my_str = generateString(random.randint(1,100))
  browser.mainForm.getControl(name='field_my_description').value = my_str
  
  # XXX: how to upload data?

  # Submit the changes, record the time elapsed in seconds
  result('Save',
    browser.mainForm.submitSave(sleep=(TMIN_SLEEP, TMAX_SLEEP)))

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'
  sale_order_url = my_order_sale_url

  # Validate the Data Stream
  #browser.mainForm.submitSelectWorkflow(value='validate_action')
  #result('Validate',
  #    browser.mainForm.submitDialogConfirm(sleep=(TMIN_SLEEP, TMAX_SLEEP)))
  #assert browser.getTransitionMessage() == 'Status changed.'
