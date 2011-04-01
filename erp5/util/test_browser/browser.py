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
from urlparse import urljoin
from z3c.etestbrowser.browser import ExtendedTestBrowser
from zope.testbrowser.browser import onlyOne

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
    Meta class to define automatically C{time*InSecond} and
    C{time*InPystone} methods automatically according to given
    C{prefix}, and also to define C{lastRequestSeconds} and
    C{lastRequestPystones} on other classes besides of Browser.
    """
    def __new__(metacls, name, bases, dictionary):
      def applyMeasure(method):
        """
        Inner function to add the C{time*InSecond} and C{time*InPystone}
        methods to the dictionary of newly created class.

        For example, if the method name is C{submitSave} then
        C{timeSubmitSaveInSecond} and C{timeSubmitSaveInPystone} will
        be added to the newly created class.

        @param method: Instance method to be called
        @type method: function
        """
        # Upper the first character
        method_name_prefix = 'time' + method.func_name[0].upper() + \
            method.func_name[1:]

        def innerSecond(self, *args, **kwargs):
          """
          Call L{%(name)s} method and return the time it took in seconds.

          @param args: Positional arguments given to L{%(name)s}
          @param kwargs: Keyword arguments given to L{%(name)s}
          """
          method(self, *args, **kwargs)
          return self.lastRequestSeconds

        innerSecond.func_name = method_name_prefix + 'InSecond'
        innerSecond.__doc__ = innerSecond.__doc__ %  {'name': method.func_name}
        dictionary[innerSecond.func_name] = innerSecond

        def innerPystone(self, *args, **kwargs):
          """
          Call L{%(name)s} method and return the time it took in pystones.

          @param args: Positional arguments given to L{%(name)s}
          @param kwargs: Keyword arguments given to L{%(name)s}
          """
          method(self, *args, **kwargs)
          return self.lastRequestPystones

        innerPystone.func_name = method_name_prefix + 'InPystone'
        innerPystone.__doc__ = innerPystone.__doc__ % {'name': method.func_name}
        dictionary[innerPystone.func_name] = innerPystone

      # Create time*InSecond and time*InPystone methods only for the
      # methods prefixed by the given prefix
      for attribute_name, attribute in dictionary.items():
        if attribute_name.startswith(prefix) and callable(attribute):
          applyMeasure(attribute)

      # lastRequestSeconds and lastRequestPystones properties are only
      # defined on classes inheriting from zope.testbrowser.browser.Browser,
      # so create these properties for all other classes too
      if 'Browser' not in bases[0].__name__:
        time_method = lambda self: self.browser.lastRequestSeconds
        time_method.func_name = 'lastRequestSeconds'
        time_method.__doc__ = Browser.lastRequestSeconds.__doc__
        dictionary['lastRequestSeconds'] = property(time_method)

        time_method = lambda self: self.browser.lastRequestPystones
        time_method.func_name = 'lastRequestPystones'
        time_method.__doc__ = Browser.lastRequestPystones.__doc__
        dictionary['lastRequestPystones'] = property(time_method)

      return super(MeasurementMetaClass,
                   metacls).__new__(metacls, name, bases, dictionary)

  return MeasurementMetaClass

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
               base_url,
               erp5_site_id,
               username,
               password,
               log_filename=None,
               is_debug=False):
    """
    Create a browser object, allowing to log in right away with the
    given username and password. The base URL must contain an I{/} at
    the end.

    @param base_url: Base HTTP URL
    @type base_url: str
    @param erp5_site_id: ERP5 site name
    @type erp5_site_id: str
    @param username: Username to be used to log into ERP5
    @type username: str
    @param password: Password to be used to log into ERP5
    @param log_filename: Log filename (stdout if none given)
    @type log_filename: str
    @param is_debug: Enable or disable debugging (disable by default)
    @type is_debug: bool
    """
    # Meaningful to re-create the MainForm class every time the page
    # has been changed
    self._main_form_counter = -1
    self._main_form = None

    assert base_url[-1] == '/'

    self._base_url = base_url
    self._erp5_site_id = erp5_site_id
    self._erp5_base_url = urljoin(self._base_url, self._erp5_site_id) + '/'

    self._username = username
    self._password = password

    # Only display WARNING message if debugging is not enabled
    logging_level = level=(is_debug and logging.DEBUG or logging.WARNING)
    if log_filename:
      logging.basicConfig(filename=log_filename, level=logging_level)
    else:
      logging.basicConfig(stream=sys.stdout, level=logging_level)

    super(Browser, self).__init__()

    # Open login page, then login with the given username and password
    self.open('login_form')
    self.mainForm.submitLogin()

  def open(self, url_or_path=None, data=None):
    """
    Open a relative (to the ERP5 base URL) or absolute URL. If the
    given URL is not given, then it will open the home ERP5 page.

    @param url_or_path: Relative or absolute URL
    @type url_or_path: str
    """
    # In case url_or_path is an absolute URL, urljoin() will return
    # it, otherwise it is a relative path and will be concatenated to
    # ERP5 base URL
    absolute_url = urljoin(self._erp5_base_url, url_or_path)

    logging.info("Opening url: " + absolute_url)
    super(Browser, self).open(absolute_url, data)

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
    for cookie_name, cookie_value in self.cookies.iteritems():
      if name == cookie_name:
        return cookie_value

    return default

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
    if self._main_form_counter == self._counter and self._main_form:
      return self._main_form

    self._main_form_counter = self._counter

    main_form = None
    for form in self.mech_browser.forms():
      if form.attrs.get('id') == 'main_form':
        main_form = form

    if not main_form:
      raise LookupError("Could not get 'main_form'")

    self.mech_browser.form = form
    self._main_form = ContextMainForm(self, form)
    return self._main_form

  def getLink(self, url=None, class_attribute=None, *args, **kwargs):
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

    return super(Browser, self).getLink(url=url, *args, **kwargs)

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
    Parses the current page and returns the value of the portal_status
    message.

    @return: The transition message
    @rtype: str

    @raise LookupError: Not found
    """
    try:
      return self.etree.xpath('//div[@id="transition_message"]')[0].text
    except IndexError:
      raise LookupError("Cannot find div with ID 'transition_message'")

  _listbox_table_xpath_str = '//table[contains(@class, "listbox-table")]'

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
    # With XPATH, the position is context-dependent, therefore, as
    # there the cells are either within a <thead> or <tbody>, the line
    # number must be shifted by the number of header lines (namely 2)
    if line_number <= 2:
      relative_line_number = line_number
      column_type = 'th'
    else:
      relative_line_number = line_number - 2
      column_type = 'td'

    xpath_str = '%s//tr[%d]//%s[%d]//a[not(contains(@class, "hidden"))][%d]' % \
        (self._listbox_table_xpath_str,
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

    # Get all cells in the column (if column_number is given and
    # including header columns) or line (if line_number is given)
    if column_number:
      xpath_str_fmt = self._listbox_table_xpath_str + '//tr//%%s[%d]' % \
          column_number

      column_or_line_xpath_str = "%s | %s" % (xpath_str_fmt % 'th',
                                              xpath_str_fmt % 'td')
    else:
      # With XPATH, the position is context-dependent, therefore, as
      # there the cells are either within a <thead> or <tbody>, the
      # line number must be shifted by the number of header lines
      # (namely 2)
      if line_number <= 2:
        relative_line_number = line_number
        column_type = 'th'
      else:
        relative_line_number = line_number - 2
        column_type = 'td'

      column_or_line_xpath_str = self._listbox_table_xpath_str + '//tr[%d]//%s' %\
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
    activity_counter = self.mech_browser.open_novisit(
      self._erp5_base_url + 'portal_activities/countMessage').read()

    return activity_counter and int(activity_counter) or 0

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
    logging.debug("Submitting (name='%s', label='%s', class='%s')" % \
                    (name, label, class_attribute))

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

  def submitSelect(self, select_name, submit_name, label=None, value=None):
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

    @param select_name: Select control name
    @type select_name: str
    @param submit_name: Submit control name
    @type submit_name: str
    @param label: Label of the option control
    @type label: str
    @param value: Value of the option control
    @type value: str

    @raise LookupError: The select, option or submit control could not
                        be found
    """
    select_control = self.getControl(name=select_name)

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

    logging.debug("select_id='%s', label='%s', value='%s'" % \
                    (select_name, label, value))

    select_control.getControl(label=label, value=value).selected = True
    self.submit(name=submit_name)

  def submitLogin(self):
    """
    Log into ERP5 using the username and password provided in the
    browser. It is assumed that the current page is the login page (by
    calling C{open('login_form')} beforehand).

    This method should rarely be used by scripts as login is already
    performed upon instanciation of Browser class.

    @raise LoginError: Login failed

    @todo: Use information sent back as headers rather than looking
           into the page content?
    """
    logging.debug("Logging in: username='%s', password='%s'" % \
                    (self.browser._username, self.browser._password))

    self.getControl(name='__ac_name').value = self.browser._username
    self.getControl(name='__ac_password').value = self.browser._password
    self.submit()

    if 'Logged In as' not in self.browser.contents:
      raise LoginError

  def submitSelectFavourite(self, label=None, value=None):
    """
    Select and submit a favourite, given either by its label (such as
    I{Log out}) or value (I{/logout}). See L{submitSelect}.
    """
    self.submitSelect('select_favorite', 'Base_doFavorite:method', label, value)

  def submitSelectModule(self, label=None, value=None):
    """
    Select and submit a module, given either by its label (such as
    I{Currencies}) or value (such as I{/glossary_module}). See
    L{submitSelect}.
    """
    self.submitSelect('select_module', 'Base_doModule:method', label, value)

  def submitSelectLanguage(self, label=None, value=None):
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
  def submitJump(self, label=None, value=None):
    """
    Select and submit a jump, given either by its label (such as
    I{Queries}) or value (such as
    I{/person_module/Base_jumpToRelatedObject?portal_type=Foo}). See
    L{submitSelect}.
    """
    self.submitSelect('select_jump', 'Base_doJump:method', label, value)

  def submitSelectAction(self, label=None, value=None):
    """
    Select and submit an action, given either by its label (such as
    I{Add Person}) or value (such as I{add} and I{add Person}). See
    L{submitSelect}.
    """
    self.submitSelect('select_action', 'Base_doAction:method', label, value)

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

  def submitSelectWorkflow(self, label=None, value=None,
                           script_id='viewWorkflowActionDialog'):
    """
    Select and submit a workflow action, given either by its label
    (such as I{Create User}) or value (such as I{create_user_action}
    in I{/Person_viewCreateUserActionDialog?workflow_action=create_user_action},
    with C{script_id=Person_viewCreateUserActionDialog}). See L{submitSelect}.

    When validating an object, L{submitDialogConfirm} allows to
    perform the validation required on the next page.

    @param script_id: Script identifier
    @type script_id: str
    """
    try:
      self.submitSelect('select_action', 'Base_doAction:method', label,
                        value and '%s?workflow_action=%s' % (script_id, value))

    except LookupError:
      self.submitSelect('select_action', 'Base_doAction:method', label,
                        value and '%s?field_my_workflow_action=%s' % (script_id,
                                                                      value))

  def submitDialogCancel(self):
    """
    Cancel the dialog action. A dialog is showed when validating a
    workflow or deleting an object for example.
    """
    self.submit(name='Base_cancel:method')

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
    L{erp5.utils.test_browser.browser.Browser.getListboxPosition}.

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
    if line_number <= 2:
      relative_line_number = line_number
      column_type = 'th'
    else:
      relative_line_number = line_number - 2
      column_type = 'td'

    xpath_str = '%s//tr[%d]//%s[%d]/*[not(@type="hidden") and ' \
        'not(contains(@class, "hidden"))][%d]' % \
        (self.browser._listbox_table_xpath_str,
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
