##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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

    security.declareProtected(ERP5Permissions.View, 'getSelectionCheckedUidsFor')
    def getSelectionCheckedUidsFor(self, selection_name, REQUEST=None):
      """
        Sets the selection params for a given selection_name
      """
      selection_object = self.getSelectionFor(selection_name, REQUEST)
      if selection_object:
        return selection_object.selection_checked_uids
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
    def getSelectionColumns(self, selection_name, columns=[], REQUEST=None):
      """
        Returns the columns in the selection
      """
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
    def nextPage(self, listbox_uid, uids=[], REQUEST=None):
      """
        Access the next page of a list
      """
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
    def previousPage(self, listbox_uid, uids=[], REQUEST=None):
      """
        Access the previous page of a list
      """
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
    def setPage(self, listbox_uid, uids=[], REQUEST=None):
      """
        Access the previous page of a list
      """
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



InitializeClass( SelectionTool )
