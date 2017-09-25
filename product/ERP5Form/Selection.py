##############################################################################
#
# Copyright (c) 2002,2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

from Products.ERP5Type.Globals import InitializeClass, Persistent
import Acquisition
from Acquisition import aq_base
from OFS.Traversable import Traversable
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions as ERP5Permissions
from Products.PythonScripts.Utility import allow_class
from hashlib import md5

# Put a try in front XXX
from Products.CMFCategory.Category import Category
from Products.ERP5.Document.Domain import Domain

from zLOG import LOG

from Products.ERP5Type.Tool.MemcachedTool import MEMCACHED_TOOL_MODIFIED_FLAG_PROPERTY_ID

class Selection(Acquisition.Implicit, Traversable, Persistent):
    """
        Selection

        A Selection instance allows a ListBox object to browse the data
        resulting from a method call such as an SQL Method Call. Selection
        instances are used to implement persistent selections in ERP5.

        Selection uses the following control variables

        - method      --  a method which will be used
                                    to select objects

        - params      --  a dictionnary of parameters to call the
                                    method with

        - sort_on     --  a dictionnary of parameters to sort
                                    the selection

        - uids        --  a list of object uids which defines the
                                    selection

        - invert_mode --  defines the mode of the selection
                                    if mode is 1, then only show the
                                    ob

        - list_url    --  the URL to go back to list mode

        - checked_uids --  a list of uids checked

        - domain_path --  the path to the root of the selection tree


        - domain_list --  the relative path of the current selected domain
                                    XXX this will have to be updated for cartesion product

        - report_path --  the report path

        - report_list -- list of open report nodes
                                    XXX this will have to be updated for cartesion product

        - domain                -- a DomainSelection instance

        - report                -- a DomainSelection instance

        - flat_list_mode  --

        - domain_tree_mode --

        - report_tree_mode --

    """

    method_path=None
    params=None
    sort_on=()
    default_sort_on=()
    uids=()
    invert_mode=0
    list_url=''
    columns=()
    checked_uids=()
    index=None
    domain_path = ('portal_categories',)
    domain_list = ((),)
    report_path = ('portal_categories',)
    report_list = ((),)
    domain=None
    report=None
    report_opened=None

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    security.declarePublic('domain')
    security.declarePublic('report')

    def getId(self):
      return self.name

    def __init__(self, name, method_path=None, params=None, sort_on=None,
                 default_sort_on=None, uids=None, invert_mode=0, list_url='',
                 domain=None, report=None, columns=None, checked_uids=None,
                 index=None):
        if params is None: params = {}
        if sort_on is None: sort_on = []
        if default_sort_on is None: default_sort_on = []
        if uids is None: uids = []
        if columns is None: columns = []
        if checked_uids is None: checked_uids = []
        # XXX Because method_path is an URI, it must be in ASCII.
        #     Shouldn't Zope automatically does this conversion? -yo
        if type(method_path) is type(u'a'):
          method_path = method_path.encode('ascii')
        self.method_path = method_path
        self.params = params
        self.uids = uids
        self.invert_mode = invert_mode
        self.list_url = list_url
        self.columns = columns
        self.sort_on = sort_on
        self.default_sort_on = default_sort_on
        self.checked_uids = checked_uids
        self.name = name
        self.index = index
        self.domain_path = ('portal_categories',)
        self.domain_list = ()
        self.report_path = None
        self.report_list = ()
        self.domain = None
        self.report = None
        self.report_opened = None

    security.declarePrivate('edit')
    def edit(self, params=None, **kw):
        setattr(self, MEMCACHED_TOOL_MODIFIED_FLAG_PROPERTY_ID, True)
        if params is not None:
          # We should only keep params which do not start with field_
          # in order to make sure we do not collect unwanted params
          # resulting form the REQUEST generated by an ERP5Form submit
          params = dict(item for item in params.iteritems()
                        if not item[0].startswith('field_'))
          if self.params != params:
            self.params = params
        if kw is not None:
          for k,v in kw.iteritems():
            if k in ('domain', 'report', 'domain_path', 'report_path', 'domain_list', 'report_list') or v is not None:
              # XXX Because method_path is an URI, it must be in ASCII.
              #     Shouldn't Zope automatically does this conversion? -yo
              if k == 'method_path' and isinstance(v, unicode):
                v = v.encode('ascii')
              if getattr(self, k, None) != v:
                setattr(self, k, v)

    def _p_independent(self) :
      return 1

    def _p_resolveConflict(self, oldState, savedState, newState) :
      """Selection are edited by listboxs, so many conflicts can happen,
         this is a workaround, so that no unnecessary transaction is
         restarted."""
      return newState

    def __call__(self, method=None, context=None, REQUEST=None, params=None):
        """
        Calls the selection and return the list of selected documents
        or objects. Seledction method, context and parameters may be
        overriden in a non persistent way.

        method -- optional method (callable) or method path (string)
                  to use instead of the persistent selection method

        context -- optional context to call the selection method on

        REQUEST -- optional REQUEST parameters (not used, only to
                   provide API compatibility)

        params -- optional parameters which can be used to override
                  default params
        """
        #LOG("Selection", 0, str((self.__dict__)))
        #LOG("Selection", 0, str(method))
        #LOG('Selection', 0, "self.invert_mode = %s" % repr(self.invert_mode))
        if not params:
          kw = self.getParams()
        else:
          kw = params.copy()
          kw.setdefault("ignore_unknown_columns", True)
        # Always remove '-C'-named parameter.
        kw.pop('-C', None)
        if self.invert_mode is not 0:
          kw['uid'] = self.uids
        if method is None or isinstance(method, str):
          method_path = method or self.method_path
          method = context.unrestrictedTraverse(method_path)
        if type(method) is type('a'):
          method = context.unrestrictedTraverse(self.method_path)
        sort_on = getattr(self, 'sort_on', [])
        if len(sort_on) == 0:
          sort_on = getattr(self, 'default_sort_on', [])
        if len(sort_on) > 0:
          kw['sort_on'] = sort_on
        elif kw.has_key('sort_on'):
          del kw['sort_on'] # We should not sort if no sort was defined
        # We should always set selection_name with self.name
        kw['selection_name'] = self.name
        # XXX: Use of selection parameter is deprecated. Use selection_name
        # instead, and access the selection via selection_tool.
        kw['selection'] = self
        if self.domain is not None:
          kw['selection_domain'] = self.domain
        if self.report is not None:
          kw['selection_report'] = self.report
        if callable(method):
          result = method(**kw)
        else:
          result = []
        return result

    def __getitem__(self, index, REQUEST=None):
        return self(REQUEST)[index]

    security.declarePublic('getName')
    def getName(self):
        """
          Get the name of this selection.
        """
        return self.name

    security.declarePublic('getIndex')
    def getIndex(self):
        """
          Get the index of this selection.
        """
        return self.index

    security.declarePublic('getDomain')
    def getDomain(self):
        """
          Get the domain selection of this selection.
        """
        return self.domain

    security.declarePublic('getReport')
    def getReport(self):
        """
          Get the report selection of this selection.
        """
        return self.report

    security.declarePublic('getParams')
    def getParams(self):
        """
          Get a dictionary of parameters in this selection.
        """
        if not isinstance(self.params, dict):
          self.params = {}

        params = self.params.copy()
        params.setdefault("ignore_unknown_columns", True)
        return params

    security.declarePublic('getSortOrder')
    def getSortOrder(self):
        """
          Return sort order stored in selection
        """
        return self.sort_on

    security.declarePublic('getListUrl')
    def getListUrl(self):
        result = ''
        #LOG('getListUrl', 0, 'list_url = %s' % str(self.list_url))
        if self.list_url is None:
          self.list_url = ''
        else:
          result = self.list_url
        return result

    security.declarePublic('getCheckedUids')
    def getCheckedUids(self):
        if not hasattr(self, 'checked_uids'):
          self.checked_uids = []
        elif self.checked_uids is None:
          self.checked_uids = []
        return self.checked_uids

    security.declarePublic('getDomainPath')
    def getDomainPath(self, default=None):
        if self.domain_path is None:
          if default is None:
            self.domain_path = self.getDomainList()[0]
          else:
            self.domain_path = default
        return self.domain_path

    security.declarePublic('getDomainList')
    def getDomainList(self):
        if self.domain_list is None:
          self.domain_list = (('portal_categories',),)
        return self.domain_list

    security.declarePublic('getReportPath')
    def getReportPath(self, default=None):
        if self.report_path is None:
          if default is None:
            self.report_path = self.getReportList()[0]
          else:
            self.report_path = default
        return self.report_path

    security.declarePublic('getZoom')
    def getZoom(self):
      try:
        current_zoom=self.params['zoom']
        if current_zoom != None:
          return current_zoom
        else:
          return 1
      except KeyError:
        return 1

    security.declarePublic('getReportList')
    def getReportList(self):
        if self.report_list is None:
          self.report_list = (('portal_categories',),)
        return self.report_list

    security.declarePublic('isReportOpened')
    def isReportOpened(self):
        if self.report_opened is None:
          self.report_opened = 1
        return self.report_opened

    security.declarePublic('isInvertMode')
    def isInvertMode(self):
        return self.invert_mode

    security.declarePublic('getInvertModeUidList')
    def getInvertModeUidList(self):
        return self.uids

    security.declarePublic('getDomainTreeMode')
    def getDomainTreeMode(self):
        return getattr(self, 'domain_tree_mode', 0)

    security.declarePublic('getReportTreeMode')
    def getReportTreeMode(self):
        return getattr(self, 'report_tree_mode', 0)

    security.declarePublic('getAnonymousSelectionKey')
    def getAnonymousSelectionKey(self):
        return md5(repr({k: v for k, v in self.__dict__.iteritems()
                              if k != 'index'})).hexdigest()

