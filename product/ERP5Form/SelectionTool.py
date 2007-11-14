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

"""
  ERP5 portal_selection tool.
"""

from OFS.Traversable import NotFound
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from Globals import InitializeClass, DTMLFile, PersistentMapping, get_request
from ZTUtils import make_query
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions as ERP5Permissions
from Products.ERP5Form import _dtmldir
from Selection import Selection, DomainSelection
from ZPublisher.HTTPRequest import FileUpload
from email.MIMEBase import MIMEBase
from email import Encoders
from copy import copy
from DateTime import DateTime
import md5
import pickle
import hmac
import random
import re
import string
from zLOG import LOG, WARNING, INFO
from Acquisition import Implicit, aq_base
from Products.ERP5Type.Message import Message
import warnings

_MARKER = []

class SelectionError( Exception ):
    pass

class SelectionTool( BaseTool, UniqueObject, SimpleItem ):
    """
      The SelectionTool object is the place holder for all
      methods and algorithms related to persistent selections
      in ERP5.
    """

    id              = 'portal_selections'
    meta_type       = 'ERP5 Selections'
    portal_type     = 'Selection Tool'
    security = ClassSecurityInfo()

    #
    #   ZMI methods
    #
    manage_options = ( ( { 'label'      : 'Overview'
                         , 'action'     : 'manage_overview'
                         },
                         { 'label'      : 'View Selections'
                         , 'action'     : 'manage_view_selections'
                         },
                         { 'label'      : 'Configure'
                         , 'action'     : 'manage_configure'
                         } ))

    security.declareProtected( ERP5Permissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainSelectionTool', _dtmldir )

    security.declareProtected( ERP5Permissions.ManagePortal
                             , 'manage_view_selections' )
    manage_view_selections = DTMLFile( 'SelectionTool_manageViewSelections', _dtmldir )

    security.declareProtected( ERP5Permissions.ManagePortal
                             , 'manage_configure' )
    manage_configure = DTMLFile( 'SelectionTool_configure', _dtmldir )

    # storages of SelectionTool
    storage_list = ('Persistent Mapping', 'Memcached Tool')

    security.declareProtected( ERP5Permissions.ManagePortal, 'setStorage')
    def setStorage(self, value, RESPONSE=None):
      """
        Set the storage of Selection Tool.
      """
      if value in self.storage_list:
        self.storage = value
      else:
        raise ValueError, 'Given storage type (%s) is now supported.' % (value,)
      if RESPONSE is not None:
        RESPONSE.redirect('%s/manage_configure' % (self.absolute_url()))

    def getStorage(self, default=None):
      if default is None:
        default = self.storage_list[0]
      storage = getattr(aq_base(self), 'storage', default)
      if storage is not default and storage not in self.storage_list:
        storage = self.storage_list[0]
      return storage

    def isMemcachedUsed(self):
      return self.getStorage() == 'Memcached Tool'
      
    def _redirectToOriginalForm(self, REQUEST=None, form_id=None, dialog_id=None,
                                query_string=None,
                                no_reset=False, no_report_depth=False):
      """Redirect to the original form or dialog, using the information given
         as parameters.
         (Actually does not redirect  in the HTTP meaning because of URL
         limitation problems.)

         DEPRECATED parameters :
         query_string is used to transmit parameters from caller to callee.
         If no_reset is True, replace reset parameters with noreset.
         If no_report_depth is True, replace report_depth parameters with
         noreport_depth.
      """
      if REQUEST is None:
        return

      if no_reset and REQUEST.form.has_key('reset'):
        REQUEST.form['noreset'] = REQUEST.form['reset'] # Kept for compatibility - might no be used anymore
        del REQUEST.form['reset']
      if no_report_depth and REQUEST.form.has_key('report_depth'):
        REQUEST.form['noreport_depth'] = REQUEST.form['report_depth'] # Kept for compatibility - might no be used anymore
        del REQUEST.form['report_depth']

      if query_string is not None:
        warnings.warn('DEPRECATED: _redirectToOriginalForm got called with a query_string. The variables must be passed in REQUEST.form.',
                      DeprecationWarning)
      context = REQUEST['PARENTS'][0]
      form_id = dialog_id or REQUEST.get('dialog_id', None) or form_id or REQUEST.get('form_id', 'view')
      return getattr(context, form_id)()

    security.declareProtected(ERP5Permissions.View, 'getSelectionNameList')
    def getSelectionNameList(self, context=None, REQUEST=None):
      """
        Returns the selection names of the current user.
      """
      if self.isMemcachedUsed():
        return []
      return self._getSelectionNameListFromContainer()

    # backward compatibility
    security.declareProtected(ERP5Permissions.View, 'getSelectionNames')
    def getSelectionNames(self, context=None, REQUEST=None):
      warnings.warn("getSelectionNames() is deprecated.\n"
                    "Please use getSelectionNameList() instead.",
                    DeprecationWarning)
      return self.getSelectionNameList(context, REQUEST)

    security.declareProtected(ERP5Permissions.View, 'callSelectionFor')
    def callSelectionFor(self, selection_name, context=None, REQUEST=None):
      if context is None: context = self
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is None:
        return None
      return selection(context=context)

    security.declareProtected(ERP5Permissions.View, 'getSelectionFor')
    def getSelectionFor(self, selection_name, REQUEST=None):
      """
        Returns the selection instance for a given selection_name
      """
      if isinstance(selection_name, (tuple, list)):
        selection_name = selection_name[0]
      selection = self._getSelectionFromContainer(selection_name)
      if selection is not None:
        return selection.__of__(self)

    def __getitem__(self, key):
        return self.getSelectionParamsFor(key)

    security.declareProtected(ERP5Permissions.View, 'setSelectionFor')
    def setSelectionFor(self, selection_name, selection_object, REQUEST=None):
      """
        Sets the selection instance for a given selection_name
      """
      if selection_object != None:
        # Set the name so that this selection itself can get its own name.
        selection_object.edit(name = selection_name)

      if self.getSelectionFor(selection_name) != selection_object:
        self._setSelectionToContainer(selection_name, selection_object)

    security.declareProtected(ERP5Permissions.View, 'getSelectionParamsFor')
    def getSelectionParamsFor(self, selection_name, params=None, REQUEST=None):
      """
        Returns the params in the selection
      """
      if params is None: params = {}
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        if len(selection.params) > 0:
          return selection.getParams()
        else:
          return params
      else:
        return params

    # backward compatibility
    security.declareProtected(ERP5Permissions.View, 'getSelectionParams')
    getSelectionParams = getSelectionParamsFor

    security.declareProtected(ERP5Permissions.View, 'setSelectionParamsFor')
    def setSelectionParamsFor(self, selection_name, params, REQUEST=None):
      """
        Sets the selection params for a given selection_name
      """
      selection_object = self.getSelectionFor(selection_name, REQUEST)
      if selection_object is not None:
        selection_object.edit(params=params)
      else:
        selection_object = Selection(params=params)
      self.setSelectionFor(selection_name, selection_object, REQUEST)

    security.declareProtected(ERP5Permissions.View, 'getSelectionDomainDictFor')
    def getSelectionDomainDictFor(self, selection_name, REQUEST=None):
      """
        Returns the Domain dict for a given selection_name
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        try:
          return selection.getDomain().asDomainDict
        except AttributeError:
          return {}

    security.declareProtected(ERP5Permissions.View, 'getSelectionReportDictFor')
    def getSelectionReportDictFor(self, selection_name, REQUEST=None):
      """
        Returns the Report dict for a given selection_name
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        try:
          return selection.getReport().asDomainDict
        except AttributeError:
          return {}

    security.declareProtected(ERP5Permissions.View, 'setSelectionCheckedUidsFor')
    def setSelectionCheckedUidsFor(self, selection_name, checked_uids, REQUEST=None):
      """
        Sets the checked uids for a given selection_name
      """
      selection_object = self.getSelectionFor(selection_name, REQUEST)
      if selection_object:
        selection_object.edit(checked_uids=checked_uids)
      else:
        selection_object = Selection(checked_uids=checked_uids)
      self.setSelectionFor(selection_name, selection_object, REQUEST)

    security.declareProtected(ERP5Permissions.View, 'updateSelectionCheckedUidList')
    def updateSelectionCheckedUidList(self, selection_name, listbox_uid, uids, REQUEST=None):
      """
        Updates the unchecked uids(listbox_uids) and checked uids (uids)
        for a given selection_name
      """
      if listbox_uid is None:
        listbox_uid = []
      if uids is None:
        uids = []
      self.uncheckAll(selection_name,listbox_uid,REQUEST=REQUEST)
      self.checkAll(selection_name,uids,REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'getSelectionCheckedUidsFor')
    def getSelectionCheckedUidsFor(self, selection_name, REQUEST=None):
      """
        Returns the checked uids for a given selection_name
      """
      selection_object = self.getSelectionFor(selection_name, REQUEST)
      if selection_object:
        #return selection_object.selection_checked_uids
        return selection_object.getCheckedUids()
      return []

    security.declareProtected(ERP5Permissions.View, 'checkAll')
    def checkAll(self, selection_name, listbox_uid=[], REQUEST=None,
                 query_string=None, form_id=None):
      """
        Check uids in a given listbox_uid list for a given selection_name
      """
      selection_object = self.getSelectionFor(selection_name, REQUEST)
      if selection_object:
        selection_uid_dict = {}
        for uid in selection_object.checked_uids:
          selection_uid_dict[uid] = 1
        for uid in listbox_uid:
          try:
            selection_uid_dict[int(uid)] = 1
          except ValueError:
            selection_uid_dict[uid] = 1
        self.setSelectionCheckedUidsFor(selection_name, selection_uid_dict.keys(), REQUEST=REQUEST)
      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST, form_id=form_id,
                                            query_string=query_string, no_reset=True)

    security.declareProtected(ERP5Permissions.View, 'uncheckAll')
    def uncheckAll(self, selection_name, listbox_uid=[], REQUEST=None,
                   query_string=None, form_id=None):
      """
        Uncheck uids in a given listbox_uid list for a given selection_name
      """
      selection_object = self.getSelectionFor(selection_name, REQUEST)
      if selection_object:
        selection_uid_dict = {}
        for uid in selection_object.checked_uids:
          selection_uid_dict[uid] = 1
        for uid in listbox_uid:
          try:
            if selection_uid_dict.has_key(int(uid)): del selection_uid_dict[int(uid)]
          except ValueError:
            if selection_uid_dict.has_key(uid): del selection_uid_dict[uid]
        self.setSelectionCheckedUidsFor(selection_name, selection_uid_dict.keys(), REQUEST=REQUEST)
      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST, form_id=form_id,
                                            query_string=query_string, no_reset=True)

    security.declareProtected(ERP5Permissions.View, 'getSelectionListUrlFor')
    def getSelectionListUrlFor(self, selection_name, REQUEST=None):
      """
        Returns the URL of the list mode of selection instance
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection:
        return selection.getListUrl()
      else:
        return None

    security.declareProtected(ERP5Permissions.View, 'getSelectionInvertModeFor')
    def getSelectionInvertModeFor(self, selection_name, REQUEST=None):
      """Get the 'invert_mode' parameter of a selection.
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        return selection.isInvertMode()
      return 0

    security.declareProtected(ERP5Permissions.View, 'setSelectionInvertModeFor')
    def setSelectionInvertModeFor(self, selection_name,
                                  invert_mode, REQUEST=None):
      """Change the 'invert_mode' parameter of a selection.
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        selection.edit(invert_mode=invert_mode)

    security.declareProtected(ERP5Permissions.View, 'getSelectionInvertModeUidListFor')
    def getSelectionInvertModeUidListFor(self, selection_name, REQUEST=None):
      """Get the 'invert_mode' parameter of a selection.
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        return selection.getInvertModeUidList()
      return 0

    security.declareProtected(ERP5Permissions.View, 'getSelectionIndexFor')
    def getSelectionIndexFor(self, selection_name, REQUEST=None):
      """Get the 'index' parameter of a selection.
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        return selection.getIndex()
      return None

    security.declareProtected(ERP5Permissions.View, 'setSelectionToIds')
    def setSelectionToIds(self, selection_name, selection_uids, REQUEST=None):
      """
        Sets the selection to a small list of uids of documents
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        selection.edit(invert_mode=1, uids=selection_uids, checked_uids=selection_uids)

    security.declareProtected(ERP5Permissions.View, 'setSelectionToAll')
    def setSelectionToAll(self, selection_name, REQUEST=None,
                          reset_domain_tree=False, reset_report_tree=False):
      """
        Resets the selection
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        selection.edit(invert_mode=0, params={}, checked_uids=[], report_opened=1)
        if reset_domain_tree:
          selection.edit(domain=None, domain_path=None, domain_list=None)
        if reset_report_tree:
          selection.edit(report=None, report_path=None, report_list=None)

    security.declareProtected(ERP5Permissions.View, 'setSelectionSortOrder')
    def setSelectionSortOrder(self, selection_name, sort_on, REQUEST=None):
      """
        Defines the sort order of the selection
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        selection.edit(sort_on=sort_on)

    security.declareProtected(ERP5Permissions.View, 'setSelectionQuickSortOrder')
    def setSelectionQuickSortOrder(self, selection_name, sort_on, REQUEST=None,
                                   query_string=None, form_id=None):
      """
        Defines the sort order of the selection directly from the listbox
        In this method, sort_on is just a string that comes from url
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        current_sort_on = self.getSelectionSortOrder(selection_name)
        # We must first switch from asc to desc and vice-versa if sort_order exists
        # in selection
        n = 0
        for current in current_sort_on:
          if current[0] == sort_on:
            n = 1
            if current[1] == 'ascending':
              new_sort_on = [(sort_on, 'descending')]
              break
            else:
              new_sort_on = [(sort_on,'ascending')]
              break
        # And if no one exists, we just set ascending sort
        if n == 0:
          new_sort_on = [(sort_on,'ascending')]
        selection.edit(sort_on=new_sort_on)

      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST, form_id=form_id,
                                            query_string=query_string, no_reset=True)

    security.declareProtected(ERP5Permissions.View, 'getSelectionSortOrder')
    def getSelectionSortOrder(self, selection_name, REQUEST=None):
      """
        Returns the sort order of the selection
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is None: return ()
      return selection.sort_on

    security.declareProtected(ERP5Permissions.View, 'setSelectionColumns')
    def setSelectionColumns(self, selection_name, columns, REQUEST=None):
      """
        Defines the columns in the selection
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      selection.edit(columns=columns)

    security.declareProtected(ERP5Permissions.View, 'getSelectionColumns')
    def getSelectionColumns(self, selection_name, columns=None, REQUEST=None):
      """
        Returns the columns in the selection if not empty, otherwise
        returns the value of columns argument
      """
      if columns is None: columns = []
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        if len(selection.columns) > 0:
          return selection.columns
      return columns


    security.declareProtected(ERP5Permissions.View, 'setSelectionStats')
    def setSelectionStats(self, selection_name, stats, REQUEST=None):
      """
        Defines the stats in the selection
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      selection.edit(stats=stats)

    security.declareProtected(ERP5Permissions.View, 'getSelectionStats')
    def getSelectionStats(self, selection_name, stats=_MARKER, REQUEST=None):
      """
        Returns the stats in the selection
      """
      if stats is not _MARKER:
        default_stats = stats
      else:
        default_stats = [' '] * 6
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        return getattr(aq_base(selection), 'stats', default_stats)
      return default_stats


    security.declareProtected(ERP5Permissions.View, 'viewFirst')
    def viewFirst(self, selection_index='', selection_name='', form_id='view', REQUEST=None):
      """
        Access first item in a selection
      """
      if not REQUEST:
        REQUEST = get_request()
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection:
        method = self.unrestrictedTraverse(selection.method_path)
        selection_list = selection(method = method, context=self, REQUEST=REQUEST)
        if len(selection_list):
          o = selection_list[0]
          url = o.absolute_url()
        else:
          url = REQUEST.getURL()  
      else:
        url = REQUEST.getURL()
      url = '%s/%s?selection_index=%s&selection_name=%s' % (url, form_id, 0, selection_name)
      REQUEST.RESPONSE.redirect(url)

    security.declareProtected(ERP5Permissions.View, 'viewLast')
    def viewLast(self, selection_index='', selection_name='', form_id='view', REQUEST=None):
      """
        Access last item in a selection
      """
      if not REQUEST:
        REQUEST = get_request()
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection:
        method = self.unrestrictedTraverse(selection.method_path)
        selection_list = selection(method = method, context=self, REQUEST=REQUEST)
        if len(selection_list):
          o = selection_list[-1]
          url = o.absolute_url()
        else:
          url = REQUEST.getURL()
      else:
        url = REQUEST.getURL()
      url = '%s/%s?selection_index=%s&selection_name=%s' % (url, form_id, -1, selection_name)
      REQUEST.RESPONSE.redirect(url)

    security.declareProtected(ERP5Permissions.View, 'viewNext')
    def viewNext(self, selection_index='', selection_name='', form_id='view', REQUEST=None):
      """
        Access next item in a selection
      """
      if not REQUEST:
        REQUEST = get_request()
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection:
        method = self.unrestrictedTraverse(selection.method_path)
        selection_list = selection(method = method, context=self, REQUEST=REQUEST)
        if len(selection_list):
          o = selection_list[(int(selection_index) + 1) % len(selection_list)]
          url = o.absolute_url()
        else:
          url = REQUEST.getURL()
      else:
        url = REQUEST.getURL()
      url = '%s/%s?selection_index=%s&selection_name=%s' % (url, form_id, int(selection_index) + 1, selection_name)
      REQUEST.RESPONSE.redirect(url)

    security.declareProtected(ERP5Permissions.View, 'viewPrevious')
    def viewPrevious(self, selection_index='', selection_name='', form_id='view', REQUEST=None):
      """
        Access previous item in a selection
      """
      if not REQUEST:
        REQUEST = get_request()
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection:
        method = self.unrestrictedTraverse(selection.method_path)
        selection_list = selection(method = method, context=self, REQUEST=REQUEST)
        if len(selection_list):
          o = selection_list[(int(selection_index) - 1) % len(selection_list)]
          url = o.absolute_url()
        else:
          url = REQUEST.getURL()
      else:
        url = REQUEST.getURL()
      url = '%s/%s?selection_index=%s&selection_name=%s' % (url, form_id, int(selection_index) - 1, selection_name)
      REQUEST.RESPONSE.redirect(url)


    # ListBox related methods

    security.declareProtected(ERP5Permissions.View, 'firstPage')
    def firstPage(self, list_selection_name, listbox_uid, uids=None, REQUEST=None):
      """
        Access the first page of a list
      """
      if uids is None: uids = []
      selection = self.getSelectionFor(list_selection_name, REQUEST)
      REQUEST.form['list_start'] = 0
      self.uncheckAll(list_selection_name, listbox_uid)
      return self.checkAll(list_selection_name, uids, REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'lastPage')
    def lastPage(self, list_selection_name, listbox_uid, uids=None, REQUEST=None):
      """
        Access the last page of a list
      """
      if uids is None: uids = []
      selection = self.getSelectionFor(list_selection_name, REQUEST)
      params = selection.getParams()
      # XXX This will not work if the number of lines shown in the listbox is greater
      #       than the BIG_INT constan. Such a case has low probability but is not
      #       impossible. If you are in this case, send me a mail ! -- Kev
      BIG_INT = 10000000
      last_page_start = BIG_INT
      total_lines = REQUEST.form.get('total_size', BIG_INT)
      if total_lines != BIG_INT:
        lines_per_page  = params.get('list_lines', 1)
        last_page_start = int(total_lines) - (int(total_lines) % int(lines_per_page))
      REQUEST.form['list_start'] = last_page_start
      self.uncheckAll(list_selection_name, listbox_uid)
      return self.checkAll(list_selection_name, uids, REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'nextPage')
    def nextPage(self, list_selection_name, listbox_uid, uids=None, REQUEST=None):
      """
        Access the next page of a list
      """
      if uids is None: uids = []
      selection = self.getSelectionFor(list_selection_name, REQUEST)
      params = selection.getParams()
      lines = params.get('list_lines', 0)
      start = params.get('list_start', 0)
      REQUEST.form['list_start'] = int(start) + int(lines)
      self.uncheckAll(list_selection_name, listbox_uid)
      return self.checkAll(list_selection_name, uids, REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'previousPage')
    def previousPage(self, list_selection_name, listbox_uid, uids=None, REQUEST=None):
      """
        Access the previous page of a list
      """
      if uids is None: uids = []
      selection = self.getSelectionFor(list_selection_name, REQUEST)
      params = selection.getParams()
      lines = params.get('list_lines', 0)
      start = params.get('list_start', 0)
      REQUEST.form['list_start'] = max(int(start) - int(lines), 0)
      self.uncheckAll(list_selection_name, listbox_uid)
      return self.checkAll(list_selection_name, uids, REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'setPage')
    def setPage(self, list_selection_name, listbox_uid, query_string=None, uids=None, REQUEST=None):
      """
         Sets the current displayed page in a selection
      """
      if uids is None: uids = []
      selection = self.getSelectionFor(list_selection_name, REQUEST)
      params = selection.getParams()
      params['list_start'] = REQUEST.form.get('list_start', 0)
      selection.edit(params=params)
      self.uncheckAll(list_selection_name, listbox_uid)
      return self.checkAll(list_selection_name, uids, REQUEST=REQUEST, query_string=query_string)

    # PlanningBox related methods
    security.declareProtected(ERP5Permissions.View, 'setZoomLevel')
    def setZoomLevel(self, uids=None, REQUEST=None, form_id=None,
                     query_string=None):
      """
      Set graphic zoom level in PlanningBox
      """
      if uids is None:
        uids = []
      request = REQUEST
      selection_name=request.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        params = selection.getParams()
        zoom_level = request.form.get('zoom_level', None)
        if zoom_level is None:
          # If zoom_level is not defined try to 
          # use the last one from params
          zoom_level =  params.get('zoom_level', 1)

        # for keep compatibility with the old zoom        
        zoom_start = request.form.get('zoom_start',0)
        if zoom_level <= zoom_start:
          zoom_start = max(int(float(zoom_level)),1) - 1
          params['zoom_start'] = zoom_start   

        # XXX URL currently pass string parameter and not int
        # This is a dirty fix!
        # It should be fixed by cleaning the date zoom level
        # in a generic way
        zoom_level = int(zoom_level)
        zoom_begin = request.form.get('zoom_begin', None)
        #zoom_end = request.form.get('zoom_end', None)
        zoom_date_start = request.form.get('zoom_date_start', None)
        if zoom_date_start is not None:
          zoom_begin = zoom_date_start
        if zoom_begin is None:
          zoom_begin = params.get('zoom_begin', None)
        params['zoom_level'] = zoom_level
        # Calculating New zoom Dates Range.
        validate_method = getattr(self, 'planning_validate_date_list', None)
        date_range = validate_method(zoom_begin,zoom_level)
        params['from_date'] = params['zoom_begin'] = date_range[0]
        params['to_date'] = params['zoom_end'] = date_range[1]
        selection.edit(params=params)
      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST,
                                            form_id=form_id,
                                            query_string=query_string)

    security.declareProtected(ERP5Permissions.View, 'setZoom')
    def setZoom(self, uids=None, REQUEST=None, form_id=None, query_string=None):
      """
      Set graphic zoom in PlanningBox
      """
      if uids is None: uids = []
      request = REQUEST
      selection_name=request.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        params = selection.getParams()
        zoom_start = request.form.get('zoom_start',0)
        params['zoom_start'] = zoom_start
        selection.edit(params= params)
      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST, form_id=form_id,
                                           query_string=query_string)

    security.declareProtected(ERP5Permissions.View, 'nextZoom')
    def nextZoom(self, uids=None, REQUEST=None, form_id=None, query_string=None):
      """
      Set next graphic zoom start in PlanningBox
      """
      if uids is None:
        uids = []
      request = REQUEST
      selection_name=request.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        params = selection.getParams()
        zoom_level =  params.get('zoom_level', 1)
        zoom_variation = + 1
        zoom_begin = request.form.get('zoom_begin', None)
        
        # for keep the compatibility
        zoom_start = params.get('zoom_start',0)
        params['zoom_start'] = int(zoom_start) + 1

        if zoom_begin is None:
          zoom_begin = params.get('zoom_begin', None)
        validate_method = getattr(self, 'planning_validate_date_list', None)
        date_range = validate_method(zoom_begin,zoom_level,zoom_variation)
        params['zoom_begin'] = params['from_date'] = date_range[0]
        params['zoom_end'] = params['to_date'] = date_range[1]
        selection.edit(params=params)
      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST,
                                            form_id=form_id,
                                             query_string=query_string)

    security.declareProtected(ERP5Permissions.View, 'previousZoom')
    def previousZoom(self, uids=None, REQUEST=None, form_id=None, query_string=None):
      """
      Set previous graphic zoom in PlanningBox
      """
      if uids is None:
        uids = []
      request = REQUEST
      selection_name=request.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        params = selection.getParams()
        zoom_level =  params.get('zoom_level', 1)
        zoom_variation = -1
        zoom_begin = request.form.get('zoom_begin', None)

        # for keep the compatibility
        zoom_start = params.get('zoom_start',0)
        params['zoom_start'] = int(zoom_start) - 1

        if zoom_begin is None:
          zoom_begin = params.get('zoom_begin', None)
        validate_method = getattr(self, 'planning_validate_date_list', None)
        date_range = validate_method(zoom_begin,zoom_level,zoom_variation)
        params['zoom_begin'] = params['from_date'] = date_range[0]
        params['zoom_end'] = params['to_date'] = date_range[1]
        selection.edit(params=params)
      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST,
                                            form_id=form_id,
                                             query_string=query_string)
    
    security.declareProtected(ERP5Permissions.View, 'setDomainRoot')
    def setDomainRoot(self, REQUEST, form_id=None, query_string=None):
      """
        Sets the root domain for the current selection
      """
      selection_name = REQUEST.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)
      root_url = REQUEST.form.get('domain_root_url','portal_categories')
      selection.edit(domain_path=root_url, domain_list=())

      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST, form_id=form_id,
                                            query_string=query_string)

    security.declareProtected(ERP5Permissions.View, 'setDomainRootFromParam')
    def setDomainRootFromParam(self, REQUEST, selection_name, domain_root):
      if REQUEST is None:
        return
      selection = self.getSelectionFor(selection_name, REQUEST)
      selection.edit(domain_path=domain_root, domain_list=())

    security.declareProtected(ERP5Permissions.View, 'unfoldDomain')
    def unfoldDomain(self, REQUEST, form_id=None, query_string=None):
      """
        Unfold domain for the current selection
      """
      selection_name = REQUEST.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)
      domain_url = REQUEST.form.get('domain_url',None)
      domain_depth = REQUEST.form.get('domain_depth',0)
      domain_list = list(selection.getDomainList())
      domain_list = domain_list[0:min(domain_depth, len(domain_list))]
      if isinstance(domain_url, str):
        selection.edit(domain_list = domain_list + [domain_url])

      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST, form_id=form_id,
                                            query_string=query_string)

    security.declareProtected(ERP5Permissions.View, 'foldDomain')
    def foldDomain(self, REQUEST, form_id=None, query_string=None):
      """
        Fold domain for the current selection
      """
      selection_name = REQUEST.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)
      domain_url = REQUEST.form.get('domain_url',None)
      domain_depth = REQUEST.form.get('domain_depth',0)
      domain_list = list(selection.getDomainList())
      domain_list = domain_list[0:min(domain_depth, len(domain_list))]
      selection.edit(domain_list=[x for x in domain_list if x != domain_url])

      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST, form_id=form_id,
                                            query_string=query_string)


    security.declareProtected(ERP5Permissions.View, 'setReportRoot')
    def setReportRoot(self, REQUEST, form_id=None, query_string=None):
      """
        Sets the root report for the current selection
      """
      selection_name = REQUEST.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)
      root_url = REQUEST.form.get('report_root_url','portal_categories')
      selection.edit(report_path=root_url, report_list=())

      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST, form_id=form_id,
                                            query_string=query_string)

    security.declareProtected(ERP5Permissions.View, 'unfoldReport')
    def unfoldReport(self, REQUEST, form_id=None, query_string=None):
      """
        Unfold report for the current selection
      """
      selection_name = REQUEST.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)
      report_url = REQUEST.form.get('report_url',None)
      if type(report_url) == type('a'):
        selection.edit(report_list=list(selection.getReportList()) + [report_url])

      return self._redirectToOriginalForm(REQUEST=REQUEST, form_id=form_id,
                                          query_string=query_string,
                                          no_report_depth=True)

    security.declareProtected(ERP5Permissions.View, 'foldReport')
    def foldReport(self, REQUEST, form_id=None, query_string=None):
      """
        Fold domain for the current selection
      """
      selection_name = REQUEST.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)
      report_url = REQUEST.form.get('report_url',None)
      if type(report_url) == type('a'):
        report_list = selection.getReportList()
        selection.edit(report_list=[x for x in report_list if x != report_url])

      return self._redirectToOriginalForm(REQUEST=REQUEST, form_id=form_id,
                                          query_string=query_string,
                                          no_report_depth=True)

    security.declareProtected(ERP5Permissions.View, 'getListboxDisplayMode')
    def getListboxDisplayMode(self, selection_name, REQUEST=None):
      if REQUEST is None:
        REQUEST = get_request()
      selection = self.getSelectionFor(selection_name, REQUEST)

      if getattr(selection, 'report_tree_mode', 0):
        return 'ReportTreeMode'
      elif getattr(selection, 'domain_tree_mode', 0):
        return 'DomainTreeMode'
      return 'FlatListMode'

    security.declareProtected(ERP5Permissions.View, 'setListboxDisplayMode')
    def setListboxDisplayMode(self, REQUEST, listbox_display_mode,
                              selection_name=None, redirect=0,
                              form_id=None, query_string=None):
      """
        Toggle display of the listbox
      """
      request = REQUEST
      # XXX FIXME
      # Dirty fix: we must be able to change the display mode of a listbox
      # in form_view
      # But, form can have multiple listbox...
      # This need to be cleaned
      # Beware, this fix may break the report system...
      # and we don't have test for this
      # Possible fix: currently, display mode icon are implemented as
      # method. It could be easier to generate them as link (where we
      # can define explicitely parameters through the url).
      try:
        list_selection_name = request.list_selection_name
      except AttributeError:
        pass
      else:
        if list_selection_name is not None:
          selection_name = request.list_selection_name
      # Get the selection
      selection = self.getSelectionFor(selection_name, REQUEST)
      if selection is None:
        selection = Selection()
        self.setSelectionFor(selection_name, selection, REQUEST=REQUEST)

      if listbox_display_mode == 'FlatListMode':
        flat_list_mode = 1
        domain_tree_mode = 0
        report_tree_mode = 0
      elif listbox_display_mode == 'DomainTreeMode':
        flat_list_mode = 0
        domain_tree_mode = 1
        report_tree_mode = 0
      elif listbox_display_mode == 'ReportTreeMode':
        flat_list_mode = 0
        domain_tree_mode = 0
        report_tree_mode = 1
      else:
        flat_list_mode = 0
        domain_tree_mode = 0
        report_tree_mode = 0

      selection.edit(flat_list_mode=flat_list_mode,
                     domain_tree_mode=domain_tree_mode,
                     report_tree_mode=report_tree_mode)
      # It is better to reset the query when changing the display mode.
      params = selection.getParams()
      if 'where_expression' in params: del params['where_expression']
      selection.edit(params = params)

      if redirect:
        return self._redirectToOriginalForm(REQUEST=request, form_id=form_id,
                                            query_string=query_string,
                                            no_reset=True)

    security.declareProtected(ERP5Permissions.View, 'setFlatListMode')
    def setFlatListMode(self, REQUEST, selection_name=None):
      """
        Set display of the listbox to FlatList mode
      """
      return self.setListboxDisplayMode(
                       REQUEST=REQUEST, listbox_display_mode='FlatListMode',
                       selection_name=selection_name, redirect=1)

    security.declareProtected(ERP5Permissions.View, 'setDomainTreeMode')
    def setDomainTreeMode(self, REQUEST, selection_name=None):
      """
         Set display of the listbox to DomainTree mode
      """
      return self.setListboxDisplayMode(
                       REQUEST=REQUEST, listbox_display_mode='DomainTreeMode',
                       selection_name=selection_name, redirect=1)

    security.declareProtected(ERP5Permissions.View, 'setReportTreeMode')
    def setReportTreeMode(self, REQUEST, selection_name=None):
      """
        Set display of the listbox to ReportTree mode
      """
      return self.setListboxDisplayMode(
                       REQUEST=REQUEST, listbox_display_mode='ReportTreeMode',
                       selection_name=selection_name, redirect=1)

    security.declareProtected(ERP5Permissions.View, 'getSelectionSelectedValueList')
    def getSelectionSelectedValueList(self, selection_name, REQUEST=None, selection_method=None, context=None):
      """
        Get the list of values selected for 'selection_name'
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is None:
        return []
      return selection(method=selection_method, context=context, REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'getSelectionCheckedValueList')
    def getSelectionCheckedValueList(self, selection_name, REQUEST=None):
      """
        Get the list of values checked for 'selection_name'
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is None:
        return []
      uid_list = selection.getCheckedUids()
      value_list = self.portal_catalog.getObjectList(uid_list)
      return value_list

    security.declareProtected(ERP5Permissions.View, 'getSelectionValueList')
    def getSelectionValueList(self, selection_name, REQUEST=None, selection_method=None, context=None):
      """
        Get the list of values checked or selected for 'selection_name'
      """
      value_list = self.getSelectionCheckedValueList(selection_name, REQUEST=REQUEST)
      if len(value_list) == 0:
        value_list = self.getSelectionSelectedValueList(
                                            selection_name,
                                            REQUEST=REQUEST,
                                            selection_method=selection_method,
                                            context=context)
      return value_list

    security.declareProtected(ERP5Permissions.View, 'getSelectionUidList')
    def getSelectionUidList(self, selection_name, REQUEST=None, selection_method=None, context=None):
      """
        Get the list of values checked or selected for 'selection_name'
      """
      return [x.getObject().getUid() for x in self.getSelectionValueList(selection_name, REQUEST=REQUEST, selection_method=selection_method, context=context)]

    security.declareProtected(ERP5Permissions.View, 'selectionHasChanged')
    def selectionHasChanged(self, md5_string, object_uid_list):
      """
        We want to be sure that the selection did not change
      """
      # XXX To avoid the difference of the string representations of int and long,
      # convert each element to a string.
      object_uid_list = [str(x) for x in object_uid_list]
      object_uid_list.sort()
      new_md5_string = md5.new(str(object_uid_list)).hexdigest()
      return md5_string != new_md5_string

    security.declareProtected(ERP5Permissions.View, 'getPickle')
    def getPickle(self,**kw):
      """
      we give many keywords and we will get the corresponding
      pickle string
      """
      #LOG('getPickle kw',0,kw)
      # XXX Remove DateTime, This is really bad, only use for zope 2.6
      # XXX This has to be removed as quickly as possible
      for k,v in kw.items():
        if isinstance(v,DateTime):
          del kw[k]
      # XXX End of the part to remove
      #LOG('SelectionTool.getPickle, kw',0,kw)
      pickle_string = pickle.dumps(kw)
      msg = MIMEBase('application','octet-stream')
      msg.set_payload(pickle_string)
      Encoders.encode_base64(msg)
      pickle_string = msg.get_payload()
      pickle_string = pickle_string.replace('\n','@@@')
      return pickle_string

    security.declareProtected(ERP5Permissions.View, 'getPickleAndSignature')
    def getPickleAndSignature(self,**kw):
      """
      we give many keywords and we will get the corresponding
      pickle string and signature
      """
      cookie_password = self._getCookiePassword()
      pickle_string = self.getPickle(**kw)
      signature = hmac.new(cookie_password,pickle_string).hexdigest()
      return (pickle_string,signature)

    security.declareProtected(ERP5Permissions.View, 'getObjectFromPickle')
    def getObjectFromPickle(self,pickle_string):
      """
      get object from a pickle string
      """
      object = None
      pickle_string = pickle_string.replace('@@@','\n')
      msg = MIMEBase('application','octet-stream')
      Encoders.encode_base64(msg)
      msg.set_payload(pickle_string)
      pickle_string = msg.get_payload(decode=1)
      object = pickle.loads(pickle_string)
      return object

    security.declareProtected(ERP5Permissions.View, 'getObjectFromPickleAndSignature')
    def getObjectFromPickleAndSignature(self,pickle_string,signature):
      """
      get object from a pickle string only when a signature maches
      """
      cookie_password = self._getCookiePassword()
      object = None
      new_signature = hmac.new(cookie_password,pickle_string).hexdigest()
      if new_signature==signature:
        object = self.getObjectFromPickle(pickle_string)
      return object

    security.declarePrivate('_getCookiePassword')
    def _getCookiePassword(self):
      """
      get the password used for encryption
      """
      cookie_password = getattr(self,'cookie_password',None)
      if cookie_password is None:
        cookie_password = str(random.randrange(1,2147483600))
        self.cookie_password = cookie_password
      return cookie_password

    security.declareProtected(ERP5Permissions.View, 'setCookieInfo')
    def setCookieInfo(self,request,cookie_name,**kw):
      """
      register info directly in cookie
      """
      cookie_name = cookie_name + '_cookie'
      (pickle_string,signature) = self.getPickleAndSignature(**kw)
      request.RESPONSE.setCookie(cookie_name,pickle_string,max_age=15*60)
      signature_cookie_name = cookie_name + '_signature'
      request.RESPONSE.setCookie(signature_cookie_name,signature,max_age=15*60)

    security.declareProtected(ERP5Permissions.View, 'getCookieInfo')
    def getCookieInfo(self,request,cookie_name):
      """
      get info directly from cookie
      """
      cookie_name = cookie_name + '_cookie'
      object = None
      if getattr(request,cookie_name,None) is not None:
        pickle_string = request.get(cookie_name)
        signature_cookie_name = cookie_name + '_signature'
        signature = request.get(signature_cookie_name)
        object = self.getObjectFromPickleAndSignature(pickle_string,signature)
      if object is None:
        object = {}
      return object

    # Related document searching
    def viewSearchRelatedDocumentDialog(self, index, form_id,
                                        REQUEST=None, sub_index=None, **kw):
      """
      Returns a search related document dialog
      A set of forwarders us defined to circumvent limitations of HTML
      """
      if sub_index != None:
        REQUEST.form['sub_index'] = sub_index
      object_path = REQUEST.form['object_path']
      # Find the object which needs to be updated
      o = self.restrictedTraverse(object_path)
      # Find the field which was clicked on
      # Important to get from the object instead of self
      form = getattr(o, form_id)
      field = None
      # Search the correct field
      relation_field_found = 0
      relation_index = 0
      # XXX may be should support another parameter,
      for field in form.get_fields(include_disabled=0):
        if field.get_value('editable', REQUEST=REQUEST):
          try:
           field.get_value('is_relation_field')
          except KeyError:
            pass
          else:
            if index == relation_index:
              relation_field_found = 1
              break
            else:
              relation_index += 1
      if not relation_field_found:
        # We didn't find the field...
        raise SelectionError, "SelectionTool: can not find the relation" \
                              " field %s" % index
      else:
        # Field found
        field_key = field.generate_field_key()
        field_value = REQUEST.form[field_key]
        # XXX Hardcoded form name
        dialog_id = 'Base_viewRelatedObjectList'
        redirect_form = getattr(o, dialog_id)
        # XXX Hardcoded listbox field
        selection_name = redirect_form.listbox.get_value('selection_name')
        # Reset current selection
        self.portal_selections.setSelectionFor(selection_name, None)


        if (field.get_value('is_multi_relation_field')) and \
           (sub_index is None):
          # user click on the wheel, not on the validation button
          # we need to facilitate user search

          # first: store current field value in the selection
          base_category = field.get_value('base_category')

          property_get_related_uid_method_name = \
            "get%sUidList" % ''.join(['%s%s' % (x[0].upper(), x[1:]) \
                                      for x in base_category.split('_')])
          current_uid_list = getattr(o, property_get_related_uid_method_name)\
                               (portal_type=[x[0] for x in \
                                  field.get_value('portal_type')])
          # Checked current uid
          kw ={}
          kw[field.get_value('catalog_index')] = field_value
          self.portal_selections.setSelectionParamsFor(selection_name,
                                                       kw.copy())
          self.portal_selections.setSelectionCheckedUidsFor(
                                             selection_name,
                                             current_uid_list)
          field_value = str(field_value).splitlines()
          REQUEST.form[field_key] = field_value
          portal_status_message = Message(
                          domain='erp5_ui',
                          message="Please select one (or more) object.")
        else:
          portal_status_message = Message(domain='erp5_ui',
                                          message="Please select one object.")


        # Save the current REQUEST form
        # We can't put FileUpload instances because we can't pickle them
        pickle_kw = {}
        for key in REQUEST.form.keys():
          if not isinstance(REQUEST.form[key],FileUpload):
            pickle_kw[key] = REQUEST.form[key]
        form_pickle, form_signature = self.getPickleAndSignature(**pickle_kw)

        base_category = None
        kw = {}
        kw['dialog_id'] = dialog_id
        kw['selection_name'] = selection_name
        kw['selection_index'] = 0 # We start on the first page
        kw['field_id'] = field.id
        kw['portal_type'] = [x[0] for x in field.get_value('portal_type')]
        parameter_list = field.get_value('parameter_list')
        if len(parameter_list) > 0:
          for k,v in parameter_list:
            kw[k] = v
        kw['reset'] = 0
        kw['base_category'] = field.get_value( 'base_category')
        kw['cancel_url'] = REQUEST.get('HTTP_REFERER')
        kw['form_id'] = form_id
        kw[field.get_value('catalog_index')] = field_value
        kw['portal_status_message'] = portal_status_message
        kw['form_pickle'] = form_pickle
        kw['form_signature'] = form_signature

         # Empty the selection (uid)
        REQUEST.form = kw # New request form
        # Define new HTTP_REFERER
        REQUEST.HTTP_REFERER = '%s/%s' % (o.absolute_url(),
                                          dialog_id)

        # If we are called from a Web Site, we should return
        # in the context of the Web Section
        if self.getApplicableLayout() is not None:
          return getattr(o.__of__(self.getWebSectionValue()), dialog_id)(REQUEST=REQUEST)
        # Return the search dialog
        return getattr(o, dialog_id)(REQUEST=REQUEST)

    security.declarePublic('buildSQLJoinExpressionFromDomainSelection')
    def buildSQLJoinExpressionFromDomainSelection(self, selection_domain,
                                                  domain_id=None,
                                                  exclude_domain_id=None,
                                                  category_table_alias='category'):
      if isinstance(selection_domain, DomainSelection):
        warnings.warn("To pass a DomainSelection instance is deprecated.\n"
                      "Please use a domain dict instead.",
                      DeprecationWarning)
      else:
        selection_domain = DomainSelection(selection_domain).__of__(self)
      return selection_domain.asSQLJoinExpression(
          category_table_alias=category_table_alias)

    security.declarePublic('buildSQLExpressionFromDomainSelection')
    def buildSQLExpressionFromDomainSelection(self, selection_domain,
                                              table_map=None, domain_id=None,
                                              exclude_domain_id=None,
                                              strict_membership=0,
                                              join_table="catalog",
                                              join_column="uid",
                                              base_category=None,
                                              category_table_alias='category'):
      if isinstance(selection_domain, DomainSelection):
        warnings.warn("To pass a DomainSelection instance is deprecated.\n"
                      "Please use a domain dict instead.",
                      DeprecationWarning)
      else:
        selection_domain = DomainSelection(selection_domain).__of__(self)
      return selection_domain.asSQLExpression(
          strict_membership = strict_membership,
          join_table=join_table,
          join_column=join_column,
          base_category=base_category,
          category_table_alias = category_table_alias)

    def _aq_dynamic(self, name):
      """
        Generate viewSearchRelatedDocumentDialog0,
                 viewSearchRelatedDocumentDialog1,... if necessary
      """
      aq_base_name = getattr(aq_base(self), name, None)
      if aq_base_name == None:
        DYNAMIC_METHOD_NAME = 'viewSearchRelatedDocumentDialog'
        method_name_length = len(DYNAMIC_METHOD_NAME)

        zope_security = '__roles__'
        if (name[:method_name_length] == DYNAMIC_METHOD_NAME) and \
           (name[-len(zope_security):] != zope_security):
          method_count_string_list = name[method_name_length:].split('_')
          method_count_string = method_count_string_list[0]
          # be sure that method name is correct
          try:
            method_count = string.atoi(method_count_string)
          except TypeError:
            return aq_base_name
          else:
            if len(method_count_string_list) > 1:
              # be sure that method name is correct
              try:
                sub_index = string.atoi(method_count_string_list[1])
              except TypeError:
                return aq_base_name
            else:
              sub_index = None

            # generate dynamicaly needed forwarder methods
            def viewSearchRelatedDocumentDialogWrapper(self, form_id,
                                                       REQUEST=None, **kw):
              """
                viewSearchRelatedDocumentDialog Wrapper
              """
