# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ayush Tiwari <ayush.tiwari@nexedi.com>
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

import deepdiff
from zLOG import LOG, WARNING
from deepdiff import DeepDiff
from unidiff import PatchSet
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import interfaces
from Products.PythonScripts.PythonScript import PythonScript

class DiffTool(BaseTool):
  """
  A portal tool that provides all kinds of utilities to
  compare objects.
  """
  id = 'portal_diff'
  title = 'Diff Tool'
  meta_type = 'ERP5 Diff Tool'
  portal_type = 'Diff Tool'
  allowed_types = ()

  # Declarative Security
  security = ClassSecurityInfo()

  def diffPortalObject(self, old, new, path=None, patch_format="deepdiff"):
    """
      Returns a PortalPatch instance with the appropriate format
      original -- original object
      new -- new object
      path -- optional path to specify which property to diff
      patch_format -- optional format (rfc6902 or deepdiff)
    """
    return PortalPatch(old, new, path, patch_format)

  def patchPortalObject(self, old, diff_list):
    """
    Receives the dict with old object, diff value and returns a new object from
    the diff and the old value
    """
    #LOG('DiffTool', 0, str(diff_list))

    copy_data = old.aq_parent.manage_copyObjects([old.id,])
    new_id = old.aq_parent.manage_pasteObjects(copy_data)[0]['new_id']
    new_obj = old.aq_parent[new_id]

    LOG('DiffTool', 0, str([l['path'] for l in diff_list]))
    for diff in diff_list:
      setattr(new_obj, diff['path'], diff['t2'])

    return new_obj