InitializeClass(Selection)
allow_class(Selection)

class DomainSelection(Acquisition.Implicit, Traversable, Persistent):
  """
    A class to store a selection of domains which defines a report
    section.

    Do not use this class directly, but use selection_{domain,report}
    parameters in SQLCatalog API.
  """

  security = ClassSecurityInfo()
  security.declareObjectPublic()

  def __init__(self, domain_dict = None):
    #LOG('DomainSelection', 0, '__init__ is called with %r' % (domain_dict,))
    if domain_dict is not None:
      self.domain_dict = domain_dict
      for k, v in domain_dict.iteritems():
        if k is not None:
          setattr(self, k, v)

  def __len__(self):
    return len(self.domain_dict)

  security.declarePublic('getCategoryList')
  def getCategoryList(self):
    return

  def _getDomainObject(self, portal, domain):
    """Return a domain or category object.
    """
    if isinstance(domain, tuple):
      # This is the new form. The first item describes the name of a tool or
      # None if a domain is under a module. The second item is the relative
      # URL of a domain.
      tool = domain[0]
      if tool is None:
        obj = portal.restrictedTraverse(domain[1])
      elif tool == 'portal_domains':
        # Special case, as Domain Tool may generate a domain dynamically.
        obj = portal.portal_domains.getDomainByPath(domain[1])
      else:
        obj = portal[tool].restrictedTraverse(domain[1])
    elif isinstance(domain, str):
      # XXX backward compatibility: a domain was represented by a string previously.
      obj = portal.portal_domains.getDomainByPath(domain)
    else:
      # XXX backward compatibility: a category was represented by an object itself.
      obj = aq_base(domain).__of__(portal)

    return obj

  security.declarePublic('asDomainDict')
  def asDomainDict(self, domain_id=None, exclude_domain_id=None):
    return self.domain_dict

  security.declarePublic('asDomainItemDict')
  def asDomainItemDict(self, domain_id=None, exclude_domain_id=None):
    domain_item_dict = {}
    portal = self.getPortalObject()
    for k, d in self.domain_dict.iteritems():
      domain_item_dict[k] = self._getDomainObject(portal,d)
    return domain_item_dict

  security.declarePublic('updateDomain')
  def updateDomain(self, domain):
    pass

InitializeClass(DomainSelection)
allow_class(DomainSelection)
