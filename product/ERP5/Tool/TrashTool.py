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

import imp, re, sys
from AccessControl import ClassSecurityInfo
from ZODB.broken import Broken
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir
from zExceptions import BadRequest
from zLOG import LOG, WARNING
from DateTime import DateTime
from Acquisition import aq_base
from io import BytesIO

class TrashTool(BaseTool):
  """
    TrashTool contains objects removed/replaced during installation of business templates.
  """
  id = 'portal_trash'
  meta_type = 'ERP5 Trash Tool'
  portal_type = 'Trash Tool'
  title = 'Trash Bins'
  allowed_types = ('ERP5 Trash Bin',)

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainTrashTool', _dtmldir )

  security.declarePrivate('backupObject')
  def backupObject(self, trashbin, container_path, object_id, save, keep_subobjects=False):
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
          if not hasattr(aq_base(backup_object_container), "newContent"):
            backup_object_container.manage_addFolder(id=path,)
            backup_object_container = backup_object_container._getOb(path)
          else:
            backup_object_container = backup_object_container.newContent(portal_type='Trash Folder', id=path,
                                                                         is_indexable=0)
            backup_object_container.edit(isHidden=1)
        else:
          backup_object_container = backup_object_container._getOb(path)
      # backup the object
      # here we choose export/import to copy because cut/paste
      # do too many things and check for what we want to do
      object_path = container_path + [object_id]
      obj = self.unrestrictedTraverse(object_path, None)
      if obj is not None:
        connection = obj._p_jar
        o = obj
        while connection is None:
          o = o.aq_parent
          connection=o._p_jar
        if obj._p_oid is None:
          LOG("Trash Tool backupObject", WARNING,
              "Trying to backup uncommitted object %s" % object_path)
          return {}
        if isinstance(obj, Broken):
          LOG("Trash Tool backupObject", WARNING,
              "Can't backup broken object %s" % object_path)
          klass = obj.__class__
          if klass.__module__[:27] in ('Products.ERP5Type.Document.',
                                        'erp5.portal_type'):
            # meta_type is required so that a broken object
            # can be removed properly from a BTreeFolder2
            # (unfortunately, we can only guess it)
            klass.meta_type = 'ERP5' + re.subn('(?=[A-Z])', ' ',
                                                klass.__name__)[0]
          return {}
        copy = connection.exportFile(obj._p_oid)
        # import object in trash
        connection = backup_object_container._p_jar
        o = backup_object_container
        while connection is None:
          o = o.aq_parent
          connection=o._p_jar
        copy.seek(0)
        try:
          backup = connection.importFile(copy)
          backup.isIndexable = ConstantGetter('isIndexable', value=False)
          # the isIndexable setting above avoids the recursion of
          # manage_afterAdd on
          # Products.ERP5Type.CopySupport.CopySupport.manage_afterAdd()
          # but not on event subscribers, so we need to suppress_events,
          # otherwise subobjects will be reindexed
          backup_object_container._setObject(object_id, backup,
                                              suppress_events=True)
        except (AttributeError, ImportError):
          # XXX we can go here due to formulator because attribute
          # field_added doesn't not exists on parent if it is a Trash
          # Folder and not a Form, or a module for the old object is
          # already removed, and we cannot backup the object
          LOG("Trash Tool backupObject", WARNING,
              "Can't backup object %s" % object_path)
          return {}
        finally:
          copy.close()

    subobjects_dict = {}

    if not keep_subobjects:
      # export subobjects
      if save:
        obj = backup_object_container._getOb(object_id, None)
      else:
        object_path = container_path + [object_id]
        obj = self.unrestrictedTraverse(object_path, None)
      if obj is not None:
        for subobject_id in list(obj.objectIds()):
          subobject = obj[subobject_id]
          subobjects_dict[subobject_id] = subobject._p_jar.exportFile(
            subobject._p_oid, BytesIO())

          if save: # remove subobjecs from backup object
            obj._delObject(subobject_id)
            if subobject_id in obj.objectIds():
              LOG('Products.ERP5.Tool.TrashTool', WARNING,
                  'Cleaning corrupted BTreeFolder2 object at %r.' % \
                                                       (subobject.getRelativeUrl(),))
              obj._cleanup()
    return subobjects_dict

  security.declarePrivate('newTrashBin')
  def newTrashBin(self, bt_title='trash', bt=None):
    """
      Create a new trash bin at upgrade of bt
    """
    # construct date
    date = DateTime()
    start_date = date.strftime('%Y-%m-%d')

    def getBaseTrashId():
      ''' A little function to get an id without leading underscore
      '''
      base_id = '%s' % start_date
      if bt_title not in ('', None):
        base_id = '%s_%s' % (bt_title, base_id)
      return base_id

    # generate id
    trash_ids = self.objectIds()
    n = 0
    new_trash_id = getBaseTrashId()
    while new_trash_id in trash_ids:
      n += 1
      new_trash_id = '%s_%s' % (getBaseTrashId(), n)
    # create trash bin
    trashbin = self.newContent( portal_type     = 'Trash Bin'
                              , id              = new_trash_id
                              , title           = bt_title
                              , start_date      = start_date
                              , causality_value = bt
                              )
    return trashbin

  security.declarePrivate('restoreObject')
  def restoreObject(self, trashbin, container_path, object_id, pass_if_exist=True):
    """
      Restore an object from the trash bin (copy it under portal)
    """
    portal = self.getPortalObject()
    # recreate path of the backup object if necessary
    backup_object_container = portal
    for path in container_path:
      if path.endswith('_items'):
        path = path[0:-len('_items')]
      if path not in backup_object_container.objectIds():
        if not hasattr(aq_base(backup_object_container), "newContent"):
          backup_object_container.manage_addFolder(id=path,)
          backup_object_container = backup_object_container._getOb(path)
        else:
          backup_object_container = backup_object_container.newContent(
            portal_type='Folder',
            id=path,
          )
      else:
        backup_object_container = backup_object_container._getOb(path)
    # backup the object
    # here we choose export/import to copy because cut/paste
    # do too many things and check for what we want to do
    object_path = container_path + [object_id]
    obj = trashbin.restrictedTraverse(object_path, None)
    if obj is not None:
      connection = obj._p_jar
      o = obj
      while connection is None:
        o = o.aq_parent
        connection=o._p_jar
      if obj._p_oid is None:
        LOG("Trash Tool backupObject", WARNING,
            "Trying to backup uncommitted object %s" % object_path)
        return {}
      if isinstance(obj, Broken):
        LOG("Trash Tool backupObject", WARNING,
            "Can't backup broken object %s" % object_path)
        klass = obj.__class__
        if klass.__module__[:27] in ('Products.ERP5Type.Document.',
                                      'erp5.portal_type'):
          # meta_type is required so that a broken object
          # can be removed properly from a BTreeFolder2
          # (unfortunately, we can only guess it)
          klass.meta_type = 'ERP5' + re.subn('(?=[A-Z])', ' ',
                                              klass.__name__)[0]
        return
      copy = connection.exportFile(obj._p_oid)
      # import object in trash
      connection = backup_object_container._p_jar
      o = backup_object_container
      while connection is None:
        o = o.aq_parent
        connection=o._p_jar
      copy.seek(0)
      try:
        backup = connection.importFile(copy)
        if hasattr(aq_base(backup), 'isIndexable'):
          del backup.isIndexable
        backup_object_container._setObject(object_id, backup)
      except (AttributeError, ImportError):
        # XXX we can go here due to formulator because attribute
        # field_added doesn't not exists on parent if it is a Trash
        # Folder and not a Form, or a module for the old object is
        # already removed, and we cannot backup the object
        LOG("Trash Tool backupObject", WARNING,
            "Can't backup object %s" % object_path)
      except BadRequest:
        if pass_if_exist:
          pass

  security.declareProtected(Permissions.ManagePortal, 'getTrashBinObjectsList')
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