#               LOG('SelectionTool.viewSearchRelatedDocumentDialogWrapper, kw',
#                   0, kw)
              return self.viewSearchRelatedDocumentDialog(
                                   method_count, form_id,
                                   REQUEST=REQUEST, sub_index=sub_index, **kw)
            setattr(self.__class__, name,
                    viewSearchRelatedDocumentDialogWrapper)

            klass = aq_base(self).__class__
            security_property_id = '%s__roles__' % (name, )
            # Declare method as public
            setattr(klass, security_property_id, None)

            return getattr(self, name)
        else:
          return aq_base_name
      return aq_base_name

    def _getUserId(self):
      return self.portal_membership.getAuthenticatedMember().getUserName()
      # XXX It would be good to add somthing here
      # So that 2 anonymous users do not share the same selection

    def _getSelectionFromContainer(self, selection_name):
      user_id = self._getUserId()
      if user_id is None: return None
      if self.isMemcachedUsed():
        return self._getMemcachedContainer().get('%s-%s' %
                                                 (user_id, selection_name))
      else:
        return self._getPersistentContainer(user_id).get(selection_name,
                                                         None)

    def _setSelectionToContainer(self, selection_name, selection):
      user_id = self._getUserId()
      if user_id is None: return
      if self.isMemcachedUsed():
        self._getMemcachedContainer().set('%s-%s' % (user_id, selection_name), aq_base(selection))
      else:
        self._getPersistentContainer(user_id)[selection_name] = aq_base(selection)

    def _getSelectionNameListFromContainer(self):
      if self.isMemcachedUsed():
        return []
      else:
        user_id = self._getUserId()
        if user_id is None: return []
        return self._getPersistentContainer(user_id).keys()

    def _getMemcachedContainer(self):
      value = getattr(self, '_v_selection_data', None)
      if value is None:
        value = self.getPortalObject().portal_memcached.getMemcachedDict(key_prefix='selection_tool')
        setattr(self, '_v_selection_data', value)
      return value

    def _getPersistentContainer(self, user_id):
      if getattr(self, 'selection_data', None) is None:
        self.selection_data = PersistentMapping()
      if not self.selection_data.has_key(user_id):
        self.selection_data[user_id] = SelectionPersistentMapping()
      return self.selection_data[user_id]

