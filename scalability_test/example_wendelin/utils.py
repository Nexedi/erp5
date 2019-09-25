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
