# -*- coding: utf-8 -*-

import datetime
import random
import time
import string
from utils import *

TMIN_SLEEP = 2
TMAX_SLEEP = 6

SALE_TRADE_CONDITION_NAME = "Scalability Sale Trade Condition"
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

  ## Choose the product randomly
  fillRelatedObjects(browser, result,
      "portal_selections/viewSearchRelatedDocumentDialog0:method", 1,
               "AddOrderLine", TMIN_SLEEP, TMAX_SLEEP)


def createSaleOrder(result, browser):
  """
  Create a Sale Order with details using Sale Trade Condition to fill,
  and add some random sale order lines.
  Use the following command:
  performance_tester_erp5 http://foo.bar:4242/erp5/ 1 createSaleOrder

  Please note that  you must run this command from the  same directory of this
  script and userInfo.py.  Further information  about performance_tester_erp5
  options and arguments are available by specifying ``--help''.

  This test requires the bt5 erp5_simulation_performance_test to be installed
  for relation with organisation, also it requires a configured Sale Trade Condition.
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
  sale_order_url = browser.url


  ## Set Sale Trade conditions
  # Click on the specified menu
  result('GoToSaleTradeConditionRelations', browser.mainForm.getControl(
      name="portal_selections/viewSearchRelatedDocumentDialog2:method").click())
  assert browser.getTransitionMessage() == 'Please select one object.'
  line_number = browser.getListboxPosition(SALE_TRADE_CONDITION_NAME, column_number=2)
  # Check the box corresponding to line_number
  browser.mainForm.getListboxControl(line_number=line_number, column_number=1).click()
  result('SubmitSaleTradeConditionRelation',
      browser.mainForm.submit(name='Base_callDialogMethod:method',
                                        sleep=(TMIN_SLEEP, TMAX_SLEEP)))

  # Add Sale order lines
  max_ite = random.randint(1,MAX_PRODUCT)
  for i in range (0, max_ite):
    browser.open(sale_order_url+"/view")
    addOrderLine(browser, my_title, result)

  browser.open(my_order_sale_url)

  # Validate the Sale Order
  browser.mainForm.submitSelectWorkflow(value='plan_action')
  result('Validate',
      browser.mainForm.submitDialogConfirm(sleep=(TMIN_SLEEP, TMAX_SLEEP)))
  assert browser.getTransitionMessage() == 'Status changed.'