InitializeClass( SelectionTool )


class SelectionPersistentMapping(PersistentMapping):
  """A conflict-free PersistentMapping.

  Like selection objects, the purpose is to only prevent restarting
  transactions.
  """
  def _p_independent(self) :
    return 1

  def _p_resolveConflict(self, oldState, savedState, newState):
    # update keys that only savedState has
    oldState = newState
    # dict returned by PersistentMapping.__getstate__ contains the data
    # under '_container' key in zope 2.7 and 'data' in zope 2.8
    if 'data' in oldState:
      oldState['data'].update(savedState['data'])
    else:
      oldState['_container'].update(savedState['_container'])
    return oldState


class TreeListLine:
  def __init__(self,object,is_pure_summary,depth, is_open,select_domain_dict,exception_uid_list):
    self.object=object
    self.is_pure_summary=is_pure_summary
    self.depth=depth
    self.is_open=is_open
    self.select_domain_dict=select_domain_dict
    self.exception_uid_list=exception_uid_list

  def getObject(self):
    return self.object

  def getIsPureSummary(self):
    return self.is_pure_summary

  def getDepth(self):
    return self.depth

  def getIsOpen(self):
    return self.is_open

  def getSelectDomainDict(self):
    return self.select_domain_dict

  def getExceptionUidList(self):
    return self.exception_uid_list


