# -*- coding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# First version: ERP5Mechanize from Vincent Pelletier <vincent@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import logging
import sys
from six.moves.urllib.parse import urlencode
from six.moves import http_cookies as Cookie
import re

from zope.testbrowser._compat import urlparse
from z3c.etestbrowser.browser import ExtendedTestBrowser
from zope.testbrowser.browser import onlyOne
from contextlib import contextmanager

def measurementMetaClass(prefix):
  """
  Prepare a meta class where the C{prefix} is used to select for which
  methods measurement methods will be added automatically.

  @param prefix:
  @type prefix: str
  @return: The measurement meta class corresponding to the prefix
  @rtype: type
  """
  class MeasurementMetaClass(type):
    """
    Meta class to automatically wrap methods whose prefix starts with
    C{prefix}, and also to define C{lastRequestSeconds} on other classes
    besides of Browser.
    """
    def __new__(metacls, name, bases, dictionary):
      def nonBrowserClass_getattr(self, attribute):
        """
        Some attributes, such as lastRequestSeconds, are only defined in the
        Browser class
        """
        return getattr(self.browser, attribute)

      def timeInSecondDecorator(method):
        def wrapper(self, *args, **kwargs):
          """
          Replaced by the wrapped method docstring. Some methods return the
          time spent on waiting (C{submitSelectJump} and for example), thus
          return a tuple with the time spent on the request and the time spent
          on waiting
          """
          if 'sleep' in kwargs:
            minimum_sleep, maximum_sleep = kwargs.pop('sleep')
            self.randomSleep(minimum_sleep, maximum_sleep)

          ret = method(self, *args, **kwargs)
          if ret is None:
            return self.lastRequestSeconds
          elif isinstance(ret, tuple):
            return (self.lastRequestSeconds,) + ret
          else:
            return (self.lastRequestSeconds, ret)

        return wrapper

      def applyMeasure(method):
        """
        Inner function to wrap timed methods to automatically return the time
        spent on the request

        @param method: Instance method to be called
        @type method: function
        """
        wrapper_method = timeInSecondDecorator(method)
        wrapper_method.func_name = method.func_name
        wrapper_method.__doc__ = method.__doc__

        # In order to avoid re-wrapping the method when looking at the bases
        # for example
        wrapper_method.__is_wrapper__ = True

        dictionary[method.func_name] = wrapper_method

      # Only wrap methods prefixed by the given prefix
      for attribute_name, attribute in dictionary.items():
        if attribute_name.startswith(prefix) and callable(attribute):
          applyMeasure(attribute)

      # And also create these methods by looking at the bases
      for attribute_name in dir(bases[0]):
        if attribute_name not in dictionary and \
           attribute_name.startswith(prefix):
          attribute = getattr(bases[0], attribute_name)
          if callable(attribute) and not getattr(attribute, '__is_wrapper__', False):
            applyMeasure(attribute)

      if 'Browser' not in bases[0].__name__:
        dictionary['__getattr__'] = nonBrowserClass_getattr

      return super(MeasurementMetaClass,
                   metacls).__new__(metacls, name, bases, dictionary)

  return MeasurementMetaClass

import random
import time

