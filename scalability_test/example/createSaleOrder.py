# -*- coding: utf-8 -*-

from builtins import str
from builtins import range
import datetime
import random
import time
import string
from utils import *

TMIN_SLEEP = 2
TMAX_SLEEP = 6

PREFIX_TITLE = ""
MAX_PRODUCT = 5

def addOrderLine(browser, my_title, result) :
  """
  Add an order line to the sale order

  @param browser: Browser
  @type browser: Browser
  @param my_title: The sale order title
  @type my_title: string
  """
  # Create a new Sale Order Line
  browser.mainForm.submitSelectAction(label="Add Sale Order Line")
  assert browser.getTransitionMessage() == 'Object created.'

  # Fill the quantity randomly
  browser.mainForm.getControl(name='field_my_quantity').value = str(random.randint(1, 20))
  result('SetRelationProduct', browser.mainForm.submitSave(
      sleep=(TMIN_SLEEP, TMAX_SLEEP)))
  assert browser.getTransitionMessage() == 'Data updated.'

  # Choose the product randomly
  fillRelatedObjects(browser, result,
      "portal_selections/viewSearchRelatedDocumentDialog0:method", 1,
               "AddOrderLine", TMIN_SLEEP, TMAX_SLEEP)

def createSaleOrder(result, browser):
  """
  Create a Sale Order with details using Sale Trade Condition to fill,
  and add some random sale order lines.
  """
  # Open ERP5 homepage and log in
  result('Open', browser.open())

  # Log in unless already logged in by a previous test suite
  result('Login', browser.mainForm.submitLogin(
                            sleep=(TMIN_SLEEP, TMAX_SLEEP)))

  # Go to sale Order module
  result('GotoModule',
      browser.mainForm.submitSelectModule(value='/sale_order_module',
                                       sleep=(TMIN_SLEEP, TMAX_SLEEP)))

  # Create a new sale order and record the time elapsed in seconds
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
  browser.mainForm.getControl(name='field_my_comment').value = my_str
  browser.mainForm.getControl(name='field_my_description').value = my_str

  # Select some options randomly
  selectRandomOption(browser, "field_my_order")

  # Set dates
  date = datetime.datetime.now()
  browser.mainForm.getControl(name='subfield_field_my_start_date_day').value = str(date.day)
  browser.mainForm.getControl(name='subfield_field_my_start_date_month').value = str(date.month)
  browser.mainForm.getControl(name='subfield_field_my_start_date_year').value = str(date.year)

  # Submit the changes, record the time elapsed in seconds
  result('Save',
    browser.mainForm.submitSave(sleep=(TMIN_SLEEP, TMAX_SLEEP)))

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'
  sale_order_url = my_order_sale_url

  # Set Sale Trade Condition, Client and Beneficiary
  for number_button in (2,4,5):
    fillRelatedObjects(browser, result,
      "portal_selections/viewSearchRelatedDocumentDialog%s:method" % str(number_button), 1,
               "AddOrderLine", TMIN_SLEEP, TMAX_SLEEP)

  # Add Sale order lines
  max_ite = random.randint(1, MAX_PRODUCT)
  for i in range (0, max_ite):
    browser.open(sale_order_url+"/view")
    addOrderLine(browser, my_title, result)

  browser.open(my_order_sale_url)

  # Validate the Sale Order
  browser.mainForm.submitSelectWorkflow(value='plan_action')
  result('Validate',
      browser.mainForm.submitDialogConfirm(sleep=(TMIN_SLEEP, TMAX_SLEEP)))
  assert browser.getTransitionMessage() == 'Status changed.'
