import random
import string

def selectRandomOption(browser, select_name):
  """
  Function to select randomly an option

  @param browser: Browser
  @type browser: Browser
  @param select_name: Name of the input
  @type select_name: string
  """
   # Get the option values
  options = browser.mainForm.getControl(name=select_name).options[1:]
  if len(options) > 0:
    # Select randomly one value
    browser.mainForm.getControl(name=select_name).value = [random.choice(options)]

def generateString(size) :
  """
  Function to generate a string randomly (a-z)

  @param size: Size of the string
  @type size: int
  """
  new_string = random.choice(string.ascii_uppercase)
  new_string = new_string + ''.join(random.choice(string.ascii_lowercase) for x in range(size))
  return new_string

def fillRelatedObjects(browser, result, name, maximum=1, actionName="", TMIN_SLEEP=0, TMAX_SLEEP=0, col_num=0, text="") :
  """
  Function to fill randomly related objetcs

  @param browser: browser
  @type browser: Browser
  @param result: result
  @type result:
  @param name: Name of the input name attribute
  @type name: string
  @param maximum: Max number of related objects
  @type maximum: int
  @param actionName: Name of the action (used for backtrace and statistic ?)
  @type actionName: string
  @param TMIN_SLEEP: Min time to sleep (in second)
  @type TMIN_SLEEP: int
  @param TMAX_SLEEP: Max time to sleep (in second)
  @type TMAX_SLEEP: int
  @param col_num: The numero of the column to filter
  @type col_num: int
  @param text: Text used to filter
  @type text: string
  """

  # Go to the section linked by the input
  result('GoTo '+actionName+' Relations', browser.mainForm.getControl(
      name=name).click())

  # Check the status
  assert (( browser.getTransitionMessage() == 'Please select one (or more) object.' )
           or ( browser.getTransitionMessage() == 'Please select one object.' ))

  # Check if it is possible to choose many objects
  if (browser.getTransitionMessage() == 'Please select one object.'):
    assert ( maximum <= 1 )

  # Filter applied the 'col_num' column with text 'text'
  if col_num != 0 :
    browser.mainForm.getListboxControl(line_number=2, column_number=col_num).value = text
    browser.mainForm.submitDialogUpdate()

  # Get the number of lines
  page_stop_number = browser.etree.xpath('//span[@class="listbox-current-page-stop-number"]')
  if len(page_stop_number) > 0:
    num_line = int(page_stop_number[0].text)
  else:
    num_line = 0
  # Choose randomly one or more objects
  if ( num_line > 0 ) and ( maximum > 0 ):
    iteration = random.randint(1, maximum)
    for i in range(0, iteration):
      line_number = random.randint(1,num_line) + 2
      # Check the box corresponding to line_number if not already checked
      if not browser.mainForm.getListboxControl(line_number=line_number, column_number=1).value == 'checked':
        browser.mainForm.getListboxControl(line_number=line_number, column_number=1).value = 'checked'
  result('Submit '+actionName+' Relations',
      browser.mainForm.submit(name='Base_callDialogMethod:method',
                                        sleep=(TMIN_SLEEP, TMAX_SLEEP)))

  # Check whether the changes have been successfully updated
  assert browser.getTransitionMessage() == 'Data updated.'

def fillOneRelatedObjectSimplified(browser, name):
  """
  Function to fill randomly related objetcs

  @param browser: browser
  @type browser: Browser
  @param name: Name of the input name attribute
  @type name: string
  """

  # Go to the section linked by the input
  browser.mainForm.getControl(name=name).click()

  # Check the status
  assert ( browser.getTransitionMessage() == 'Please select one object.' )

  # Get the number of line
  page_stop_number = browser.etree.xpath('//span[@class="listbox-current-page-stop-number"]')
  if len(page_stop_number) > 0 :
    num_line = int(page_stop_number[0].text)
  else :
    num_line = 0

  # Choose randomly one or more objects
  if num_line > 0 :
    line_number = random.randint(1,num_line) + 2
    # Check the box corresponding to line_number if not already checked
    browser.mainForm.getListboxControl(line_number=line_number, column_number=1).value = 'checked'
    browser.mainForm.submit(name='Base_callDialogMethod:method')

    # Check whether the changes have been successfully updated
    assert browser.getTransitionMessage() == 'Data updated.'