class Browser(ExtendedTestBrowser):
  """
  Implements mechanize tests specific to an ERP5 environment through
  U{ExtendedTestBrowser<http://pypi.python.org/pypi/z3c.etestbrowser>}
  (providing features to parse XML and access elements using XPATH)
  using U{zope.testbrowser<http://pypi.python.org/pypi/zope.testbrowser>}
  (providing benchmark and testing features on top of
  U{mechanize<http://wwwsearch.sourceforge.net/mechanize/>}).

  @todo:
   - getFormulatorFieldValue
  """
  __metaclass__ = measurementMetaClass(prefix='open')

  def __init__(self,
               erp5_base_url,
               username,
               password,
               log_file=None,
               is_debug=False,
               is_legacy_listbox=False):
    """
    Create a browser object.

    @param erp5_base_url: ERP5 HTTP URL
    @type erp5_base_url: str
    @param username: Username to be used to log into ERP5
    @type username: str
    @param password: Password to be used to log into ERP5
    @param log_file: Log file object (stderr if none given)
    @type log_file: file
    @param is_debug: Enable or disable debugging (disable by default)
    @type is_debug: bool
    @param is_legacy_listbox: Use legacy listbox
    @type is_legacy_listbox: bool
    """
    # Meaningful to re-create the MainForm class every time the page
    # has been changed
    self._main_form = None

    self._erp5_base_url = erp5_base_url
    if self._erp5_base_url[-1] != '/':
      self._erp5_base_url += '/'

    self._username = username
    self._password = password

    # Only display WARNING message if debugging is not enabled
    logging_level = is_debug and logging.DEBUG or logging.WARNING
    stream = log_file and log_file or sys.stderr
    logging.basicConfig(
      stream=stream, level=logging_level,
      format='%(asctime)s: %(levelname)s: %(message)s [%(name)s]')

    self._logger = logging.getLogger('erp5.util.testbrowser')
    self._is_legacy_listbox = is_legacy_listbox
    self._is_logged_in = False

    super(Browser, self).__init__()

  def open(self, url_or_path=None, data=None, site_relative=True):
    """
    Open a relative (to the ERP5 base URL) or absolute URL. If the given URL
    is not given, then it will open the home ERP5 page. If C{site_relative} is
    False, it will open the URL within the current context.

    @param url_or_path: Relative or absolute URL
    @type url_or_path: str
    """
    if site_relative:
      # In case url_or_path is an absolute URL, urljoin() will return
      # it, otherwise it is a relative path and will be concatenated to
      # ERP5 base URL
      url_or_path = urlparse.urljoin(self._erp5_base_url, url_or_path)

    if isinstance(data, dict):
      data = urlencode(data)

    self._logger.debug("Opening: " + url_or_path)
    super(Browser, self).open(url_or_path, data)

  @contextmanager
  def _preparedRequest(self, url, no_visit=False):
    """
    Monkey patched for openNoVisit()
    """
    from zope.testbrowser._compat import urlparse

    self.timer.start()

    headers = {}
    if self.url:
      headers['Referer'] = self.url

    if self._req_content_type:
      headers['Content-Type'] = self._req_content_type

    headers['Connection'] = 'close'
    headers['Host'] = urlparse.urlparse(url).netloc
    headers['User-Agent'] = 'Python-urllib/2.4'

    headers.update(self._req_headers)

    extra_environ = {}
    if self.handleErrors:
      extra_environ['paste.throw_errors'] = None
      headers['X-zope-handle-errors'] = 'True'
    else:
      extra_environ['wsgi.handleErrors'] = False
      extra_environ['paste.throw_errors'] = True
      extra_environ['x-wsgiorg.throw_errors'] = True
      headers.pop('X-zope-handle-errors', None)

    kwargs = {'headers': sorted(headers.items()),
              'extra_environ': extra_environ,
              'expect_errors': True}

    yield kwargs

    if not no_visit:
      self._changed()

    self.timer.stop()

  def _processRequest(self, url, make_request, no_visit=False):
    """
    Monkey patched for openNoVisit()
    """
    from zope.testbrowser.browser import REDIRECTS
    from zope.testbrowser._compat import urlparse

    with self._preparedRequest(url, no_visit=no_visit) as reqargs:
      if not no_visit:
        self._history.add(self._response)

      resp = make_request(reqargs)
      remaining_redirects = 100  # infinite loops protection
      while resp.status_int in REDIRECTS and remaining_redirects:
        remaining_redirects -= 1
        # BEGIN: Bugfix
        location = resp.headers['location']
        if '?' in location:
          location_without_query_string, query_string = location.split('?')
          location = (
            location_without_query_string +
            '?' + urlencode(urlparse.parse_qs(query_string,
                                                     strict_parsing=True),
                                   doseq=True))
        # END: Bugfix
        url = urlparse.urljoin(url, location)

        with self._preparedRequest(url, no_visit=no_visit) as reqargs:
          resp = self.testapp.get(url, **reqargs)
      assert remaining_redirects > 0, "redirects chain looks infinite"

      if not no_visit:
        self._setResponse(resp)
      self._checkStatus()

    return resp

  def _absoluteUrl(self, url):
    absolute = url.startswith('http://') or url.startswith('https://')
    if absolute:
      return str(url)

    if self._response is None:
      raise BrowserStateError(
        "can't fetch relative reference: not viewing any document")

    if not isinstance(url, unicode):
      url = url.decode('utf-8')

    return str(urlparse.urljoin(self._getBaseUrl(), url).encode('utf-8'))

  def openNoVisit(self, url_or_path, data=None, site_relative=True):
    """
    Copy/paste from zope.testbrowser.Browser.open() to allow opening an URL
    without changing the current page. See L{open}.

    @see zope.testbrowser.interfaces.IBrowser
    """
    if site_relative:
      # In case url_or_path is an absolute URL, urljoin() will return
      # it, otherwise it is a relative path and will be concatenated to
      # ERP5 base URL
      url_or_path = urlparse.urljoin(self._erp5_base_url, url_or_path)

    if isinstance(data, dict):
      data = urlencode(data)

    url = self._absoluteUrl(url_or_path)
    self._logger.debug("Opening: " + url)

    if data is not None:
      def make_request(args):
        return self.testapp.post(url, data, **args)
    else:
      def make_request(args):
        return self.testapp.get(url, **args)

    return self._processRequest(url, make_request, no_visit=True)

  def randomSleep(self, minimum, maximum):
    """
    Allow to randomly sleep in seconds in the interval [minimum,
    maximum] and is meaningful to simulate an user more realistically.

    It is also called automatically when passing sleep argument to
    click* (C{Link} classes), submit* (C{Form} classes) or open*
    (C{Browser} classes) functions, see C{timeInSecondDecorator} wrapper.

    @param minimum: Minimum number of seconds to sleep
    @type minimum: int
    @param maximum: Maximum number of seconds to sleep
    @type maximum: int
    """
    sleep_time = random.randint(minimum, maximum)

    self._logger.debug("Sleeping %ds ([%d, %d])" % (sleep_time,
                                                   minimum,
                                                   maximum))

    time.sleep(sleep_time)

  def getCookieValue(self, name, default=None):
    """
    Get the cookie value of the given cookie name.

    @param name: Name of the cookie
    @type name: str
    @param default: Fallback value if the cookie was not found
    @type default: str
    @return: Cookie value
    @rtype: str
    """
    return self.cookies.get(name, default)

  @property
  def mainForm(self):
    """
    Get the ERP5 main form of the current page. ERP5 generally use
    only one form (whose C{id} is C{main_form}) for all the controls
    within a page. A Form instance is returned including helper
    methods specific to ERP5.

    @return: The main Form class instance
    @rtype: Form

    @raise LookupError: The main form could not be found.

    @todo: Perhaps the page could be parsed to generate a class with
           only appropriate methods, but that would certainly be an
           huge overhead for little benefit...

    @todo: Patch zope.testbrowser to allow the class to be given
           rather than duplicating the code
    """
    # If the page has not changed, no need to re-create a class, so
    # just return the main_form instance
    if self._main_form and self._counter == self._main_form._browser_counter:
      return self._main_form
    main_form = self.getForm(id='main_form')._form
    if not main_form:
      raise LookupError("Could not get 'main_form'")
    self._main_form = ContextMainForm(self, main_form)
    return self._main_form

  def getLink(self, text=None, url=None, id=None, index=0,
              class_attribute=None):
    """
    Override original C{getLink} allowing to not consider the HTTP
    query string unless it is explicitly given.

    Also, allows to select a link by its class attribute, which
    basically look for the first element whose C{attribute} is
    C{class_attribute} then call C{getLink} with the element C{href}.

    @param class_attribute: Get the link with this class
    @type class_attribute: str
    @param args: Positional arguments given to original C{getLink}
    @type args: list
    @param kwargs: Keyword arguments given to original C{getLink}
    @type kwargs: dict
    """
    if class_attribute:
      element_list = self.etree.xpath('//a[contains(@class, "%s")]' % \
                                        class_attribute)

      try:
        url = element_list[0].get('href')
      except (IndexError, AttributeError):
        url = None

      if not url:
        raise LookupError("Could not find any link whose class is '%s'" % \
                            class_attribute)

    elif url and '?' not in url:
      url += '?'

    from zope.testbrowser.browser import isMatching, LinkNotFoundError
    qa = 'a' if id is None else 'a#%s' % id
    qarea = 'area' if id is None else 'area#%s' % id
    html = self._html
    links = html.select(qa)
    links.extend(html.select(qarea))

    matching = []
    for elem in links:
      matches = (isMatching(elem.text.encode('utf-8'), text) and
                 isMatching(elem.get('href', ''), url))

      if matches:
        matching.append(elem)

    if index >= len(matching):
      raise LinkNotFoundError()
    elem = matching[index]

    baseurl = self._getBaseUrl()

    return LinkWithTime(elem, self, baseurl)

  def getImportExportLink(self):
    """
    Get Import/Export link. Use the class attribute rather than the
    name as the latter is dependent on the context.

    @return: The link whose class is C{report}
    @rtype: Link

    @todo: Should perhaps be a ContextBrowser class?
    """
    return self.getLink(class_attribute='import_export')

  def getFastInputLink(self):
    """
    Get Fast Input link. Use the class attribute rather than the name
    as the latter is dependent on the context.

    @return: The link whose class is C{fast_input}
    @rtype: Link

    @todo: Should perhaps be a ContextBrowser class?
    """
    return self.getLink(class_attribute='fast_input')

  def getTransitionMessage(self):
    """
    Parse the current page and returns the value of the portal_status
    message.

    @return: The transition message
    @rtype: str

    @raise LookupError: Not found
    """
    try:
      transition_message = self.etree.xpath(
        '//div[@id="transition_message"]')[0].text
    except IndexError:
      raise LookupError("Cannot find div with ID 'transition_message'")
    else:
      if isinstance(transition_message, unicode):
        transition_message = transition_message.encode('utf-8')

      return transition_message

  def getInformationArea(self):
    """
    Parse the current page and returns the value of the information_area
    message.

    @return: The information area message
    @rtype: str

    @raise LookupError: Not found
    """
    try:
      return self.etree.xpath('//div[@id="information_area"]')[0].text
    except IndexError:
      raise LookupError("Cannot find div with ID 'information_area'")

  _listbox_table_xpath_str = '//table[contains(@class, "listbox-table")]'

  _legacy_listbox_table_xpath_str = '//div[contains(@class, "listbox")]'\
      '//table'

  def getListboxLink(self, line_number, column_number, cell_element_index=1,
                     *args, **kwargs):
    """
    Follow the link at the given position, excluding any link whose
    class is hidden. In case there are several links within a cell,
    C{cell_element_index} allows to select which one to get (starting
    from 1).

    @param line_number: Line number of the link
    @type line_number: int
    @param column_number: Column number of the link
    @type column_number: int
    @param cell_element_index: Index of the link to be selected in the cell
    @type cell_element_index: int
    @param args: positional arguments given to C{getLink}
    @type args: list
    @param kwargs: keyword arguments given to C{getLink}
    @type kwargs: dict
    @return: C{Link} at the given line and column number
    @rtype: L{zope.testbrowser.interfaces.ILink}

    @raise LookupError: No link could be found at the given position
                        and cell indexes
    """
    if self._is_legacy_listbox:
      listbox_basic_xpath_str = self._legacy_listbox_table_xpath_str
    else:
      listbox_basic_xpath_str = self._listbox_table_xpath_str

    # With XPATH, the position is context-dependent, therefore, as
    # there the cells are either within a <thead> or <tbody>, the line
    # number must be shifted by the number of header lines (namely 2)
    if line_number <= 2:
      relative_line_number = line_number

      if self._is_legacy_listbox:
        column_type = 'td'
      else:
        column_type = 'th'
    else:
      if self._is_legacy_listbox:
        relative_line_number = line_number
      else:
        relative_line_number = line_number - 2

      column_type = 'td'

    xpath_str = '%s//tr[%d]//%s[%d]//a[not(contains(@class, "hidden"))][%d]' % \
        (listbox_basic_xpath_str,
         relative_line_number,
         column_type,
         column_number,
         cell_element_index)

    # xpath() method always return a list even if there is only one element
    element_list = self.etree.xpath(xpath_str)

    try:
      link_href = element_list[0].get('href')
    except (IndexError, AttributeError):
      link_href = None

    if not link_href:
      raise LookupError("Could not find link in listbox cell %dx%d (index=%d)" %\
                          (line_number, column_number, cell_element_index))

    return self.getLink(url=link_href, *args, **kwargs)

  def getListboxPosition(self,
                         text,
                         column_number=None,
                         line_number=None,
                         strict=False):
    """
    Returns the position number of the first line containing given
    text in given column or line number (starting from 1).

    @param text: Text to search
    @type text: str
    @param column_number: Look into all the cells of this column
    @type column_number: int
    @param line_number: Look into all the cells of this line
    @type line_number: int
    @param strict: Should given text matches exactly
    @type strict: bool
    @return: The cell position
    @rtype: int

    @raise LookupError: Not found
    """
    # Require either column_number or line_number to be given
    onlyOne([column_number, line_number], '"column_number" and "line_number"')

    if self._is_legacy_listbox:
      listbox_basic_xpath_str = self._legacy_listbox_table_xpath_str
    else:
      listbox_basic_xpath_str = self._listbox_table_xpath_str

    # Get all cells in the column (if column_number is given and
    # including header columns) or line (if line_number is given)
    if column_number:
      xpath_str_fmt = listbox_basic_xpath_str + '//tr//%%s[%d]' % \
          column_number

      if self._is_legacy_listbox:
        column_or_line_xpath_str = xpath_str_fmt % 'td'
      else:
        column_or_line_xpath_str = "%s | %s" % (xpath_str_fmt % 'th',
                                                xpath_str_fmt % 'td')

    else:
      listbox_basic_xpath_str = self._listbox_table_xpath_str

      # With XPATH, the position is context-dependent, therefore, as
      # there the cells are either within a <thead> or <tbody>, the
      # line number must be shifted by the number of header lines
      # (namely 2)
      if line_number <= 2:
        relative_line_number = line_number

        if self._is_legacy_listbox:
          column_type = 'td'
        else:
          column_type = 'th'
      else:
        if self._is_legacy_listbox:
          relative_line_number = line_number
        else:
          relative_line_number = line_number - 2

        column_type = 'td'

      column_or_line_xpath_str = listbox_basic_xpath_str + '//tr[%d]//%s' %\
          (relative_line_number, column_type)

    cell_list = self.etree.xpath(column_or_line_xpath_str)

    # Iterate over the cells list until one the children content
    # matches the expected text
    for position, cell in enumerate(cell_list):
      for child in cell.iterchildren():
        if not child.text:
          continue

        if (strict and child.text == text) or \
           (not strict and text in child.text):
          return position + 1

    raise LookupError("No matching cell with value '%s'" % text)

  def getRemainingActivityCounter(self):
    """
    Return the number of remaining activities, but do not visit the
    URL so it does not interfere with next calls.

    @return: The number of remaining activities
    @rtype: int
    """
    self._logger.debug("Checking the number of remaining activities")
    response = self.openNoVisit('portal_activities/countMessage')[1]
    activity_counter = response.body

    activity_counter = activity_counter and int(activity_counter) or 0
    self._logger.debug("Remaining activities: %d" % activity_counter)

    return activity_counter

  def waitForActivity(self, interval=20, maximum_attempt_number=30):
    """
    Wait for activities every C{interval} seconds at most
    C{maximum_attempt_number} of times and return the waiting time (excluding
    loading time to get the number of remaining time).

    This is mainly relevant when a setup script triggering activities has to
    be executed before running the actual script.

    @param interval: Interval between checking for remaining activities
    @type interval: int
    @param maximum_attempt_number: Number of attempts before failing
    @type maximum_attempt_number: int
    @return: Number of seconds spent waiting
    @rtype: int
    """
    current_attempt_counter = 0
    while current_attempt_counter < maximum_attempt_number:
      if self.getRemainingActivityCounter() == 0:
        return current_attempt_counter * interval

      time.sleep(interval)
      current_attempt_counter += 1

    raise AssertionError("Maximum number of attempts reached while waiting "
                         "for activities to be processed")

