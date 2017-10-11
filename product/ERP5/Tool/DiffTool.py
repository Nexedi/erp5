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

import jsonpatch
from deepdiff import DeepDiff

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions

class DiffTool(BaseTool):
  """
  A portal tool that provides all kinds of utilities to
  compare objects.
  """
  id = 'portal_diff'
  title = 'Diff Tool'
  meta_type = 'ERP5 Diff Tool'
  portal_type = 'Portal Diff Tool'
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
    return PortalPatch(old, new, patch_format)


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

  def __init__(self, old, new, patch_format="deepdiff"):
    """
    Intialises the class from a deepdiff or
    a rfc6902 patch. deepdiff is the default.
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

  def patchPortalObject(self, object):
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

  def patchPortalObject(object, unified_diff_selection=None):
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
