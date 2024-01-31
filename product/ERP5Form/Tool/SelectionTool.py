# -*- coding: utf-8 -*-
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

from OFS.SimpleItem import SimpleItem
from Products.ERP5Type.Utils import ensure_list
from Products.ERP5Type.Globals import InitializeClass, DTMLFile, PersistentMapping, get_request
from AccessControl import ClassSecurityInfo
from ZTUtils import make_query
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions as ERP5Permissions
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.Utils import str2bytes
from Products.ERP5Form import _dtmldir
from Products.ERP5Form.Selection import Selection, DomainSelection
from ZPublisher.HTTPRequest import FileUpload
from hashlib import md5
import string, re
from six.moves.urllib.parse import urlsplit, urlunsplit
from zLOG import LOG, INFO, WARNING
from Acquisition import aq_base
from Products.ERP5Type.Message import translateString
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
import warnings
import six

_MARKER = []

class SelectionError( Exception ):
    pass

class SelectionTool( BaseTool, SimpleItem ):
    """
      The SelectionTool object is the place holder for all
      methods and algorithms related to persistent selections
      in ERP5.
    """

    id              = 'portal_selections'
    meta_type       = 'ERP5 Selections'
    portal_type     = 'Selection Tool'
    title           = 'Selections'
    security = ClassSecurityInfo()

    #
    #   ZMI methods
    #
    manage_options = ( ( { 'label'      : 'Overview'
                         , 'action'     : 'manage_overview'
                         },
                         { 'label'      : 'View Selections'
                         , 'action'     : 'manage_viewSelections'
                         },
                         { 'label'      : 'Configure'
                         , 'action'     : 'manage_configure'
                         } ))

    security.declareProtected( ERP5Permissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainSelectionTool', _dtmldir )

    security.declareProtected( ERP5Permissions.ManagePortal
                             , 'manage_viewSelections' )
    manage_viewSelections = DTMLFile( 'SelectionTool_manageViewSelections', _dtmldir )

    security.declareProtected( ERP5Permissions.ManagePortal
                             , 'manage_configure' )
    manage_configure = DTMLFile( 'SelectionTool_configure', _dtmldir )

    security.declareProtected( ERP5Permissions.ManagePortal
                             , 'manage_deleteSelectionForUser' )
    def manage_deleteSelectionForUser(self, selection_name, user_id, REQUEST=None):
      """
        Delete a specified selection
      """
      self._deleteSelectionForUserFromContainer(selection_name, user_id)
      if REQUEST is not None:
        return REQUEST.RESPONSE.redirect('%s/%s' %
                (self.absolute_url(), 'manage_viewSelections'))

    security.declareProtected( ERP5Permissions.ManagePortal
                             , 'manage_deleteSelection' )
    def manage_deleteSelection(self, selection_name, REQUEST=None):
      """
        Relete a specified selection
      """
      self._deleteSelectionFromContainer(selection_name)
      if REQUEST is not None:
        return REQUEST.RESPONSE.redirect('%s/%s' %
                (self.absolute_url(), 'manage_viewSelections'))

    security.declareProtected( ERP5Permissions.ManagePortal
                             , 'manage_deleteGlobalSelection' )
    def manage_deleteGlobalSelection(self, selection_name, REQUEST=None):
      """
        Relete a specified selection
      """
      self._deleteGlobalSelectionFromContainer(selection_name)
      if REQUEST is not None:
        return REQUEST.RESPONSE.redirect('%s/%s' %
                (self.absolute_url(), 'manage_viewSelections'))

    # storages of SelectionTool
    security.declareProtected(ERP5Permissions.ManagePortal
                              , 'getStorageItemList')
    def getStorageItemList(self):
      """Return the list of available storages
      """
      #storage_item_list = [('Persistent Mapping', 'selection_data',)]
      #list of tuple may fail dtml code: zope/documenttemplate/dt_in.py +578
      storage_item_list = [['Persistent Mapping', 'selection_data']]
      memcached_plugin_list = self.portal_memcached.contentValues(portal_type='Memcached Plugin', sort_on='int_index')
      storage_item_list.extend([['/'.join((mp.getParentValue().getTitle(), mp.getTitle(),)), mp.getRelativeUrl()] for mp in memcached_plugin_list])
      return storage_item_list

    security.declareProtected(ERP5Permissions.ModifyPortalContent, 'clearCachedContainer')
    def clearCachedContainer(self, is_anonymous=False):
      """
      Clear Container currently being used for Selection Tool because either the
      storage has changed or the its settings
      """
      if is_anonymous:
        container_id = '_v_anonymous_selection_container'
      else:
        container_id = '_v_selection_container'

      if getattr(aq_base(self), container_id, None):
        delattr(self, container_id)

    security.declareProtected( ERP5Permissions.ManagePortal, 'setStorage')
    def setStorage(self, storage, anonymous_storage=None, RESPONSE=None):
      """
        Set the storage of Selection Tool.
      """
      if storage in [item[1] for item in self.getStorageItemList()]:
        self.storage = storage
        self.clearCachedContainer()
      else:
        raise ValueError('Given storage type (%s) is now supported.' % (storage,))
      anonymous_storage = anonymous_storage or None
      if anonymous_storage in [item[1] for item in self.getStorageItemList()] + [None]:
        self.anonymous_storage = anonymous_storage
        self.clearCachedContainer(is_anonymous=True)
      else:
        raise ValueError('Given storage type (%s) is now supported.' % (anonymous_storage,))
      if RESPONSE is not None:
        RESPONSE.redirect('%s/manage_configure' % (self.absolute_url()))

    security.declareProtected( ERP5Permissions.ManagePortal, 'getStorage')
    def getStorage(self, default='selection_data'):
      """return the selected storage
      """
      storage = getattr(aq_base(self), 'storage', default)
      if storage is not default:
        #Backward compatibility
        if storage == 'Persistent Mapping':
          storage = 'selection_data'
        elif storage == 'Memcached Tool':
          memcached_plugin_list = self.portal_memcached.contentValues(portal_type='Memcached Plugin', sort_on='int_index')
          if len(memcached_plugin_list):
            storage = memcached_plugin_list[0].getRelativeUrl()
          else:
            storage = 'selection_data'
      return storage

    security.declareProtected( ERP5Permissions.ManagePortal, 'getAnonymousStorage')
    def getAnonymousStorage(self, default=None):
      """return the selected storage
      """
      return getattr(aq_base(self), 'anonymous_storage', default)

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

      form = REQUEST.form
      if no_reset and 'reset' in form:
        form['noreset'] = form['reset'] # Kept for compatibility - might no be used anymore
        del form['reset']
      if no_report_depth and 'report_depth' in form:
        form['noreport_depth'] = form['report_depth'] # Kept for compatibility - might no be used anymore
        del form['report_depth']

      if query_string is not None:
        warnings.warn('DEPRECATED: _redirectToOriginalForm got called with a query_string. The variables must be passed in REQUEST.form.',
                      DeprecationWarning)
      context = REQUEST['PARENTS'][0]
      form_id = dialog_id or REQUEST.get('dialog_id', None) or form_id or REQUEST.get('form_id', None)
      if form_id is None:
        return context()
      return getattr(context, form_id)()

    security.declareProtected(ERP5Permissions.View, 'getSelectionNameList')
    def getSelectionNameList(self, context=None, REQUEST=None):
      """
        Returns the selection names of the current user.
      """
      return sorted(self._getSelectionNameListFromContainer())

    # backward compatibility
    security.declareProtected(ERP5Permissions.View, 'getSelectionNames')
    def getSelectionNames(self, context=None, REQUEST=None):
      warnings.warn("getSelectionNames() is deprecated.\n"
                    "Please use getSelectionNameList() instead.",
                    DeprecationWarning)
      return self.getSelectionNameList(context, REQUEST)

    security.declareProtected(ERP5Permissions.View, 'callSelectionFor')
    def callSelectionFor(self, selection_name, method=None, context=None,
                                               REQUEST=None, params=None):
      """
      Calls the selection and return the list of selected documents
      or objects. Seledction method, context and parameters may be
      overriden in a non persistent way.

      selection_name -- the name of the selectoin (string)

      method -- optional method (callable) or method path (string)
                to use instead of the persistent selection method

      context -- optional context to call the selection method on

      REQUEST -- optional REQUEST parameters (not used, only to
                 provide API compatibility)

      params -- optional parameters which can be used to override
                default params

      TODO: is it acceptable to keep method in the API at this level
            for security reasons (XXX-JPS)
      """
      if context is None: context = self
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is None:
        return None
      return selection(method=method, context=context, REQUEST=REQUEST, params=params)

    def _getRequest(self, REQUEST=None):
      if REQUEST is None:
        REQUEST = getattr(self, 'REQUEST', None)
      return REQUEST

    def _getSelectionKeyFromRequest(self, selection_name, REQUEST):
      REQUEST = self._getRequest(REQUEST=REQUEST)
      if REQUEST is not None:
        return REQUEST.get('%s_selection_key' % selection_name, None) or \
          REQUEST.get('selection_key', None)

    security.declareProtected(ERP5Permissions.View, 'getSelectionFor')
    def getSelectionFor(self, selection_name, REQUEST=None):
      """
        Returns the selection instance for a given selection_name
      """
      if isinstance(selection_name, (tuple, list)):
        selection_name = selection_name[0]
      if not selection_name:
        return None
      selection = self._getSelectionFromContainer(selection_name)
      if selection is None and self.isAnonymous():
        selection_key = self._getSelectionKeyFromRequest(selection_name, REQUEST)
        if selection_key is not None:
          selection = self.getAnonymousSelection(selection_key, selection_name)
          self._setSelectionToContainer(selection_name, selection)
      if selection is not None:
        return selection.__of__(self)

    def __getitem__(self, key):
        return self.getSelectionParamsFor(key)

    security.declareProtected(ERP5Permissions.View, 'setSelectionFor')
    def setSelectionFor(self, selection_name, selection_object, REQUEST=None):
      """
        Sets the selection instance for a given selection_name
      """
      if not selection_name:
        return
      if not (selection_object is None or
              selection_name == selection_object.name):
        LOG('SelectionTool', WARNING,
            "Selection not set: new Selection name ('%s') differs from existing one ('%s')" % \
            (selection_name,
             selection_object.name))
      elif self.getSelectionFor(selection_name, REQUEST=REQUEST) != selection_object:
        self._setSelectionToContainer(selection_name, selection_object)
      if selection_object is None and self.isAnonymous():
        REQUEST = self._getRequest(REQUEST=REQUEST)
        for key in ('%s_selection_key' % selection_name, 'selection_key'):
          try:
            del REQUEST.form[key]
          except KeyError:
            pass

    security.declareProtected(ERP5Permissions.View, 'getSelectionParamsFor')
    def getSelectionParamsFor(self, selection_name, params=None, REQUEST=None):
      """
        Returns the params in the selection
      """
      if params is None:
        params = {}
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        if selection.params:
          return selection.getParams()
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
        selection_object = Selection(selection_name, params=params)
      self.setSelectionFor(selection_name, selection_object, REQUEST)

    security.declareProtected(ERP5Permissions.View, 'getSelectionDomainDictFor')
    def getSelectionDomainDictFor(self, selection_name, REQUEST=None):
      """
        Returns the Domain dict for a given selection_name
      """
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        try:
          return selection.getDomain().asDomainDict()
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
          return selection.getReport().asDomainDict()
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
        selection_object = Selection(selection_name, checked_uids=checked_uids)
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
        return selection_object.getCheckedUids()
      return []

    security.declareProtected(ERP5Permissions.View, 'checkAll')
    def checkAll(self, list_selection_name, listbox_uid=[], REQUEST=None,
                 query_string=None, form_id=None):
      """
        Check uids in a given listbox_uid list for a given list_selection_name
      """
      selection_object = self.getSelectionFor(list_selection_name, REQUEST)
      if selection_object:
        selection_uid_dict = {}
        for uid in selection_object.checked_uids:
          selection_uid_dict[uid] = 1
        for uid in listbox_uid:
          try:
            selection_uid_dict[int(uid)] = 1
          except (ValueError, TypeError):
            selection_uid_dict[uid] = 1
        self.setSelectionCheckedUidsFor(list_selection_name, ensure_list(selection_uid_dict.keys()), REQUEST=REQUEST)
      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST, form_id=form_id,
                                            query_string=query_string, no_reset=True)

    security.declareProtected(ERP5Permissions.View, 'uncheckAll')
    def uncheckAll(self, list_selection_name, listbox_uid=[], REQUEST=None,
                   query_string=None, form_id=None):
      """
        Uncheck uids in a given listbox_uid list for a given list_selection_name
      """
      selection_object = self.getSelectionFor(list_selection_name, REQUEST)
      if selection_object:
        selection_uid_dict = {}
        for uid in selection_object.checked_uids:
          selection_uid_dict[uid] = 1
        for uid in listbox_uid:
          try:
            if int(uid) in selection_uid_dict: del selection_uid_dict[int(uid)]
          except (ValueError, TypeError):
            if uid in selection_uid_dict: del selection_uid_dict[uid]
        self.setSelectionCheckedUidsFor(list_selection_name, ensure_list(selection_uid_dict.keys()), REQUEST=REQUEST)
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
        url = selection.getListUrl()
        if self.isAnonymous() and '?' in url:
          url += '&selection_key=%s' % self._getSelectionKeyFromRequest(selection_name, REQUEST)
        return url
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
    def setSelectionQuickSortOrder(self, selection_name=None, sort_on=None, REQUEST=None,
                                   query_string=None, form_id=None):
      """
        Defines the sort order of the selection directly from the listbox
        In this method, sort_on is just a string that comes from url
      """
      # selection_name, sort_on and form_id params are kept only for bacward compatibilty
      # as some test call setSelectionQuickSortOrder in url with these params
      listbox_id = None
      if REQUEST is not None:
        form = REQUEST.form
      if sort_on is None:
        listbox_id, sort_on = form["setSelectionQuickSortOrder"].split(".", 1)

      # Sort order can be specified in sort_on.
      if sort_on.endswith(':asc'):
        order = 'ascending'
        sort_on = sort_on[:-4]
      elif sort_on.endswith(':desc'):
        order = 'descending'
        sort_on = sort_on[:-5]
      elif sort_on.endswith(':none'):
        order = 'none'
        sort_on = sort_on[:-5]
      else:
        order = None
      # ... as well as cast type
      i = sort_on.find(':')
      if i < 0:
        as_type = None
      else:
        as_type = sort_on[i+1:]
        if as_type != 'float':
          return
        sort_on = sort_on[:i]

      if REQUEST is not None:
        if listbox_id is not None:
            selection_name_key = "%s_list_selection_name" %listbox_id
            selection_name = form[selection_name_key]
        elif selection_name is None:
            selection_name = form['selection_name']

      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is not None:
        if order is not None:
          # Allow user to sort by multiple columns
          new_sort_on = [s for s in selection.sort_on if s[0] != sort_on]
          if order != 'none':
            new_sort_on.append((sort_on, order, as_type) if as_type else
                               (sort_on, order))
        else:
          # We must first switch from asc to desc and vice-versa if sort_order exists
          # in selection
          order = 'ascending'
          for current in selection.sort_on:
            if current[0] == sort_on:
              if current[1] == order:
                order = 'descending'
              break
          new_sort_on = ((sort_on, order, as_type) if as_type else
                         (sort_on, order),)
        selection.edit(sort_on=new_sort_on)

      if REQUEST is not None:
        if 'listbox_uid' in form and \
            'uids' in form:
          self.uncheckAll(selection_name, REQUEST.get('listbox_uid'))
          self.checkAll(selection_name, REQUEST.get('uids'))

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

    def _getExistingFormId(self, document, form_id):
      portal = document.getPortalObject()
      for url in [q['url'] for q in portal.portal_actions\
          .listFilteredActionsFor(document).get('object_view', [])]:
        # XXX-Luke: As this is not possible to do form_id -> action_id the
        # only way to know if form_id is implemented by action of document
        # is to use string matching.
        # This re will (form_id = Base_view):
        # qdsqdsq/Base_view --> match
        # qdsqdsq/Base_view?qsdsqd --> matches
        # qdsqdsq/Base_view/qsdsqd --> matches
        # qdsqdsq/Base_viewAaa --> doesn't match
        # qdsqdsq/Umpa_view --> doesn't match
        if re.search('/%s($|\W+)' % form_id, url):
          return form_id
      return 'view'

    security.declareProtected(ERP5Permissions.View, 'viewFirst')
    def viewFirst(self, selection_index='', selection_name='', form_id='view', REQUEST=None):
      """
        Access first item in a selection
      """
      return self._redirectToIndex(0, selection_name, form_id, REQUEST)

    security.declareProtected(ERP5Permissions.View, 'viewLast')
    def viewLast(self, selection_index='', selection_name='', form_id='view', REQUEST=None):
      """
        Access last item in a selection
      """
      return self._redirectToIndex(-1, selection_name, form_id, REQUEST)

    security.declareProtected(ERP5Permissions.View, 'viewNext')
    def viewNext(self, selection_index='', selection_name='', form_id='view', REQUEST=None):
      """
        Access next item in a selection
      """
      return self._redirectToIndex(int(selection_index) + 1, selection_name, form_id, REQUEST)

    security.declareProtected(ERP5Permissions.View, 'viewPrevious')
    def viewPrevious(self, selection_index='', selection_name='', form_id='view', REQUEST=None):
      """
        Access previous item in a selection
      """
      return self._redirectToIndex(int(selection_index) - 1, selection_name, form_id, REQUEST)

    def _redirectToIndex(self, selection_index, selection_name, form_id, REQUEST):
      if not REQUEST:
        REQUEST = get_request()
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection:
        method = self.unrestrictedTraverse(selection.method_path)
        selection_list = selection(method = method, context=self, REQUEST=REQUEST)
        if len(selection_list):
          if selection_index > 0:
            selection_index = selection_index % len(selection_list)
          o = selection_list[selection_index]
          url = o.absolute_url()
          form_id = self._getExistingFormId(o.getObject(), form_id)
        else:
          url = REQUEST.getURL()
      else:
        url = REQUEST.getURL()
      if form_id != 'view':
        url += '/%s' % form_id
      query_kw = {
        'selection_index': selection_index,
        'selection_name': selection_name,
      }
      if int(REQUEST.get('ignore_layout', 0)):
        query_kw['ignore_layout'] = 1
      if self.isAnonymous():
        query_kw['selection_key'] = self.getAnonymousSelectionKey(selection_name, REQUEST=REQUEST)
      REQUEST.RESPONSE.redirect('%s?%s' % (url, make_query(query_kw)))

    # ListBox related methods

    security.declareProtected(ERP5Permissions.View, 'firstPage')
    def firstPage(self, list_selection_name, listbox_uid, uids=None, REQUEST=None):
      """
        Access the first page of a list
      """
      if uids is None: uids = []
      selection = self.getSelectionFor(list_selection_name, REQUEST)
      if selection is not None:
        params = selection.getParams()
        params['list_start'] = 0
        selection.edit(params=params)
      self.uncheckAll(list_selection_name, listbox_uid)
      return self.checkAll(list_selection_name, uids, REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'lastPage')
    def lastPage(self, list_selection_name, listbox_uid, uids=None, REQUEST=None):
      """
        Access the last page of a list
      """
      if uids is None: uids = []
      selection = self.getSelectionFor(list_selection_name, REQUEST)
      if selection is not None:
        params = selection.getParams()
        # XXX This will not work if the number of lines shown in the listbox is greater
        #       than the BIG_INT constan. Such a case has low probability but is not
        #       impossible. If you are in this case, send me a mail ! -- Kev
        BIG_INT = 10000000
        last_page_start = BIG_INT
        total_lines = int(params.get('total_size', BIG_INT))
        if total_lines != BIG_INT:
          lines_per_page  = int(params.get('list_lines', 1))
          if total_lines % lines_per_page:
            # Example: if we have 105 documents and display 40 per line,
            # it is 105 // 40 * 40 = 80
            last_page_start = total_lines // lines_per_page * lines_per_page
          else:
            # Example; if we have 120 documents and display 40 per line,
            # it is 120 // (40 - 1) * 40 = 80
            last_page_start = (total_lines // lines_per_page - 1) * lines_per_page
        params['list_start'] = last_page_start
        selection.edit(params=params)
      self.uncheckAll(list_selection_name, listbox_uid)
      return self.checkAll(list_selection_name, uids, REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'nextPage')
    def nextPage(self, list_selection_name, listbox_uid, uids=None, REQUEST=None):
      """
        Access the next page of a list
      """
      if uids is None: uids = []
      selection = self.getSelectionFor(list_selection_name, REQUEST)
      if selection is not None:
        params = selection.getParams()
        lines = int(params.get('list_lines', 0))
        form = REQUEST.form
        if 'page_start' in form:
          try:
            list_start = (int(form.pop('page_start', 0)) - 1) * lines
          except (ValueError, TypeError):
            list_start = 0
        else:
          list_start = int(form.pop('list_start', 0))
        params['list_start'] = max(list_start + lines, 0)
        selection.edit(params=params)
      self.uncheckAll(list_selection_name, listbox_uid)
      return self.checkAll(list_selection_name, uids, REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'previousPage')
    def previousPage(self, list_selection_name, listbox_uid, uids=None, REQUEST=None):
      """
        Access the previous page of a list
      """
      if uids is None: uids = []
      selection = self.getSelectionFor(list_selection_name, REQUEST)
      if selection is not None:
        params = selection.getParams()
        lines = int(params.get('list_lines', 0))
        form = REQUEST.form
        if 'page_start' in form:
          try:
            list_start = (int(form.pop('page_start', 0)) - 1) * lines
          except (ValueError, TypeError):
            list_start = 0
        else:
          list_start = int(form.pop('list_start', 0))
        params['list_start'] = max(list_start - lines, 0)
        selection.edit(params=params)
      self.uncheckAll(list_selection_name, listbox_uid)
      return self.checkAll(list_selection_name, uids, REQUEST=REQUEST)

    security.declareProtected(ERP5Permissions.View, 'setPage')
    def setPage(self, list_selection_name, listbox_uid, query_string=None, uids=None, REQUEST=None):
      """
         Sets the current displayed page in a selection
      """
      if uids is None: uids = []
      selection = self.getSelectionFor(list_selection_name, REQUEST)
      if selection is not None:
        params = selection.getParams()
        lines = int(params.get('list_lines', 0))
        form = REQUEST.form
        if 'page_start' in form:
          try:
            list_start = (int(form.pop('page_start', 0)) - 1) * lines
          except (ValueError, TypeError):
            list_start = 0
        else:
          list_start = int(form.pop('list_start', 0))
        params['list_start'] = max(list_start, 0)
        selection.edit(params=params)
        self.uncheckAll(list_selection_name, listbox_uid)
      return self.checkAll(list_selection_name, uids, REQUEST=REQUEST, query_string=query_string)

    # PlanningBox related methods
    security.declareProtected(ERP5Permissions.View, 'setLanePath')
    def setLanePath(self, uids=None, REQUEST=None, form_id=None,
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
        lane_path = request.form.get('lane_path', None)
        if lane_path is None:
          # If lane_path is not defined try to
          # use the last one from params
          lane_path = params.get('lane_path',1)
        bound_start = request.form.get('bound_start', None)
        if bound_start is not None:
          params['bound_start'] = bound_start
        params['lane_path'] = lane_path
        params['zoom_variation'] = 0
        selection.edit(params=params)
      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST,
                                            form_id=form_id,
                                            query_string=query_string)

    security.declareProtected(ERP5Permissions.View, 'nextLanePage')
    def nextLanePage(self, uids=None, REQUEST=None, form_id=None, query_string=None):
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
        params['bound_variation'] = 1
        selection.edit(params=params)
      if REQUEST is not None:
        return self._redirectToOriginalForm(REQUEST=REQUEST,
                                            form_id=form_id,
                                             query_string=query_string)

    security.declareProtected(ERP5Permissions.View, 'previousLanePage')
    def previousLanePage(self, uids=None, REQUEST=None, form_id=None, query_string=None):
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
        params['bound_variation'] = -1
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

    security.declareProtected(ERP5Permissions.View, 'setDomainDictFromParam')
    def setDomainDictFromParam(self, selection_name, domain_dict):
      domain_list = []
      domain_path = []
      for key, value in domain_dict.items():
        domain_path.append(key)
        splitted_domain_list = value[1].split('/')[1:]
        for i in range(len(splitted_domain_list)):
          domain_list.append('%s/%s' % (key, '/'.join(splitted_domain_list[:i + 1])))

      if len(domain_path) == 1:
        domain_path = domain_path[0]

      selection = self.getSelectionFor(selection_name)
      selection.edit(
        domain_list=domain_list,
        domain_path=domain_path,
        domain=DomainSelection(domain_dict=domain_dict),
        flat_list_mode=0,
        domain_tree_mode=1,
        report_tree_mode=0,
      )

    security.declareProtected(ERP5Permissions.View, 'unfoldDomain')
    def unfoldDomain(self, REQUEST, form_id=None, query_string=None):
      """
        Unfold domain for the current selection
      """
      selection_name = REQUEST.list_selection_name
      selection = self.getSelectionFor(selection_name, REQUEST)

      unfoldDomain = REQUEST.form.get('unfoldDomain', None)
      domain_url, domain_depth = unfoldDomain.split('.', 2)
      domain_depth = int(domain_depth)

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

      foldDomain = REQUEST.form.get('foldDomain', None)
      domain_url, domain_depth = foldDomain.split('.', 2)
      domain_depth = int(domain_depth)

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
        selection = Selection(selection_name)
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
      selection.edit(params=params)

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
        Get the list of uids checked or selected for 'selection_name'
      """
      return [x.getObject().getUid() for x in self.getSelectionValueList(selection_name, REQUEST=REQUEST, selection_method=selection_method, context=context)]

    security.declareProtected(ERP5Permissions.View, 'selectionHasChanged')
    def selectionHasChanged(self, md5_string, object_uid_list):
      """
        We want to be sure that the selection did not change
      """
      return md5_string != self._getUIDListChecksum(object_uid_list)

    security.declareProtected(ERP5Permissions.View, 'getSelectionChecksum')
    def getSelectionChecksum(self, selection_name, uid_list=None):
      """Generate an MD5 checksum against checked uids. This is used to confirm
      that selected values do not change between a display of a dialog and an
      execution.
      uid_list (deprecated)
        For backward compatibility with code not updating selected uids.
      """
      if uid_list is None:
        uid_list = self.getSelectionCheckedUidsFor(selection_name)
      return self._getUIDListChecksum(uid_list)

    def _getUIDListChecksum(self, uid_list):
      if uid_list is None:
          return None
      # XXX To avoid the difference of the string representations of int and long,
      # convert each element to a string.
      return md5(str2bytes(repr(sorted(str(e) for e in uid_list)))).hexdigest()

    # Related document searching
    security.declarePublic('viewSearchRelatedDocumentDialog')
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
        raise SelectionError("SelectionTool: can not find the relation field %s"
                             % index)
      else:
        # Field found
        field_key = field.generate_field_key()
        field_value = REQUEST.form[field_key]
        dialog_id = field.get_value('relation_form_id') or \
                                                   'Base_viewRelatedObjectList'
        redirect_form = getattr(o, dialog_id)
        # XXX Hardcoded listbox field
        selection_name = redirect_form.listbox.get_value('selection_name')
        # Reset current selection
        self.setSelectionFor(selection_name, None)


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
          catalog_index = field.get_value('catalog_index')
          kw[catalog_index] = field_value
          self.setSelectionParamsFor(selection_name,
                                     kw.copy())
          self.setSelectionCheckedUidsFor(selection_name,
                                          current_uid_list)
          field_value = str(field_value)
          if len(field_value):
            sql_catalog = self.portal_catalog.getSQLCatalog()
            field_value = sql_catalog.buildQuery({
              catalog_index:{'query':field_value.splitlines(),
                             'key':'ExactMatch',},
            }).asSearchTextExpression(sql_catalog, column='')

          REQUEST.form[field_key] = field_value
          portal_status_message = translateString("Please select one (or more) object.")
        else:
          portal_status_message = translateString("Please select one object.")


        # Save the current REQUEST form
        # We can't put FileUpload instances because we can't pickle them
        saved_form_data = {key: value
          for key, value in REQUEST.form.items()
          if not isinstance(value, FileUpload)}

        kw = {
          'dialog_id': dialog_id,
          'selection_name': selection_name,
          'selection_index': 0, # We start on the first page
          'field_id': field.id,
          'reset': 0,
          'base_category': field.get_value( 'base_category'),
          'form_id': form_id,
          field.get_value('catalog_index'): field_value,
          'portal_status_message': portal_status_message,
          'saved_form_data': saved_form_data,
          'ignore_layout': int(REQUEST.get('ignore_layout', 0)),
          'ignore_hide_rows': 1,
        }
        kw.update(field.get_value('parameter_list'))
        # remove ignore_layout parameter from cancel_url otherwise we
        # will have two ignore_layout parameters after clicking cancel
        # button.
        split_referer = list(urlsplit(REQUEST.get('HTTP_REFERER')))
        split_referer[3] = '&'.join([x for x in \
                                     split_referer[3].split('&') \
                                     if not re.match('^ignore_layout[:=]', x)])
        kw['cancel_url'] = urlunsplit(split_referer)

        proxy_listbox_ids = field.get_value('proxy_listbox_ids')
        REQUEST.set('proxy_listbox_ids', proxy_listbox_ids)
        if len(proxy_listbox_ids) > 0:
          REQUEST.set('proxy_listbox_id', proxy_listbox_ids[0][0])
        else:
          REQUEST.set('proxy_listbox_id',
                       "Base_viewRelatedObjectListBase/listbox")

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

    security.declarePublic('asDomainQuery')
    def asDomainQuery(self, domain, strict_membership=False):
      if isinstance(domain, DomainSelection):
        warnings.warn("To pass a DomainSelection instance is deprecated.\n"
                      "Please use a domain dict instead.",
                      DeprecationWarning)
      else:
        domain = DomainSelection(domain).__of__(self)
      relation_dict = {}
      query_list = []
      append = query_list.append
      domain_item_dict = domain.asDomainItemDict()
      # XXX: why even put Nones in domain if they are ignored ?
      domain_item_dict.pop(None, None)
      for key, value in six.iteritems(domain_item_dict):
        if getattr(aq_base(value), 'isPredicate', 0):
          append(
            value.asQuery(strict_membership=strict_membership),
          )
        else:
          relation_dict[key] = [value]
      if relation_dict:
        append(
          self.getPortalObject().portal_catalog.getCategoryValueDictParameterDict(
            relation_dict,
            strict_membership=strict_membership,
          ),
        )
      if query_list:
        return ComplexQuery(query_list)
      return SimpleQuery(uid=0, comparison_operator='>')

    def _aq_dynamic(self, name):
      """
        Generate viewSearchRelatedDocumentDialog0,
                 viewSearchRelatedDocumentDialog1,... if necessary
      """
      aq_base_name = getattr(aq_base(self), name, None)
      if aq_base_name is None:
        DYNAMIC_METHOD_NAME = 'viewSearchRelatedDocumentDialog'
        method_name_length = len(DYNAMIC_METHOD_NAME)

        zope_security = '__roles__'
        if (name[:method_name_length] == DYNAMIC_METHOD_NAME) and \
           (name[-len(zope_security):] != zope_security):
          method_count_string_list = name[method_name_length:].split('_')
          method_count_string = method_count_string_list[0]
          # be sure that method name is correct
          try:
            method_count = int(method_count_string)
          except (TypeError, ValueError):
            return aq_base_name
          else:
            if len(method_count_string_list) > 1:
              # be sure that method name is correct
              try:
                sub_index = int(method_count_string_list[1])
              except (TypeError, ValueError):
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
      return SelectionTool.inheritedAttribute('_aq_dynamic')(self, name)

    def _getUserId(self):
      tv = getTransactionalVariable()
      user_id = tv.get('_user_id', None)
      if user_id is not None:
        return user_id
      user_id = self.portal_membership.getAuthenticatedMember().getIdOrUserName()
      tv['_user_id'] = user_id
      return user_id

    security.declarePrivate('getTemporarySelectionDict')
    def getTemporarySelectionDict(self):
      """ Temporary selections are used in push/pop nested scope,
      to prevent from editting for stored selection in the scope.
      Typically, it is used for ReportSection."""
      tv = getTransactionalVariable()
      return tv.setdefault('_temporary_selection_dict', {})

    def pushSelection(self, selection_name):
      selection = self.getSelectionFor(selection_name)
      # a temporary selection is kept in transaction.
      temp_selection = Selection(selection_name)
      if selection:
        temp_selection.__dict__.update(selection.__dict__)
      self.getTemporarySelectionDict()\
        .setdefault(selection_name, []).append(temp_selection)

    def popSelection(self, selection_name):
      temporary_selection_dict = self.getTemporarySelectionDict()
      if selection_name in temporary_selection_dict and \
         temporary_selection_dict[selection_name]:
        temporary_selection_dict[selection_name].pop()

    def getAnonymousSelection(self, key, selection_name):
      container_id = '_v_anonymous_selection_container'
      storage = self.getAnonymousStorage() or self.getStorage()
      container = self._getContainerFromStorage(container_id, storage)
      return container.getSelection(key, selection_name)

    def getAnonymousSelectionKey(self, selection_name, REQUEST=None):
      if not self.isAnonymous():
        return ''
      selection = self.getSelectionFor(selection_name, REQUEST=REQUEST)
      if selection is None:
        return ''
      key = selection.getAnonymousSelectionKey()
      container_id = '_v_anonymous_selection_container'
      storage = self.getAnonymousStorage() or self.getStorage()
      container = self._getContainerFromStorage(container_id, storage)
      container.setSelection(key, selection_name, selection)
      return key

    def _getSelectionFromContainer(self, selection_name):
      user_id = self._getUserId()
      if user_id is None: return None

      temporary_selection_dict = self.getTemporarySelectionDict()
      if temporary_selection_dict and selection_name in temporary_selection_dict:
        if temporary_selection_dict[selection_name]:
          # focus the temporary selection in the most narrow scope.
          return temporary_selection_dict[selection_name][-1]

      return self._getContainer().getSelection(user_id, selection_name)

    def _setSelectionToContainer(self, selection_name, selection):
      user_id = self._getUserId()
      if user_id is None: return

      temporary_selection_dict = self.getTemporarySelectionDict()
      if temporary_selection_dict and selection_name in temporary_selection_dict:
        if temporary_selection_dict[selection_name]:
          # focus the temporary selection in the most narrow scope.
          temporary_selection_dict[selection_name][-1] = selection
          return

      self._getContainer().setSelection(user_id, selection_name, selection)

    def _deleteSelectionForUserFromContainer(self, selection_name, user_id):
      if user_id is None: return None
      self._getContainer().deleteSelection(user_id, selection_name)

    def _deleteSelectionFromContainer(self, selection_name):
      user_id = self._getUserId()
      self._deleteSelectionForUserFromContainer(selection_name, user_id)

    def _deleteGlobalSelectionFromContainer(self, selection_name):
      self._getContainer().deleteGlobalSelection(self, selection_name)

    def _getSelectionNameListFromContainer(self):
      user_id = self._getUserId()
      return list(set(self._getContainer().getSelectionNameList(user_id) +
                      ensure_list(self.getTemporarySelectionDict().keys())))

    def isAnonymous(self):
      return self._getUserId() == 'Anonymous User'

    def _getContainer(self):
      if self.isAnonymous():
        tv = getTransactionalVariable()
        storage = tv.setdefault('_transactional_selection_container', {})
        container = TransactionalCacheContainer(storage)
        return container
      else:
        container_id = '_v_selection_container'
        storage = self.getStorage()
        return self._getContainerFromStorage(container_id, storage)

    def _getContainerFromStorage(self, container_id, storage):
      container = getattr(aq_base(self), container_id, None)
      if container is None:
        if storage.startswith('portal_memcached/'):
          plugin_path = storage
          value = self.getPortalObject().\
                  portal_memcached.getMemcachedDict(key_prefix='selection_tool',
                                                    plugin_path=plugin_path)
          container = MemcachedContainer(value)
        else:
          if getattr(aq_base(self), 'selection_data', None) is None:
            self.selection_data = PersistentMapping()
          value = self.selection_data
          container = PersistentMappingContainer(value)
        setattr(self, container_id, container)
      return container

InitializeClass( SelectionTool )

class BaseContainer(object):
  def __init__(self, container):
    self._container = container

class MemcachedContainer(BaseContainer):
  def getSelectionNameList(self, user_id):
    return []

  def getSelection(self, user_id, selection_name):
    try:
      return self._container.get('%s-%s' % (user_id, selection_name))
    except KeyError:
      return None

  def setSelection(self, user_id, selection_name, selection):
    self._container.set('%s-%s' % (user_id, selection_name), aq_base(selection))

  def deleteSelection(self, user_id, selection_name):
    del(self._container['%s-%s' % (user_id, selection_name)])

  def deleteGlobalSelection(self, user_id, selection_name):
    pass

class TransactionalCacheContainer(MemcachedContainer):
  def setSelection(self, user_id, selection_name, selection):
    self._container.__setitem__('%s-%s' % (user_id, selection_name), aq_base(selection))

class PersistentMappingContainer(BaseContainer):
  def getSelectionNameList(self, user_id):
    try:
      return ensure_list(self._container[user_id].keys())
    except KeyError:
      return []

  def getSelection(self, user_id, selection_name):
    try:
      return self._container[user_id][selection_name]
    except KeyError:
      return None

  def setSelection(self, user_id, selection_name, selection):
    try:
      user_container = self._container[user_id]
    except KeyError:
      user_container = SelectionPersistentMapping()
      self._container[user_id] = user_container
    user_container[selection_name] = aq_base(selection)

  def deleteSelection(self, user_id, selection_name):
    try:
      user_container = self._container[user_id]
      del(user_container[selection_name])
    except KeyError:
      pass

  def deleteGlobalSelection(self, user_id, selection_name):
    for user_container in six.itervalues(self._container):
      try:
        del(user_container[selection_name])
      except KeyError:
        pass

class SelectionPersistentMapping(PersistentMapping):
  """A conflict-free PersistentMapping.

  Like selection objects, the purpose is to only prevent restarting
  transactions.
  """
  def _p_independent(self) :
    return 1

  def _p_resolveConflict(self, oldState, savedState, newState):
    # BUG: we should not modify newState
    # update keys that only savedState has
    newState['data'].update(savedState['data'])
    return newState


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
  portal_object = form.getPortalObject()
  if len(report_path):
    base_category = report_path[0]

  if root_dict is None:
    root_dict = {}

  is_empty_level = 1
  while is_empty_level:
    if base_category not in root_dict:
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
candidate_method_id_list = []
for x in SelectionTool.__dict__:
  if not callable(getattr(SelectionTool, x)):
    continue
  if x.startswith('_') or x.endswith('__roles__'):
    continue
  if x in method_id_filter_list:
    continue
  roles = getattr(SelectionTool, '%s__roles__' % x, None)
  if roles is None or roles == ():
    continue
  if roles.__name__ == ERP5Permissions.ManagePortal:
    continue
  candidate_method_id_list.append(x)

# Monkey patch FolderMixIn with SelectionTool methods, and wrapper methods
# ('listbox_<WRAPPED_METHOD_NAME>()') used to set ListBox properties for
# pagination
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

  def portal_selection_wrapper(self, wrapper_property_id=property_id, *args, **kw):
    """
      Wrapper method for SelectionTool.
    """
    portal_selection = getToolByName(self, 'portal_selections')
    request = self.REQUEST
    listbox_id = request.form.get('listbox_%s' % wrapper_property_id, None)
    if not listbox_id:
      # Backward-compatibility: Should be removed as soon as
      # createFolderMixInPageSelectionMethod has been removed
      warnings.warn(
        "DEPRECATED: listbox_%s: 'value' attribute of the submit button "
        "should be set to the ListBox ID and the method name 'listbox_%s" %
        (wrapper_property_id, wrapper_property_id),
        DeprecationWarning)

      listbox_id = 'listbox'

    selection_name_property_id = "%s_list_selection_name" % listbox_id
    listbox_uid_property_id = "%s_uid" % listbox_id
    list_start_property_id = "%s_list_start" % listbox_id
    page_start_property_id = "%s_page_start" % listbox_id
    # Rename request parameters
    if selection_name_property_id in request:
      request.form['list_selection_name'] = request[selection_name_property_id]
    if listbox_uid_property_id in request:
      request.form['listbox_uid'] = request[listbox_uid_property_id]
    if list_start_property_id in request:
      request.form['list_start'] = request[list_start_property_id]
    if page_start_property_id in request:
      request.form['page_start'] = request[page_start_property_id]
    # Call the wrapper
    method = getattr(portal_selection, wrapper_property_id)
    return mapply(method, positional=args, keyword=request,
                  context=self, bind=1)
  new_property_id = "listbox_%s" % property_id
  setattr(FolderMixIn, new_property_id, portal_selection_wrapper)
  security_property_id = '%s__roles__' % (property_id, )
  security_property = getattr(SelectionTool, security_property_id, None)
  if security_property is not None:
    new_security_property_id = '%s__roles__' % (new_property_id, )
    setattr(FolderMixIn, new_security_property_id, security_property)

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

  Deprecated because these methods are generated when rendering the
  ListBox. Therefore, they are only available on the ZEO client
  where it has been rendered but not the other ZEO clients.
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
      warnings.warn(
        "DEPRECATED: %s_%s: The ListBox ID must not be contained anymore in the "
        "method name, but instead be in the 'value' attribute of the submit "
        "button and the method name should be 'listbox_%s'" %
        (wrapper_listbox_id, wrapper_property_id, wrapper_listbox_id),
        DeprecationWarning)

      portal_selection = getToolByName(self, 'portal_selections')
      request = self.REQUEST
      selection_name_property_id = "%s_list_selection_name" % listbox_id
      listbox_uid_property_id = "%s_uid" % listbox_id
      list_start_property_id = "%s_list_start" % listbox_id
      page_start_property_id = "%s_page_start" % listbox_id
      # Rename request parameters
      if selection_name_property_id in request:
        request.form['list_selection_name'] = request[selection_name_property_id]
      if listbox_uid_property_id in request:
        request.form['listbox_uid'] = request[listbox_uid_property_id]
      if list_start_property_id in request:
        request.form['list_start'] = request[list_start_property_id]
      if page_start_property_id in request:
        request.form['page_start'] = request[page_start_property_id]
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