class PortalPatch:
  """
    Provides an abstraction to a patch that
    depends on the patch format.

    In the case of deepdiff, the abstraction can
    lead to a commutative merge system.

    In the case of rfc6902, the abstraction can not
    lead to a commutative merge system but may be
    useful to some UI applications.
  """

  def __init__(self, old, new, path=None, patch_format="deepdiff"):
    """
    Intialises the class from a deepdiff or
    a rfc6902 patch. deepdiff is the default.

    old_value -- Old Value (can be an object, dict, string or other object type)
                 which we want to compare the changes from
    new_value -- New Value which we want to see what has been changed from old
                 value
    """
    self.old_value = old
    self.new_value = new
    self.patch_format = patch_format

  def getPortalPatchOperationList(self):
    """
    List all PortalPatchOperation instances in the PortalPatch
    """
    patch = self.asDeepDiffPatch()
    # In general, we are using `tree` view, so basically for us all operations
    # currently are `values_changed` from old to new value or to none
    change_list = patch.values()
    # Here we can have the change_list as nested list also, for example:
    #
    #  change_list =
    #   {
    #   'iterable_item_removed': set([<root[2] t1:'c', t2:Not Present>]),
    #   'values_changed': set([<root[1] t1:'b', t2:'e'>, <root[0] t1:'a', t2:'d'>])
    #   }
    # We can see here that the values are basically change from one value to
    # another, so to get the list of operation(s), we have to flatten all the
    # values in one list
    flatten_change_list = [item for sublist in change_list for item in sublist]
    return flatten_change_list

  def patchPortalObject(self, obj):
    """
    Apply patch to an object by applying
    one by one each PortalPatchItem
    """
    pass

  def asDeepDiffPatch(self):
    """
    Returns a Json patch with deep diff extensions
    """
    # Use try-except as it's easier to ask forgiveness than permission

    # `_asDict` is available only for objects, so in that case, we convert the
    # ERP5-fied objects into dict and then work on them.
    # In all other cases, we let `deepdiff` do its work on checking the type
    try:
      src = self.old_value._asDict()
    except AttributeError:
      src = self.old_value

    try:
      dst = self.new_value._asDict()
    except AttributeError:
      dst = self.new_value

    # For now, we prefer having 'tree' view as it provides us with node level
    # where on each node we have value changed(atleast for list and dictionary)
    ddiff = DeepDiff(src, dst, view='tree')
    return ddiff

  def asBeautifiedJSONDiff(self):
    """
    Returns beautified JSON diff in format:
    {
    'diff': <diff>
    't1': <old_value>
    't2': <new_value>
    'path', <property_name>
    }
    """
    old_value_dict = self.removeProperties(self.old_value, export=True)
    new_value_dict = self.removeProperties(self.new_value, export=True)

    #old_value_dict = self.old_value.__dict__
    #new_value_dict = self.new_value.__dict__

    # Get the DeepDiff in tree format.
    tree_diff = DeepDiff(old_value_dict,
                          new_value_dict,
                          view='tree')
    diff_tree_list = []

    # Flatten the list of DiffValues
    for key, subset in tree_diff.items():
      if isinstance(subset, set):
        sublist = list(subset)
        for item in sublist:
          # XXX: This is important as the subsets with iterable item removed
          # do always have items which are diffing the items in list and not the
          # complete list, hence we get paths as root[<list_name>][<index_no>]
          # which is inconsistent to manage in string formatting, thus we have
          # decided to use the parent list by using .up
          if key in ('iterable_item_removed',):
            diff_tree_list.append(item.up)
          else:
            diff_tree_list.append(item)

    # Create a beautified list from the diff
    diff_list = []

    for val in diff_tree_list:
      new_val = {}

      diff = val.additional.get('diff', None)
      # If there is diff in additional property, save it separately
      if diff:
        # Add space in front of each newline character as it validates the diff
        diff = diff.replace('\n', ' \n')

        patch = PatchSet(diff)
        try:
          patch = patch[0]
          # In case there are multiple hunks, do create separate value dict for
          # each of them
          for l in patch:
            new_val = {}
            # Add the headers on top of every patch as they are needed for
            # rendering as pretty HTML
            new_val['diff'] = "---  \n+++  \n" + str(l)
            new_val['t1'] = val.t1
            new_val['t2'] = val.t2
            new_val['path'] = val.path()[6:-2]
            diff_list.append(new_val)
        except KeyError:
          pass
      else:
        old_value = val.t1
        new_value = val.t2
        if (val.t1 == None) or isinstance(val.t1, deepdiff.helper.NotPresent):
          old_value = ''
        if (val.t2 == None) or isinstance(val.t2, deepdiff.helper.NotPresent):
          new_value = ''

        try:
          # Create own patch for single line strings
          new_val['diff'] = "---  \n+++  \n" + "@@ -1,%s +1,%s @@\n" % (len(str(old_value)), len(str(new_value))) + "- %s\n+ %s\n" % (str(old_value), str(new_value))
        except ValueError:
          new_val['diff'] = None
        new_val['path'] = val.path()[6:-2]
        new_val['t1'] = val.t1
        new_val['t2'] = val.t2

        diff_list.append(new_val)

    # Sort the list of dictionaries according to the path
    sorted_diff_list = sorted(diff_list, key=lambda k: k['path'])

    return sorted_diff_list

  def removeProperties(self,
                       obj,
                       export,
                       properties=[],
                       keep_workflow_history=False,
                       keep_workflow_history_last_history_only=False):
    """
    Remove unneeded properties for export and then return dict which has only
    useful properties.
    """
    obj._p_activate()
    klass = obj.__class__
    classname = klass.__name__
    attr_set = {'_dav_writelocks', '_filepath', '_owner', '_related_index',
                'last_id', 'uid', '_mt_index', '_count', '_tree',
                '__ac_local_roles__', '__ac_local_roles_group_id_dict__',
                'workflow_history', 'subject_set_uid_dict', 'security_uid_dict',
                'filter_dict', '_max_uid', 'isIndexable', 'id', 'modification_date'}
    if properties:
      for prop in properties:
        if prop.endswith('_list'):
          prop = prop[:-5]
        attr_set.add(prop)
    if export:
      if keep_workflow_history_last_history_only:
        self._removeAllButLastWorkflowHistory(obj)
      elif not keep_workflow_history:
        attr_set.add('workflow_history')
      # PythonScript covers both Zope Python scripts
      # and ERP5 Python Scripts
      if isinstance(obj, PythonScript):
        attr_set.update(('func_code', 'func_defaults', '_code',
                         '_lazy_compilation', 'Python_magic', 'errors',
                         'warnings', '_proxy_roles'))
      elif classname in ('File', 'Image'):
        attr_set.update(('_EtagSupport__etag', 'size'))
      elif classname == 'SQL' and klass.__module__ == 'Products.ZSQLMethods.SQL':
        attr_set.update(('_arg', 'template'))
      elif interfaces.IIdGenerator.providedBy(obj):
        attr_set.update(('last_max_id_dict', 'last_id_dict'))
      elif classname == 'Types Tool' and klass.__module__ == 'erp5.portal_type':
        attr_set.add('type_provider_list')

    # Copy the dict and then remove the undesriable properties
    obj_dict = obj.showDict().copy()
    for attr in obj_dict.keys():
      if attr in attr_set or attr.startswith('_cache_cookie_') or attr.startswith('_v'):
        try:
          del obj_dict[attr]
        except KeyError:
          # XXX: Continue in cases where we want to delete some properties which
          # are not in attribute list
          # Raise an error
          continue

    return obj_dict


  def asStrippedHTML(self):
    """
    Returns an HTML representation of the whole patch
    that can be embedded
    """
    pass

  def asHTML(self):
    """
    Returns an HTML representation of the whole patch
    that can be displayed in a standalone way
    """
    pass

class PortalPatchOperation:
  """
    Provides an abstraction to a patch operation that
    depends on the patch format.

    In the case of deepdiff, each operation defines
    actually a desired state in a declarative way.

    In the case of rfc6902, each operation is defined
    in an imperative manner.
  """

  def patchPortalObject(self, obj, unified_diff_selection=None):
    """
      Apply patch to an object

      unified_diff_selection -- a selection of lines in the unified diff
                                that will be applied
    """
    pass

  def getOperation(self):
    """
      Returns one of "replace", "add" or "remove"

      (hopefully, this can also be used for deepdiff format)
      set_item_added, values_changed, etc.
    """
    pass

  def getPath(self):
    """
      Returns a path representing the value that is changed
      (hopefully, this can also be used for deepdiff format)
    """
    pass

  def getOldValue(self):
    """
      Returns the old value
    """
    pass

  def getNewValue(self):
    """
      Returns the new value
    """
    pass

  def getUnifiedDiff(self):
    """
      Returns a unified diff of the value changed
      (this is useful for a text value) or None if
      there is no such change.

      (see String difference 2 in deepdiff)
    """
    pass

  def asStrippedHTML(self):
    """
      Returns an HTML representation of the change
      that can be embedded
    """
    pass

  def asHTML(self):
    """
      Returns an HTML representation that can be displayed
      in a standalone way
    """
    pass

InitializeClass(DiffTool)