def makeTreeList(here, form, root_dict, report_path, base_category,
		  depth, unfolded_list, form_id, selection_name,
		  report_depth, is_report_opened=1, list_method=None,
		  filtered_portal_types=[] ,sort_on = (('id', 'ASC'),)):
  """
    (object, is_pure_summary, depth, is_open, select_domain_dict)

    select_domain_dict is a dictionary of  associative list of (id, domain)
  """
  if isinstance(report_path, str):
    report_path = report_path.split('/')

  portal_categories = getattr(form, 'portal_categories', None)
  portal_domains = getattr(form, 'portal_domains', None)
  portal_object = form.portal_url.getPortalObject()
  if len(report_path):
    base_category = report_path[0]

  if root_dict is None:
    root_dict = {}

  is_empty_level = 1
  while is_empty_level:
    if not root_dict.has_key(base_category):
      root = None
      if portal_categories is not None:
        if portal_categories._getOb(base_category, None) is not None:
          if base_category == 'parent':
            # parent has a special treatment
            root = root_dict[base_category] = root_dict[None] = here
            report_path = report_path[1:]
          else:
            root = root_dict[base_category] = root_dict[None] = \
                                               portal_categories[base_category]
            report_path = report_path[1:]
      if root is None and portal_domains is not None:
        if portal_domains._getOb(base_category, None) is not None:
          root = root_dict[base_category] = root_dict[None] = \
                                               portal_domains[base_category]
          report_path = report_path[1:]
      if root is None:
        try:
          root = root_dict[None] = \
              portal_object.unrestrictedTraverse(report_path)
        except KeyError:
          LOG('SelectionTool', INFO, "Not found %s" % str(report_path))
          root = None
        report_path = ()
    else:
      root = root_dict[None] = root_dict[base_category]
      report_path = report_path[1:]
    is_empty_level = (root is not None) and \
        (root.objectCount() == 0) and (len(report_path) != 0)
    if is_empty_level: 
      base_category = report_path[0]

  tree_list = []
  if root is None: 
    return tree_list

  if base_category == 'parent':
    # Use searchFolder as default
    if list_method is None:
      if hasattr(aq_base(root), 'objectValues'):
        # If this is a folder, try to browse the hierarchy
        object_list = root.searchFolder(sort_on=sort_on)
    else: 
      if filtered_portal_types not in [[],None,'']:
        object_list = list_method(portal_type=filtered_portal_types,
                                  sort_on=sort_on)
      else:
        object_list = list_method(sort_on=sort_on)
    for zo in object_list:
      o = zo.getObject()
      if o is not None:
        new_root_dict = root_dict.copy()
        new_root_dict[None] = new_root_dict[base_category] = o

        selection_domain = DomainSelection(domain_dict = new_root_dict)
        if (report_depth is not None and depth <= (report_depth - 1)) or \
                                          o.getRelativeUrl() in unfolded_list:
          exception_uid_list = [] # Object we do not want to display

          for sub_zo in o.searchFolder(sort_on=sort_on):
            sub_o = sub_zo.getObject()
            if sub_o is not None and hasattr(aq_base(root), 'objectValues'):
              exception_uid_list.append(sub_o.getUid())
          # Summary (open)
          tree_list += [TreeListLine(o, 1, depth, 1, selection_domain, exception_uid_list)]
          if is_report_opened :
            # List (contents, closed, must be strict selection)
            tree_list += [TreeListLine(o, 0, depth, 0, selection_domain, exception_uid_list)]

          tree_list += makeTreeList(here, form, new_root_dict, report_path,
      		    base_category, depth + 1, unfolded_list, form_id, 
      		    selection_name, report_depth,
      		    is_report_opened=is_report_opened, sort_on=sort_on)
        else:
          tree_list += [TreeListLine(o, 1, depth, 0, selection_domain, ())] # Summary (closed)
  else:
    # process to recover objects in case a generation script is used
    if hasattr(root,'getChildDomainValueList'):
      oblist = root.getChildDomainValueList(root,depth=depth)
    else:
      oblist = root.objectValues()
    for o in oblist:
      new_root_dict = root_dict.copy()
      new_root_dict[None] = new_root_dict[base_category] = o
      selection_domain = DomainSelection(domain_dict = new_root_dict)
      if (report_depth is not None and depth <= (report_depth - 1)) or o.getRelativeUrl() in unfolded_list:
        tree_list += [TreeListLine(o, 1, depth, 1, selection_domain, None)] # Summary (open)
        if is_report_opened :
          tree_list += [TreeListLine(o, 0, depth, 0, selection_domain, None)] # List (contents, closed, must be strict selection)
        tree_list += makeTreeList(here, form, new_root_dict, report_path, base_category, depth + 1,
            unfolded_list, form_id, selection_name, report_depth,
            is_report_opened=is_report_opened, sort_on=sort_on)
      else:

        tree_list += [TreeListLine(o, 1, depth, 0, selection_domain, None)] # Summary (closed)

  return tree_list