from zope.testbrowser.browser import Form, ListControl

class LoginError(Exception):
  """
  Exception raised when login fails
  """
  pass

class MainForm(Form):
  """
  Class defining convenient methods for the main form of ERP5. All the
  methods specified are those always found in an ERP5 page in contrary
  to L{ContextMainForm}.
  """
  __metaclass__ = measurementMetaClass(prefix='submit')

  def submit(self, label=None, name=None, class_attribute=None, index=None,
             *args, **kwargs):
    """
    Overriden for logging purpose, and for specifying a default index
    to 0 if not set, thus avoiding AmbiguityError being raised (in
    ERP5 there may be several submit fields with the same name).

    Also, allows to select a submit by its class attribute, which
    basically look for the first element whose C{attribute} is
    C{class_attribute} then call C{submit} with the element C{name}.

    @param class_attribute: Submit according to the class attribute
    @type class_attribute: str

    @raise LookupError: Could not find any element matching the given
                        class attribute name, if class_attribute
                        parameter is given.
    """
    self._logger.debug(
      "Submitting (name='%s', label='%s', class='%s')" % (name, label,
                                                          class_attribute))

    if class_attribute:
      element_list = self.browser.etree.xpath('//*[contains(@class, "%s")]' % \
                                                class_attribute)

      try:
        name = element_list[0].get('name')
      except (IndexError, AttributeError):
        name = None

      if not name:
        raise LookupError("Could not find any button whose class is '%s'" % \
                            class_attribute)

    if label is None and name is None:
      super(MainForm, self).submit(label=label, name=name, *args, **kwargs)
    else:
      if index is None:
        index = 0
      super(MainForm, self).submit(label=label, name=name, index=index,
                                   *args, **kwargs)

  def submitSelect(self, select_name, submit_name, label=None, value=None,
                   select_index=None, control_index=None):
    """
    Get the select control whose name attribute is C{select_name},
    then select the option control specified either by its C{label} or
    C{value} within that select control, and finally submit it using
    the submit control whose name attribute is C{submit_name}.

    The C{value} matches an option value if found at the end of the
    latter (excluding the query string), for example a search for
    I{/logout} will match I{/erp5/logout} and I{/erp5/logout?foo=bar}
    (if and only if C{value} contains no query string) but not
    I{/erp5/logout_bar}.

    Label value is searched as case-sensitive whole words within the
    labels for each item--that is, a search for I{Add} will match
    I{Add a contact} but not I{Address}.  A word is defined as one or
    more alphanumeric characters or the underline.

    C{select_index} and C{control_index} have the same meaning as in
    zope.testbrowser, namely to select a particular select or control
    when the C{label} or C{value} is ambiguous.

    @param select_name: Select control name
    @type select_name: str
    @param submit_name: Submit control name
    @type submit_name: str
    @param label: Label of the option control
    @type label: str
    @param value: Value of the option control
    @type value: str
    @param select_index: Index of the select if multiple matches
    @type select_index: int
    @param control_index: Index of the control if multiple matches
    @type control_index: int

    @raise LookupError: The select, option or submit control could not
                        be found
    """
    
    select_control = self.getControl(name=select_name, index=select_index)
    # zope.testbrowser checks for a whole word but it is also useful
    # to match the end of the option control value string because in
    # ERP5, the value could be URL (such as 'http://foo:81/erp5/logout')
    if value:
      for item in select_control.options:
        if '?' not in value:
          item = item.split('?')[0]

        if item.endswith(value):
          value = item
          break
    self._logger.debug("select_id='%s', label='%s', value='%s'" % \
                                 (select_name, label, value))
    select_control.getControl(label=label, value=value,
                              index=control_index).selected = True
    self.submit(name=submit_name)

  def submitLogin(self):
    """
    Log into ERP5 using the username and password provided in the
    browser. It is assumed that the current page is the login page (by
    calling C{open('login_form')} beforehand), otherwise it will open
    that page before logging in.

    Note that if the user is already logged in, it will do nothing.

    @raise LoginError: Login failed

    @todo: Use information sent back as headers rather than looking
           into the page content?
    """
    check_logged_in_xpath = '//div[@id="logged_in_as"]/*'
    if self.etree.xpath(check_logged_in_xpath):
      self._logger.debug("Already logged in")
      # TODO: Perhaps zope.testbrowser should be patched instead?
      self.browser.timer.start_time = self.browser.timer.end_time = 0
      return

    self._logger.debug("Logging in: username='%s', password='%s'" % \
                         (self.browser._username, self.browser._password))

    def login(form):
      form.getControl(name='__ac_name').value = self.browser._username
      form.getControl(name='__ac_password').value = self.browser._password
      form.submit()

    def setCookies():
      """
      Gets the __ac value from the browser headers and sets it as cookie in order to keep
      the user logged during the tests. If SimpleCookie can't parse the values,
      regular expressions are used.
      """
      headers_cookie = self.browser.headers['set-cookie']
      cookie = Cookie.SimpleCookie()
      cookie.load(headers_cookie)
      if '__ac' in cookie.keys():
        ac_value = cookie['__ac'].value
      else:
        reg = '__ac=\"([A-Za-z0-9%]+)*\"'
        match = re.search(reg, headers_cookie)
        ac_value = match.group(1) if match else None
      self.browser.cookies["__ac"] = ac_value

    try:
      login(self)
    except LookupError:
      self.browser.open('login_form')
      login(self.browser.mainForm)

    if not self.etree.xpath(check_logged_in_xpath):
      raise LoginError("%s: Could not log in as '%s:%s'" % \
                         (self.browser._erp5_base_url,
                          self.browser._username,
                          self.browser._password))
    setCookies()

  def submitSelectFavourite(self, label=None, value=None, **kw):
    """
    Select and submit a favourite, given either by its label (such as
    I{Log out}) or value (I{/logout}). See L{submitSelect}.
    """
    self.submitSelect('select_favorite', 'Base_doFavorite:method', label, value,
                      **kw)

  def submitSelectModule(self, label=None, value=None, **kw):
    """
    Select and submit a module, given either by its label (such as
    I{Currencies}) or value (such as I{/glossary_module}). See
    L{submitSelect}.
    """
    self.submitSelect('select_module', 'Base_doModule:method', label, value,
                      **kw)

  def submitSelectLanguage(self, label=None, value=None, **kw):
    """
    Select and submit a language, given either by its label (such as
    I{English}) or value (such as I{en}). See L{submitSelect}.
    """
    self.submitSelect('select_language', 'Base_doLanguage:method', label, value)

  def submitSearch(self, search_text):
    """
    Fill search field with C{search_text} and submit it.

    @param search_text: Text to search
    @type search_text: str
    """
    self.getControl(name='field_your_search_text').value = search_text
    self.submit(name='ERP5Site_viewQuickSearchResultList:method')

  def submitLogout(self):
    """
    Perform logout.
    """
    self.submitSelectFavourite(value='/logout')

