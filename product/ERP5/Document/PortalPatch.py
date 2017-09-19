##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet

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

  meta_type = 'Portal Patch'
  portal_type = 'Portal Patch'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def __init__(self, patch_text, patch_format="deepdiff"):
    """
    Intialises the class from a deepdiff or
    a rfc6902 patch. deepdiff is the default.
    """
    pass

  def getPortalPatchOperationList(self):
    """
    List all PortalPatchItem instances in the PortalPatch
    """
    pass

  def patchPortalObject(self, object):
    """
    Apply patch to an object by applying
    one by one each PortalPatchItem
    """
    pass

  def asJSONPatch(self):
    """
    Returns a Json patch in line with rfc6902
    """
    pass

  def asDeepDiffPatch(self):
    """
    Returns a Json patch with deep diff extensions
    """
    pass

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