# Automaticaly add wrappers on Folder so it can access portal_selections.
# Cannot be done in ERP5Type/Document/Folder.py because ERP5Type must not
# depend on ERP5Form.

from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Core.Folder import FolderMixIn
from ZPublisher.mapply import mapply

method_id_filter_list = [x for x in FolderMixIn.__dict__ if callable(getattr(FolderMixIn, x))]
candidate_method_id_list = [x for x in SelectionTool.__dict__ if callable(getattr(SelectionTool, x)) and not x.startswith('_') and not x.endswith('__roles__') and x not in method_id_filter_list]

# Monkey patch FolderMixIn with SelectionTool methods
#   kept here for compatibility with previous implementations
#   of Listbox HTML renderer. See bellow new implementation
for property_id in candidate_method_id_list:
  def portal_selection_wrapper(self, wrapper_property_id=property_id, *args, **kw):
    """
      Wrapper method for SelectionTool.
    """
    portal_selection = getToolByName(self, 'portal_selections')
    request = self.REQUEST
    method = getattr(portal_selection, wrapper_property_id)
    return mapply(method, positional=args, keyword=request,
                  context=self, bind=1)
  setattr(FolderMixIn, property_id, portal_selection_wrapper)
  security_property_id = '%s__roles__' % (property_id, )
  security_property = getattr(SelectionTool, security_property_id, None)
  if security_property is not None:
    setattr(FolderMixIn, security_property_id, security_property)

