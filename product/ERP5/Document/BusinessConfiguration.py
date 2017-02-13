# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ayush-Tiwari <ayush.tiwari@nexedi.com>
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

import hashlib
import fnmatch
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Globals import Persistent
from Acquisition import Implicit, aq_base, aq_inner, aq_parent

_MARKER = []

def _recursiveRemoveUid(obj):
  """Recusivly set uid to None, to prevent (un)indexing.
  This is used to prevent unindexing real objects when we delete subobjects on
  a copy of this object.
  """
  if getattr(aq_base(obj), 'uid', _MARKER) is not _MARKER:
    obj.uid = None
  for subobj in obj.objectValues():
    _recursiveRemoveUid(subobj)

class BusinessTemplate(XMLObject):

  """Business Template is responsible for saving objects and properties in
  an ERP5Site. Everything will be saved just via path"""

  meta_type = 'ERP5 Business Template'
  portal_type = 'Business Template'
  allowed_content_types = ('BusinessItem', )
  add_permission = Permissions.AddPortalContent

  _properties = (
    { 'id' : 'template_path',
      'type': 'lines',
      'default': 'python: ()',
      'acquisition_base_category'     : (),
      'acquisition_portal_type'       : (),
      'acquisition_depends'           : None,
      'acquisition_accessor_id'       : 'getTempaltePathList',
      'override'    : 1,
      'mode'        : 'w' },
     )

  template_path_list = ()

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.SimpleItem
                    , PropertySheet.CategoryCore
                    , PropertySheet.Version
                    )

  def getStatus(self):
    """
    Installed:      BI(s) are installed in OFS.
    Uninstalled:    Values for BI(s) at the current version removed from OFS.
    Reduced:        No two BI of same path exist at different layers.
    Flatenned:      BI(s) should be at the zeroth layer.
    Build:          BI(s) do have values from the OS DB.
    """
    pass

  def applytoERP5(self, DB):
    """Apply the flattened/reduced business template to the DB"""
    portal  = self.getPortalObject()

  security.declareProtected(Permissions.ManagePortal, 'storeTemplateData')
  def storeTemplateData(self):
    """
    Store data for objects in the ERP5
    """
    self._path_item_list = []
    path_item_list = self.getTemplatePathList()
    if not path_item_list:
      path_item_list = [l.split(' | ') for l in path_item_list]
    for path_item in path_list:
      self._path_item_list.append(BusinessItem(path[0], path[1], path[2]))

  def build(self, no_action=False, **kw):
    """Creates new values for business configuration from the values from
    OFS Database"""
    if not no_action:
      self.storeTemplateData()
      for path_item in self._path_item_list:
        path_item.build(self, **kw)

  def getTemplatePathList(self):
    return self.template_path_list

  security.declareProtected(Permissions.ManagePortal, 'getTemplatePathList')
  def _getTemplatePathList(self):
    result = self.getTemplatePathList()
    if not isinstance(result, tuple):
      result = tuple(result)
    return result

  def install(self):
    """Install the business template"""
    pass

  def upgrade(self):
    """Upgrade the business template"""
    pass

  def flatten(self):
    """
    Flattening a reduced business template with two path p1 and p2 where p1 <> p2:

    flatten([(p1, s1, l1, v1), (p2, s2, l2, v2)]) = [(p1, s1, 0, v1), (p2, s2, 0, v2)]
    A reduced business template BT is said to be flattened if and only if:
    flatten(BT) = BT
    """
    pass

  def reduceBT(self):
    """
    Reduce the current Business Template
    """
    pass

class BusinessItem(Implicit, Persistent):

  """Saves the path and values for objects, properties, etc, the
    attributes for a path configuration being:

    - path  (similar to an xpath expression)
    - sign  (+1/-1)
    - layer (0, 1, 2, 3, etc.)
    - value (a set of pickable value in python)
    - hash of the value"""

  def __init__(self, path, sign=1, layer=0, value=None, *args, **kw):
    """
    Initialize/update the attributes
    """
    self.__dict__.update(kw)
    self._path = path
    self._sign = int(sign)
    self._layer = int(layer)
    self._value = value
    # Generate hash of from the value
    self._sha = self._generateHash()

  def _generateHash(self):
    """
    Generate hash based on value for the object.
    Initially, for simplicity, we go on with SHA1 values only
    """
    if not self._value:
      # Raise in case there is no value for the BusinessItem object
      raise ValueError, "Value not defined for the %s BusinessItem" %self._path
    else:
      # Expects to raise error on case the value for the object is not
      # picklable
      sha1 = hashlib.sha1(self._value).hexdigest()

  def build(self, context, **kw):
    """
    Extract value for the given path from the OFS
    """
    p = context.getPortalObject()
    path = self._path
    include_subobjects = 0
    if path.endswith("**"):
      include_subobjects = 1
    for relative_url in self._resolvePath(p, [], path.split('/')):
      obj = p.unrestrictedTraverse(relative_url)
      obj = obj._getCopy(context)
      obj = obj.__of__(context)
      _recursiveRemoveUid(obj)
      self._value = obj

  def _resolvePath(self, folder, relative_url_list, id_list):
    """
      This method calls itself recursively.

      The folder is the current object which contains sub-objects.
      The list of ids are path components. If the list is empty,
      the current folder is valid.
    """
    if len(id_list) == 0:
      return ['/'.join(relative_url_list)]
    id = id_list[0]
    if re.search('[\*\?\[\]]', id) is None:
      # If the id has no meta character, do not have to check all objects.
      obj = folder._getOb(id, None)
      if obj is None:
        raise AttributeError, "Could not resolve '%s' during Business Item processing." % id
      return self._resolvePath(obj, relative_url_list + [id], id_list[1:])
    path_list = []
    for object_id in fnmatch.filter(folder.objectIds(), id):
      if object_id != "":
        path_list.extend(self._resolvePath(
            folder._getOb(object_id),
            relative_url_list + [object_id], id_list[1:]))
    return path_list

  def getBusinessPath(self):
    return self._path

  def getBusinessPathSign(self):
    return self._sign

  def getBusinessPathLayer(self):
    return self._layer

  def getBusinessPathValue(self):
    return self._value

  def getBusinessPathSha(self):
    return self._sha

  def getParentBusinessTemplate(self):
    return self.aq_parent

  def generateXML(self):
    """
    Generate XML for different objects/type/properties differently.
    1. Objects: Use XMLImportExport from ERP5Type
    2. For properties, first get the property type, then create XML object
    for the different property differenty(Use ObjectPropertyItem from BT5)
    3. For attributes, we can export part of the object, rather than exporting
    whole of the object
    """
    pass