class ContextMainForm(MainForm):
  """
  Class defining context-dependent convenient methods for the main
  form of ERP5.

  @todo:
   - doListboxAction
   - doContextListMode
   - doContextSearch
   - doContextSort
   - doContextConfigure
   - doContextButton
   - doContextReport
   - doContextExchange
  """
  def submitSelectJump(self, label=None, value=None,
                       no_jump_transition_message=None,
                       maximum_attempt_number=1, sleep_between_attempt=0,
                       **kw):
    """
    Select and submit a jump, given either by its label (such as
    I{Queries}) or value (such as
    I{/person_module/Base_jumpToRelatedObject?portal_type=Foo}). See
    L{submitSelect}.

    Usually, a transition message will be displayed if it was not possible to
    jump (for example because the object has not been created yet), therefore
    the number of attempts before failing can be specified if necessary.

    @param no_jump_transition_message: Transition message displayed if the
                                       jump could not be performed
    @type no_jump_transition_message: str
    @param maximum_attempt_number: Number of attempts before failing
    @type maximum_attempt_number: int
    @param sleep_between_attempt: Sleep N seconds between attempts
    @type sleep_between_attempt: int
    """
    if not no_jump_transition_message:
      self.submitSelect('select_jump', 'Base_doJump:method',
                        label, value, **kw)
    else:
      current_attempt_counter = 0
      while current_attempt_counter != maximum_attempt_number:
        self.browser.mainForm.submitSelect('select_jump', 'Base_doJump:method',
                                           label, value, **kw)

        if no_jump_transition_message != self.browser.getTransitionMessage():
          return current_attempt_counter * sleep_between_attempt

        time.sleep(sleep_between_attempt)
        current_attempt_counter += 1

      raise AssertionError("Could not jump to related object")

  def submitSelectAction(self, label=None, value=None, **kw):
    """
    Select and submit an action, given either by its label (such as
    I{Add Person}) or value (such as I{add} and I{add Person}). See
    L{submitSelect}.
    """
    self.submitSelect('select_action', 'Base_doAction:method', label, value,
                      **kw)

  def submitCut(self):
    """
    Cut the previously selected objects.
    """
    self.submit(name='Folder_cut:method')

  def submitCopy(self):
    """
    Copy the previously selected objects.
    """
    self.submit(name='Folder_copy:method')

  def submitPaste(self):
    """
    Paste the previously selected objects.
    """
    self.submit(name='Folder_paste:method')

  def submitPrint(self):
    """
    Print the previously selected objects. Use the class attribute
    rather than the name as the latter is dependent on the context.
    """
    self.submit(class_attribute='print')

  def submitReport(self):
    """
    Create a report. Use the class attribute rather than the name as
    the latter is dependent on the context.
    """
    self.submit(class_attribute='report')

  def submitNew(self):
    """
    Create a new object.
    """
    self.submit(name='Folder_create:method')

  def submitClone(self):
    """
    Clone the previously selected objects. Use the class attribute
    rather than the name as the latter is dependent on the context.
    """
    self.submit(class_attribute='clone')

  def submitDelete(self):
    """
    Delete the previously selected objects.
    """
    self.submit(name='Folder_deleteObjectList:method')

  def submitSave(self):
    """
    Save the previously selected objects.
    """
    self.submit(name='Base_edit:method')

  def submitShow(self):
    """
    Show the previously selected objects.
    """
    self.submit(name='Folder_show:method')

  def submitFilter(self):
    """
    Filter the objects.
    """
    self.submit(name='Folder_filter:method')

  def submitAction(self):
    """
    Select/unselect objects.
    """
    self.submit(name='Base_doSelect:method')

  def submitSelectWorkflow(self, label=None, value=None,
                           script_id='viewWorkflowActionDialog',
                           maximum_attempt_number=1,
                           sleep_between_attempt=0,
                           dialog_name=None,
                           expected_transition_message=None,
                           **kw):
    """
    Select and submit a workflow action, given either by its label
    (such as I{Create User}) or value (such as I{create_user_action}
    in I{/Person_viewCreateUserActionDialog?workflow_action=create_user_action},
    with C{script_id=Person_viewCreateUserActionDialog}). See L{submitSelect}.

    When validating an object, L{submitDialogConfirm} allows to perform the
    validation required on the next page, and can be called directly by
    passing the function object in C{dialog_name} parameter.

    As the Workflow action may not be available yet, it is possible to set the
    maximum number of attempts and the sleep duration between each attempt.

    The return value depends on the parameters (see C{timeInSecondDecorator}):
    - C{dialog_name} is given:
      - If C{maximum_attempt_number} equals to 1:
        (show_page_after_dialog_time, show_dialog_time)
      - Otherwise:
        (show_page_after_dialog_time, show_dialog_time, wait_time)
    - Otherwise:
      - If C{maximum_attempt_number} equals to 1:
        show_dialog_time
      - Otherwise:
        (show_dialog_time, wait_time)

    @param script_id: Script identifier
    @type script_id: str
    @param maximum_attempt_number: Number of attempts before failing
    @type maximum_attempt_number: int
    @param sleep_between_attempt: Sleep N seconds between attempts
    @type sleep_between_attempt: int
    @param dialog_name: Function to call after the workflow action ('cancel' or 'confirm')
    @type dialog_name: str
    @param expected_transition_message: Expected dialog transition message
    @type expected_transition_message: str
    """
    url_before = self.browser.url

    def tryLegacyAndNew():
      try:
        self.browser.mainForm.submitSelect(
          'select_action', 'Base_doAction:method', label,
          value and '%s?workflow_action=%s' % (script_id, value), **kw)

      except LookupError:
        self.browser.mainForm.submitSelect(
          'select_action', 'Base_doAction:method', label,
          value and '%s?field_my_workflow_action=%s' % (script_id, value), **kw)

      if dialog_name:
        show_dialog_time = self.lastRequestSeconds

        # TODO: Should it fail completely if the dialog could not be found?
        getattr(self.browser.mainForm,
                'submitDialog' + dialog_name.capitalize())()

      if expected_transition_message:
        transition_message = self.browser.getTransitionMessage()
        if transition_message != expected_transition_message:
          raise AssertionError("Expected transition message: %s, got: %s" % \
                                 (expected_transition_message,
                                  transition_message))

      if dialog_name:
        return show_dialog_time

    if maximum_attempt_number == 1:
      return tryLegacyAndNew()
    else:
      show_dialog_time = None
      current_attempt_number = 1
      while True:
        try:
          show_dialog_time = tryLegacyAndNew()
        except (AssertionError, LookupError):
          if current_attempt_number == maximum_attempt_number:
            raise

          current_attempt_number += 1
          time.sleep(sleep_between_attempt)

          # The page needs to be reloaded before the next attempt
          self.browser.open(url_before)
        else:
          break

      wait_time = (current_attempt_number - 1) * sleep_between_attempt
      if show_dialog_time is not None:
        return (show_dialog_time, wait_time)

      return wait_time

  def submitDialogCancel(self):
    """
    Cancel the dialog action. A dialog is showed when validating a
    workflow or deleting an object for example.
    """
    self.submit(name='Base_cancel:method')

  def submitDialogUpdate(self):
    """
    Update the dialog action. A dialog may contain a button to update
    the form before confirming it. See L{submitDialogConfirm} as well.
    """
    self.submit(name='Base_showUpdateDialog:method')

  def submitDialogConfirm(self):
    """
    Confirm the dialog action. A dialog is showed when validating a
    workflow or deleting an object for example.

    @todo: Specifying index is kind of ugly (there is C{dummy} field
           with the same name though)
    """
    self.submit(name='Base_callDialogMethod:method')

  def getListboxControl(self, line_number, column_number, cell_element_index=1,
                        *args, **kwargs):
    """
    Get the control located at line and column numbers (both starting
    from 1), excluding hidden control and those whose class is hidden
    too. The position of a cell from a column or line number can be
    obtained through calling
    L{erp5.util.testbrowser.browser.Browser.getListboxPosition}.

    Also, there may be several elements within a cell, thus
    C{cell_element_index} allows to select which one to get (starting
    from 1).

    @param line_number: Line number of the field
    @type line_number: int
    @param column_number: Column number of the field
    @type column_number: int
    @param cell_element_index: Index of the control to be selected in the cell
    @type cell_element_index: int
    @param args: positional arguments given to the parent C{getControl}
    @type args: list
    @param kwargs: keyword arguments given to the parent C{getControl}
    @type kwargs: dict
    @return: The control found at the given line and column numbers
    @rtype: L{zope.testbrowser.interfaces.IControl}

    @raise LookupError: No control could be found at the given
                        position and cell indexes
    """
    if self.browser._is_legacy_listbox:
      listbox_basic_xpath_str = self.browser._legacy_listbox_table_xpath_str
    else:
      listbox_basic_xpath_str = self.browser._listbox_table_xpath_str

    if line_number <= 2:
      relative_line_number = line_number

      if self.browser._is_legacy_listbox:
        column_type = 'td'
      else:
        column_type = 'th'
    else:
      if self.browser._is_legacy_listbox:
        relative_line_number = line_number
      else:
        relative_line_number = line_number - 2

      column_type = 'td'

    xpath_str = '%s//tbody//tr[%d]//%s[%d]/*[not(@type="hidden") and ' \
        'not(contains(@class, "hidden"))][%d]' % \
        (listbox_basic_xpath_str,
         relative_line_number,
         column_type,
         column_number,
         cell_element_index)

    # xpath() method always return a list even if there is only one element
    element_list = self.browser.etree.xpath(xpath_str)

    try:
      input_element = element_list[0]
      input_name = input_element.get('name')
    except (IndexError, AttributeError):
      input_element = input_name = None

    if input_element is None or not input_name:
      raise LookupError("Could not find control in listbox cell %dx%d (index=%d)" %\
                          (line_number, column_number, cell_element_index))

    control = self.getControl(name=input_element.get('name'), *args, **kwargs)

    # If this is a list control (radio button, checkbox or select
    # control), then get the item from its value
    if isinstance(control, ListControl):
      control = control.getControl(value=input_element.get('value'))
    return control