def createFolderMixInPageSelectionMethod(listbox_id):
  """
  This method must be called by listbox at rendering time.
  It dynamically creates methods on FolderMixIn in line
  with the naming of the listbox field. Generated method
  are able to convert request parameters in order to
  mimic the API of a listbox with ID "listbox". This
  approach was required for example to implement
  multiple multi-page listboxes in view mode. It also
  opens the way towards multiple editable listboxes in the same
  page although this is something which we can not recommend.
  """
  # Immediately return in the method already exists
  test_method_id = "%s_nextPage" % listbox_id
  if hasattr(FolderMixIn, test_method_id):
    return
  # Monkey patch FolderMixIn
  for property_id in candidate_method_id_list:
    def portal_selection_wrapper(self, wrapper_listbox_id=listbox_id,
                                       wrapper_property_id=property_id, *args, **kw):
      """
        Wrapper method for SelectionTool.
      """
      portal_selection = getToolByName(self, 'portal_selections')
      request = self.REQUEST
      selection_name_property_id = "%s_list_selection_name" % listbox_id
      listbox_uid_property_id = "%s_uid" % listbox_id
      list_start_property_id = "%s_list_start" % listbox_id
      # Rename request parameters
      if request.has_key(selection_name_property_id):
        request.form['list_selection_name'] = request[selection_name_property_id]
      if request.has_key(listbox_uid_property_id):
        request.form['listbox_uid'] = request[listbox_uid_property_id]
      if request.has_key(list_start_property_id):
        request.form['list_start'] = request[list_start_property_id]
      # Call the wrapper
      method = getattr(portal_selection, wrapper_property_id)
      return mapply(method, positional=args, keyword=request,
                    context=self, bind=1)
    new_property_id = "%s_%s" % (listbox_id, property_id)
    setattr(FolderMixIn, new_property_id, portal_selection_wrapper)
    security_property_id = '%s__roles__' % (property_id, )
    security_property = getattr(SelectionTool, security_property_id, None)
    if security_property is not None:
      new_security_property_id = '%s__roles__' % (new_property_id, )
      setattr(FolderMixIn, new_security_property_id, security_property)
