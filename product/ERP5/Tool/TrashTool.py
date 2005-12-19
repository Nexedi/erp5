##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir
from zLOG import LOG
from DateTime import DateTime
from Acquisition import aq_base

class TrashTool(BaseTool):
  """
    TrashTool manage removed object from installation of BusinessTemplates
  """
  title = 'Trash Tool'
  id = 'portal_trash'
  meta_type = 'ERP5 Trash Tool'
  portal_type = 'Trash Tool'
  allowed_types = ('ERP5 Trash Bin',)

  # Declarative Security
  security = ClassSecurityInfo()
  
  security.declareProtected(Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainRuleTool', _dtmldir )

  def backupObject(self, trashbin, container_path, object_id, save, **kw):
    """
      Backup an object in a trash bin
    """
#     LOG('Trash : backup object', 0, str((container_path, object_id)))
    if save:
      # recreate path of the backup object if necessary
      backup_object_container = trashbin
      for path in container_path:
        if 'portal' in path:
          path += '_items'
        if path not in backup_object_container.objectIds():
          backup_object_container = backup_object_container.newContent(portal_type='Trash Folder', id=path, is_indexable=0)
          backup_object_container.edit(isHidden=1)
        else:
          backup_object_container = backup_object_container._getOb(path)
      # backup the object
      # here we choose export/import to copy because cut/paste
      # do too many things and check for what we want to do
      if object_id not in backup_object_container.objectIds():
        # export object
        object_path = container_path + [object_id]
        obj = self.unrestrictedTraverse(object_path)
        copy = obj._p_jar.exportFile(obj._p_oid)
        # import object in trash
        connection = backup_object_container._p_jar
        o = backup_object_container
        while connection is None:
          o = o.aq_parent
          connection=o._p_jar
        copy.seek(0)
        backup = connection.importFile(copy)
        backup.isIndexable = 0
        backup_object_container._setObject(object_id, backup)
        
    keep_sub = kw.get('keep_subobjects', 0)
    subobjects_dict = {}
    if not keep_sub:
      # export subobjects
      if save:
        obj = backup_object_container._getOb(object_id)
      else:
        object_path = container_path + [object_id]
        obj = self.unrestrictedTraverse(object_path)
      for subobject_id in list(obj.objectIds()):
        subobject_path = object_path + [subobject_id]
        subobject = self.unrestrictedTraverse(subobject_path)
        subobject_copy = subobject._p_jar.exportFile(subobject._p_oid)
        subobjects_dict[subobject_id] = subobject_copy
        if save: # remove subobjecs from backup object
          obj.manage_delObjects([subobject_id])
#     LOG('return subobject dict', 0, subobjects_dict)
    return subobjects_dict

  def newTrashBin(self, bt_title='trash', bt=None):
    """
      Create a new trash bin at upgrade of bt
    """
#     LOG('new Trash bin for', 0, bt_title)
    # construct date
    date = DateTime()
    start_date = date.strftime('%Y-%m-%d')
    # generate id
    trash_ids = self.objectIds()
    n = 0
    new_trash_id = bt_title+'_'+start_date
    while  new_trash_id in trash_ids:
      n = n + 1
      new_trash_id = '%s_%s' %(bt_title+'_'+start_date, n)
    # create trash bin
#     LOG('creating trash bin with id', 0, new_trash_id)
    trashbin = self.newContent(portal_type='Trash Bin', id=new_trash_id, title=bt_title, start_date=start_date, causality_value=bt)
#     LOG('trash item created', 0, trashbin)
    return trashbin
  

  def getTrashBinObjectsList(self, trashbin):
    """
      Return a list of trash objects for a given trash bin
    """
    def getChildObjects(obj):
      object_list = []
      if hasattr(aq_base(obj), 'objectValues'):
        childObjects = obj.objectValues()
      if hasattr(aq_base(obj), 'isHidden'):
        if not obj.isHidden:
          object_list.append(obj)
      if len(childObjects) > 0:
        for o in childObjects:
          object_list.extend(getChildObjects(o))          
      else:
        object_list.append(obj)
      return object_list
              
    list = getChildObjects(trashbin)
    list.sort()
    return list



InitializeClass(TrashTool)