from zope.testbrowser.browser import SubmitControl

class SubmitControlWithTime(SubmitControl):
  """
  Only define to wrap click methods to measure the time spent
  """
  __metaclass__ = measurementMetaClass(prefix='click')

from zope.testbrowser.browser import ImageControl

class ImageControlWithTime(ImageControl):
  """
  Only define to wrap click methods to measure the time spent
  """
  __metaclass__ = measurementMetaClass(prefix='click')

import zope.testbrowser.browser

browser_simpleControlFactory = zope.testbrowser.browser.simpleControlFactory
def simpleControlFactory(wtcontrol, form, elemindex, browser):
  """
  Monkey patched to get elapsed time on ImageControl and SubmitControl
  """
  import webtest

  elem = elemindex[wtcontrol.pos]
  if isinstance(wtcontrol, webtest.forms.Submit):
    if wtcontrol.attrs.get('type', 'submit') == 'image':
      return ImageControlWithTime(wtcontrol, form, elem, browser)
    else:
      return SubmitControlWithTime(wtcontrol, form, elem, browser)

  return browser_simpleControlFactory(wtcontrol, form, elemindex, browser)

zope.testbrowser.browser.simpleControlFactory = simpleControlFactory

from zope.testbrowser.browser import Link

class LinkWithTime(Link):
  """
  Only define to wrap click methods to measure the time spent
  """
  __metaclass__ = measurementMetaClass(prefix='click')
