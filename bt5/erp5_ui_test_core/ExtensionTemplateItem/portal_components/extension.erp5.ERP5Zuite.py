import itertools
import time
from Products.CMFActivity.Activity.Queue import VALIDATION_ERROR_DELAY
from Products.CMFActivity.ActivityTool import getCurrentNode

def waitForActivities(self, delay=100, count=None):
  """
    We wait until all activities are finished

    RuntimeError is raised in case there is no way
    to finish activities.
  """
  activity_tool = self.getPortalObject().portal_activities
  assert not (
    activity_tool.isSubscribed()
    and getCurrentNode() in activity_tool.getProcessingNodeList()), \
    'still subscribed to activities'

  if count is not None: # BBB
    # completely arbitrary conversion factor: count used to default to 1000
    # and I (just as arbitrarily) converted that into a 100s default maximum
    # tolerable wait delay before bailing.
    delay = count / 10.
  deadline = time.time() + delay
  for call_count in itertools.count():
    x = activity_tool.getMessageList()
    if not x:
      return 'Done.'
    if all(x.processing_node == -2 for x in x):
      raise RuntimeError(
        'tic is looping forever: one failing activity (%s %s)' % (x[0].object_path, x[0].method_id)
      )
    activity_tool.process_timer(None, None)
    if time.time() > deadline:
      break
    if call_count % 10 == 0:
      activity_tool.timeShift(3 * VALIDATION_ERROR_DELAY)
  raise RuntimeError('tic is looping forever.')

def UpdateImage(image):
  image._update_image_info()

def urlread(url, safe_return=0):
  import urllib
  try:
    return urllib.urlopen(url).read()
  except IOError as e:
    if safe_return:
      # Return an Selenium test code that will obviously fail. This
      # prevent zelenium test run get Stalled.
      return """<html><body><table><tr><td>assertTextPresent</td>
                <td>An error occurred when dowload %s : %s </td>
                <td></td><tr></body></html>""" % (url , e)
    raise IOError(e)


def editZPT(zpt, text):
  zpt.pt_edit(text, 'text/html')

"""
  Add the test at the end of the webpage (overwrite the current test if there's already one) and hide it
"""
def appendTestToWebPage(text, test_text):
  import lxml.html
  root = lxml.html.fromstring(text)
  test_root = lxml.html.fromstring(test_text)
  test_root = test_root.xpath('//table')[0]
  tutorial_test = lxml.html.fromstring('<table></table>')
  tutorial_test.tag = test_root.tag
  for att in test_root.attrib.keys():
    tutorial_test.attrib[att] = test_root.attrib[att]
  tutorial_test.append(test_root[1])
  hidden_list = [tutorial_test] + tutorial_test.xpath('//span')
  for element in hidden_list:
    element.attrib['style']='display:none;'
  table_list = root.xpath('//table[@id="SELENIUM-TEST"]')
  if(len(table_list) == 0):
    root.append(tutorial_test)
  else:
    root.replace(table_list[0], tutorial_test)
  return lxml.html.tostring(root).replace('\n','').replace("\'","'")
