##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

"""\
ERP portal_categories tool.
"""

from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from Globals import InitializeClass, DTMLFile, PersistentMapping, get_request
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions as ERP5Permissions
from Products.ERP5Form import _dtmldir
from Selection import Selection
from email.MIMEBase import MIMEBase
from email import Encoders
from copy import copy
from DateTime import DateTime
import md5
import pickle
import hmac
import random

from zLOG import LOG

class SelectionError( Exception ):
    pass

class SelectionTool( UniqueObject, SimpleItem ):
    """
      The SelectionTool object is the place holder for all
      methods and algorithms related to persistent selections
      in ERP5.
    """

    id              = 'portal_selections'
    meta_type       = 'ERP5 Selections'

    security = ClassSecurityInfo()

    #
    #   ZMI methods
    #
    manage_options = ( ( { 'label'      : 'Overview'
                         , 'action'     : 'manage_overview'
                         }
                        ,
                        )
                     )

    security.declareProtected( ERP5Permissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainCategoryTool', _dtmldir )

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


      if not REQUEST:
        REQUEST = get_request()
      # New system: store directly - bypass session
      if 0:
        user_id = self.portal_membership.getAuthenticatedMember().getUserName()
        if user_id is not None:
          return self.selection_data.get((user_id, selection_name), None)
        else:
          return None

      # Another method: local dict
      if 0:
        if not hasattr(self, 'selection_data'):
          self.selection_data = PersistentMapping()
        user_id = self.portal_membership.getAuthenticatedMember().getUserName()
        if user_id is not None:
          return self.selection_data.get((user_id, selection_name), None)
        else:
          return None

      # Another method: local dict of dict
      if 1:
        if not hasattr(self, 'selection_data'):
          self.selection_data = PersistentMapping()
        user_id = self.portal_membership.getAuthenticatedMember().getUserName()
        if user_id is not None:
          if not self.selection_data.has_key(user_id):
            self.selection_data[user_id] = PersistentMapping()
          return self.selection_data[user_id].get(selection_name, None)
        else:
          return None

      # Previous method
      try:
        session = REQUEST.SESSION
        selection_name = selection_name + '_selection_object'
        if session.has_key(selection_name):
          return session[selection_name]
        else:
          return None
      except:
        # This prevents some transience errors to happen
        return None

    security.declareProtected(ERP5Permissions.View, 'setSelectionFor')
    def setSelectionFor(self, selection_name, selection_object, REQUEST=None):
      """
        Sets the selection instance for a given selection_name
      """
      if not REQUEST:
        REQUEST = get_request()
      # New system: store directly - bypass session
      if 0:
        user_id = self.portal_membership.getAuthenticatedMember().getUserName()
        if user_id is not None:
          self.selection_data.set((user_id, selection_name), selection_object)
        return

      # Another method: local dict
      if 0:
        if not hasattr(self, 'selection_data'):
          self.selection_data = PersistentMapping()
        user_id = self.portal_membership.getAuthenticatedMember().getUserName()
        if user_id is not None:
          self.selection_data[(user_id, selection_name)] = selection_object
        return

      # Another method: local dict but 2 stage to prevent user conflict
      if 1:
        if not hasattr(self, 'selection_data'):
          self.selection_data = PersistentMapping()
        user_id = self.portal_membership.getAuthenticatedMember().getUserName()
        if user_id is not None:
          if not self.selection_data.has_key(user_id):
            self.selection_data[user_id] = PersistentMapping()
          self.selection_data[user_id][selection_name] = selection_object
        return

      #try: CAUSES PROBLEMS WHY ??
      if 1:
        session = REQUEST.SESSION
        selection_name = selection_name + '_selection_object'
        session[selection_name] = selection_object
      #except:
      #  LOG('WARNING ERP5Form SelectionTool',0,'Could not set Selection')

    security.declareProtected(ERP5Permissions.View, 'setSelectionParamsFor')
    def setSelectionParamsFor(self, selection_name, params, REQUEST=None):
      """
        Sets the selection params for a given selection_name
      """
      selection_object = self.getSelectionFor(selection_name, REQUEST)
      if selection_object:
        selection_object.edit(params=params)
      else:
        selection_object = Selection(params=params)
      self.setSelectionFor(selection_name, selection_object, REQUEST)

    security.declareProtected(ERP5Permissions.View, 'setSelectionCheckedUidsFor')
    def setSelectionCheckedUidsFor(self, selection_name, checked_uids, REQUEST=None):
      """
        Sets the selection params for a given selection_name
      """
      selection_object = self.getSelectionFor(selection_name, REQUEST)
      if selection_object:
        selection_object.edit(checked_uids=checked_uids)
      else:
        selection_object = Selection(checked_uids=checked_uids)
      self.setSelectionFor(selection_name, selection_object, REQUEST)

    def updateSelectionCheckedUidList(self, selection_name, listbox_uid, uids, REQUEST=None):
      """
        Sets the selection params for a given selection_name
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
        Sets the selection params for a given selection_name
      """
      selection_object = self.getSelectionFor(selection_name, REQUEST)
      if selection_object:
        #return selection_object.selection_checked_uids
        return selection_object.getSelectionCheckedUids()
      return []

    security.declareProtected(ERP5Permissions.View, 'checkAll')
    def checkAll(self, selection_name, listbox_uid, REQUEST=None):
      """
        Sets the selection params for a given selection_name
      """
      selection_object = self.getSelectionFor(selection_name, REQUEST)
      if selection_object:
        selection_uid_dict = {}
        for uid in selection_object.selection_checked_uids:
          selection_uid_dict[uid] = 1
        for uid in listbox_uid:
          selection_uid_dict[int(uid)] = 1
        self.setSelectionCheckedUidsFor(selection_name, selection_uid_dict.keys(), REQUEST=REQUEST)
      request = REQUEST
      if request:
        referer = request['HTTP_REFERER']
        referer = referer.replace('reset=', 'noreset=')
        referer = referer.replace('reset:int=', 'noreset:int=')
        return request.RESPONSE.redirect(referer)

    security.declareProtected(ERP5Permissions.View, 'uncheckAll')
    def uncheckAll(self, selection_name, listbox_uid, REQUEST=None):
      """
        Sets the selection params for a given selection_name
      """
      selection_object = self.getSelectionFor(selection_name, REQUEST)
      if selection_object:
        selection_uid_dict = {}
        for uid in selection_object.selection_checked_uids:
          selection_uid_dict[uid] = 1
        for uid in listbox_uid:
          if selection_uid_dict.has_key(int(uid)): del selection_uid_dict[int(uid)]
        self.setSelectionCheckedUidsFor(selection_name, selection_uid_dict.keys(), REQUEST=REQUEST)
      request = REQUEST
      if request:
        referer = request['HTTP_REFERER']
        referer = referer.replace('reset=', 'noreset=')
        referer = referer.replace('reset:int=', 'noreset:int=')
        return request.RESPONSE.redirect(referer)

    security.declareProtected(ERP5Permissions.View, 'getSelectionListUrlFor')
    def getSelectionListUrlFor(self, selection_name, REQUEST=None):
      """
        Returns the URL of the list mode of selection instance
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection:
        return selection.getSelectionListUrl()
      else:
        return None

    security.declareProtected(ERP5Permissions.View, 'setSelectionToIds')
    def setSelectionToIds(self, selection_name, selection_uids, REQUEST=None):
      """
        Sets the selection to a small list of uids of documents
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        selection.edit(invert_mode=1, uids=selection_uids)

    security.declareProtected(ERP5Permissions.View, 'setSelectionToAll')
    def setSelectionToAll(self, selection_name, REQUEST=None):
      """
        Resets the selection
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        selection.edit(invert_mode=0, params={}, checked_uids=[])

    security.declareProtected(ERP5Permissions.View, 'setSelectionSortOrder')
    def setSelectionSortOrder(self, selection_name, sort_on, REQUEST=None):
      """
        Defines the sort order of the selection
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        selection.edit(sort_on=sort_on)

    security.declareProtected(ERP5Permissions.View, 'setSelectionQuickSortOrder')
    def setSelectionQuickSortOrder(self, selection_name, sort_on, REQUEST=None):
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

      request = REQUEST
      referer = request['HTTP_REFERER']
      referer = referer.replace('reset=', 'noreset=')
      referer = referer.replace('reset:int=', 'noreset:int=')
      return request.RESPONSE.redirect(referer)

    security.declareProtected(ERP5Permissions.View, 'getSelectionSortOrder')
    def getSelectionSortOrder(self, selection_name, REQUEST=None):
      """
        Returns the sort order of the selection
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is None: return ()
      return selection.selection_sort_on

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
        Returns the columns in the selection
      """
      if columns is None: columns = []
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        if len(selection.selection_columns) > 0:
          return selection.selection_columns
        else:
          return columns
      else:
        return columns


    security.declareProtected(ERP5Permissions.View, 'setSelectionStats')
    def setSelectionStats(self, selection_name, stats, REQUEST=None):
      """
        Defines the stats in the selection
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      selection.edit(stats=stats)

    security.declareProtected(ERP5Permissions.View, 'getSelectionStats')
    def getSelectionStats(self, selection_name, stats=[' ',' ',' ',' ',' ',' '], REQUEST=None):
      """
        Returns the stats in the selection
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        try:
          return selection.selection_stats
        except:
          return stats
      else:
        return stats


    security.declareProtected(ERP5Permissions.View, 'viewFirst')
    def viewFirst(self, selection_index='', selection_name='', form_id='view', REQUEST=None):
      """
        Access first item in a selection
      """
      if not REQUEST:
        REQUEST = get_request()
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection:
        method = self.unrestrictedTraverse(selection.selection_method_path)
        selection = selection(selection_method = method, context=self, REQUEST=REQUEST)
        o = selection[0]
        url = o.absolute_url()
      else:
        url = REQUEST.url
      url = '%s/%s?selection_index=%s&selection_name=%s' % (url, form_id, 0, selection_name)
      REQUEST.RESPONSE.redirect(url)

    security.declareProtected(ERP5Permissions.View, 'viewLast')
    def viewLast(self, selection_index='', selection_name='', form_id='view', REQUEST=None):
      """
        Access first item in a selection
      """
      if not REQUEST:
        REQUEST = get_request()
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection:
        method = self.unrestrictedTraverse(selection.selection_method_path)
        selection = selection(selection_method = method, context=self, REQUEST=REQUEST)
        o = selection[-1]
        url = o.absolute_url()
      else:
        url = REQUEST.url
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
        method = self.unrestrictedTraverse(selection.selection_method_path)
        selection = selection(selection_method = method, context=self, REQUEST=REQUEST)
        o = selection[(int(selection_index) + 1) % len(selection)]
        url = o.absolute_url()
      else:
        url = REQUEST.url
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
        method = self.unrestrictedTraverse(selection.selection_method_path)
        selection = selection(selection_method = method, context=self, REQUEST=REQUEST)
        o = selection[(int(selection_index) - 1) % len(selection)]
        url = o.absolute_url()
      else:
        url = REQUEST.url
      url = '%s/%s?selection_index=%s&selection_name=%s' % (url, form_id, int(selection_index) - 1, selection_name)
      REQUEST.RESPONSE.redirect(url)


    # ListBox related methods
    security.declareProtected(ERP5Permissions.View, 'nextPage')
    def nextPage(self, listbox_uid, uids=None, REQUEST=None):
      """
        Access the next page of a list
      """
      if uids is None: uids = []
      request = REQUEST
      form_id = request.form_id
      selection_name = request.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)
      params = selection.getSelectionParams()
      lines = params.get('list_lines',0)
      start = params.get('list_start', 0)
      params['list_start'] = int(start) + int(lines)
      selection.edit(params= params)

      self.uncheckAll(selection_name, listbox_uid)
      return self.checkAll(selection_name, uids, REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'previousPage')
    def previousPage(self, listbox_uid, uids=None, REQUEST=None):
      """
        Access the previous page of a list
      """
      if uids is None: uids = []
      request = REQUEST
      form_id = request.form_id
      selection_name = request.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)
      params = selection.getSelectionParams()
      lines = params.get('list_lines',0)
      start = params.get('list_start', 0)
      params['list_start'] = max(int(start) - int(lines), 0)
      selection.edit(params= selection.selection_params)

      self.uncheckAll(selection_name, listbox_uid)
      return self.checkAll(selection_name, uids, REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'setPage')
    def setPage(self, listbox_uid, uids=None, REQUEST=None):
      """
        Access the previous page of a list
      """
      if uids is None: uids = []
      request = REQUEST
      form_id = request.form_id
      selection_name = request.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        params = selection.getSelectionParams()
        lines = params.get('list_lines',0)
        start = request.form.get('list_start',0)

        params['list_start'] = start
        selection.edit(params= selection.selection_params)

      self.uncheckAll(selection_name, listbox_uid)
      return self.checkAll(selection_name, uids, REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'setDomainRoot')
    def setDomainRoot(self, REQUEST):
      """
        Sets the root domain for the current selection
      """
      request = REQUEST
      form_id = request.form_id
      selection_name = request.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)
      root_url = request.form.get('domain_root_url','portal_categories')
      selection.edit(domain_path=root_url, domain_list=((),))

      return request.RESPONSE.redirect(request['HTTP_REFERER'])

    security.declareProtected(ERP5Permissions.View, 'setDomainList')
    def setDomainList(self, REQUEST):
      """
        Sets the root domain for the current selection
      """
      request = REQUEST
      form_id = request.form_id
      selection_name = request.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)
      domain_list_url = request.form.get('domain_list_url','portal_categories')
      if type(domain_list_url) == type('a'):
        domain = self.unrestrictedTraverse(domain_list_url)
        domain_root = self.unrestrictedTraverse(selection.getSelectionDomainPath())
        selection.edit(domain_list=(domain.getPhysicalPath()[len(domain_root.getPhysicalPath()):],))

      return request.RESPONSE.redirect(request['HTTP_REFERER'])

    security.declareProtected(ERP5Permissions.View, 'setReportRoot')
    def setReportRoot(self, REQUEST):
      """
        Sets the root domain for the current selection
      """
      request = REQUEST
      form_id = request.form_id
      selection_name = request.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)
      root_url = request.form.get('report_root_url','portal_categories')
      selection.edit(report_path=root_url, report_list=((),))

      return request.RESPONSE.redirect(request['HTTP_REFERER'])


    security.declareProtected(ERP5Permissions.View, 'unfoldReport')
    def unfoldReport(self, REQUEST):
      """
        Sets the root domain for the current selection
      """
      request = REQUEST
      form_id = request.form_id
      selection_name = request.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)
      report_url = request.form.get('report_url','portal_categories')
      if type(report_url) == type('a'):
        report = self.unrestrictedTraverse(report_url)
        report_root = self.unrestrictedTraverse(selection.getSelectionReportPath())
        selection.edit(report_list=list(selection.getSelectionReportList())
           + [report.getPhysicalPath()[len(report_root.getPhysicalPath()):],] )

      return request.RESPONSE.redirect(request['HTTP_REFERER'])

    security.declareProtected(ERP5Permissions.View, 'foldReport')
    def foldReport(self, REQUEST):
      """
        Sets the root domain for the current selection
      """
      request = REQUEST
      form_id = request.form_id
      selection_name = request.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)
      report_url = request.form.get('report_url','portal_categories')
      if type(report_url) == type('a'):
        report = self.unrestrictedTraverse(report_url)
        report_root = self.unrestrictedTraverse(selection.getSelectionReportPath())
        report_path = report.getPhysicalPath()[len(report_root.getPhysicalPath()):]
        report_list = selection.getSelectionReportList()
        new_report_list = []
        report_path_len = len(report_path)
        for p in report_path:
          if p[0:report_path_len] != report_path:
            new_report_list += [p]
        selection.edit(report_list=new_report_list)

      return request.RESPONSE.redirect(request['HTTP_REFERER'])


    security.declareProtected(ERP5Permissions.View, 'setListboxDisplayMode')
    def setListboxDisplayMode(self, REQUEST,listbox_display_mode):
      """
        Toogle display of the listbox
      """

      request = REQUEST
      selection_name = request.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)

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


      selection.edit(flat_list_mode=flat_list_mode,domain_tree_mode=domain_tree_mode,
                                                report_tree_mode=report_tree_mode)

      referer = request['HTTP_REFERER']
      referer = referer.replace('reset=', 'noreset=')
      referer = referer.replace('reset:int=', 'noreset:int=')
      return request.RESPONSE.redirect(referer)


    security.declareProtected(ERP5Permissions.View, 'setFlatListMode')
    def setFlatListMode(self, REQUEST):
      """
        Set display of the listbox to FlatList mode
      """

      return self.setListboxDisplayMode(REQUEST=REQUEST,listbox_display_mode='FlatListMode')


    security.declareProtected(ERP5Permissions.View, 'setDomainTreeMode')
    def setDomainTreeMode(self, REQUEST):
      """
         Set display of the listbox to DomainTree mode
      """

      return self.setListboxDisplayMode(REQUEST=REQUEST,listbox_display_mode='DomainTreeMode')


    security.declareProtected(ERP5Permissions.View, 'setReportTreeMode')
    def setReportTreeMode(self, REQUEST):
      """
        Set display of the listbox to ReportTree mode
      """

      return self.setListboxDisplayMode(REQUEST=REQUEST,listbox_display_mode='ReportTreeMode')

    security.declareProtected(ERP5Permissions.View, 'getSelectionSelectedValueList')
    def getSelectionSelectedValueList(self, selection_name, REQUEST=None, selection_method=None, context=None):
      """
        Get the list of values selected for 'selection_name'
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is None:
        return []
      return selection(selection_method=selection_method, context=context, REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'getSelectionCheckedValueList')
    def getSelectionCheckedValueList(self, selection_name, REQUEST=None):
      """
        Get the list of values checked for 'selection_name'
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is None:
        return []
      uid_list = selection.getSelectionCheckedUids()
      value_list = self.portal_catalog.getObjectList(uid_list)
      return value_list

    security.declareProtected(ERP5Permissions.View, 'getSelectionValueList')
    def getSelectionValueList(self, selection_name, REQUEST=None, selection_method=None, context=None):
      """
        Get the list of values checked or selected for 'selection_name'
      """
      value_list = self.getSelectionCheckedValueList(selection_name, REQUEST=REQUEST)
      if len(value_list) == 0:
        value_list = self.getSelectionSelectedValueList(selection_name, REQUEST=REQUEST, selection_method=selection_method, context=context)
      return value_list

    security.declareProtected(ERP5Permissions.View, 'getSelectionUidList')
    def getSelectionUidList(self, selection_name, REQUEST=None, selection_method=None, context=None):
      """
        Get the list of values checked or selected for 'selection_name'
      """
      return map(lambda x:x.getObject().getUid(), self.getSelectionValueList(selection_name, REQUEST=REQUEST, selection_method=selection_method, context=context))

    security.declareProtected(ERP5Permissions.View, 'selectionHasChanged')
    def selectionHasChanged(self, md5_string, object_uid_list):
      """
        We want to be sure that the selection did not change
      """
      LOG('selectionHasChanged, md5_string',0,md5_string)
      LOG('selectionHasChanged, object_uid_list',0,object_uid_list)
      sorted_object_uid_list = copy(object_uid_list)
      sorted_object_uid_list.sort()
      new_md5_string = md5.new(str(sorted_object_uid_list)).hexdigest()
      LOG('selectionHasChanged, new_md5_string',0,new_md5_string)
      if md5_string != new_md5_string:
        LOG('selectionHasChanged, return...',0,'True')
        return True
      LOG('selectionHasChanged, return...',0,'False')
      return False

    security.declareProtected(ERP5Permissions.View, 'getPickle')
    def getPickle(self,**kw):
      """
      we give many keywords and we will get the corresponding
      pickle string and signature
      """
      LOG('getPickle kw',0,kw)
      # XXX Remove DateTime, This is really bad, only use for zope 2.6
      # XXX This has to be removed as quickly as possible
      for k,v in kw.items():
        if isinstance(v,DateTime):
          del kw[k]
      # XXX End of the part to remove
      pickle_string = pickle.dumps(kw)
      msg = MIMEBase('application','octet-stream')
      msg.set_payload(pickle_string)
      Encoders.encode_base64(msg)
      pickle_string = msg.get_payload()
      pickle_string = pickle_string.replace('\n','@@@')
      LOG('getPickleAndSignature pickle',0,pickle_string)
      return pickle_string

    security.declareProtected(ERP5Permissions.View, 'getPickleAndSignature')
    def getPickleAndSignature(self,**kw):
      """
      we give many keywords and we will get the corresponding
      pickle string and signature
      """
      pickle_string = self.getPickle(**kw)
      LOG('getPickleAndSignature pickle',0,pickle_string)
      signature = hmac.new(cookie_password,pickle_string).hexdigest()
      LOG('getPickleAndSignature signature',0,signature)
      return (pickle_string,signature)

    security.declareProtected(ERP5Permissions.View, 'getObjectFromPickle')
    def getObjectFromPickle(self,pickle_string):
      """
      we give a pickle string and a signature
      """
      object = None
      pickle_string = pickle_string.replace('@@@','\n')
      LOG('getObjectFromPickleAndSignature pickle_string',0,pickle_string)
      msg = MIMEBase('application','octet-stream')
      Encoders.encode_base64(msg)
      msg.set_payload(pickle_string)
      pickle_string = msg.get_payload(decode=1)
      object = pickle.loads(pickle_string)
      return object

    security.declareProtected(ERP5Permissions.View, 'getObjectFromPickleAndSignature')
    def getObjectFromPickleAndSignature(self,pickle_string,signature):
      """
      we give a pickle string and a signature
      """
      cookie_password = self._getCookiePassword()
      object = None
      new_signature = hmac.new(cookie_password,pickle_string).hexdigest()
      LOG('getObjectFromPickleAndSignature pickle_string',0,pickle_string)
      LOG('getObjectFromPickleAndSignature signature',0,signature)
      LOG('getObjectFromPickleAndSignature signature',0,new_signature)
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

    security.declareProtected(ERP5Permissions.View, 'registerCookieInfo')
    def setCookieInfo(self,request,cookie_name,**kw):
      """
      regiter info directly in cookie
      """
      cookie_name = cookie_name + '_cookie'
      (pickle_string,signature) = self.getPickleAndSignature(**kw)
      request.RESPONSE.setCookie(cookie_name,pickle_string,max_age=15*60)
      signature_cookie_name = cookie_name + '_signature'
      request.RESPONSE.setCookie(signature_cookie_name,signature,max_age=15*60)

    security.declareProtected(ERP5Permissions.View, 'registerCookieInfo')
    def getCookieInfo(self,request,cookie_name):
      """
      regiter info directly in cookie
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






InitializeClass( SelectionTool )
