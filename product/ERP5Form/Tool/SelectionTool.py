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
from Products.ERP5Type.Globals import InitializeClass, DTMLFile, PersistentMapping, get_request
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions as ERP5Permissions
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Form import _dtmldir
from Products.ERP5Form.Selection import Selection, DomainSelection
from ZPublisher.HTTPRequest import FileUpload
from hashlib import md5
import string, re
from urlparse import urlsplit, urlunsplit
from zLOG import LOG, INFO, WARNING
from Acquisition import aq_base
from Products.ERP5Type.Message import translateString
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
import warnings

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
    if request.has_key(selection_name_property_id):
      request.form['list_selection_name'] = request[selection_name_property_id]
    if request.has_key(listbox_uid_property_id):
      request.form['listbox_uid'] = request[listbox_uid_property_id]
    if request.has_key(list_start_property_id):
      request.form['list_start'] = request[list_start_property_id]
    if request.has_key(page_start_property_id):
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
      if request.has_key(selection_name_property_id):
        request.form['list_selection_name'] = request[selection_name_property_id]
      if request.has_key(listbox_uid_property_id):
        request.form['listbox_uid'] = request[listbox_uid_property_id]
      if request.has_key(list_start_property_id):
        request.form['list_start'] = request[list_start_property_id]
      if request.has_key(page_start_property_id):
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
