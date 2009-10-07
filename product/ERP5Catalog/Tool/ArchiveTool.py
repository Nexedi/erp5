##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5Type.Cache import CachingMethod, clearCache
from Products.ERP5Catalog import _dtmldir
from zLOG import LOG, INFO

class ArchiveTool(BaseTool):
  """
  Archive Tool contains archive objects
  """
  title = 'Archive Tool'
  id = 'portal_archives'
  meta_type = 'ERP5 Archive Tool'
  portal_type = 'Archive Tool'
  allowed_types = ('ERP5 Archive',)

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ManagePortal, 'manage_overview' )

  manage_overview = DTMLFile( 'explainArchiveTool', _dtmldir)


  def getSQLCatalogIdList(self):
    """
    Wrapper to CatalogTool method
    """
    return self.portal_catalog.getSQLCatalogIdList()

  def SQLConnectionIDs(self):
    """
    Wrapper to CatalogTool method
    """
    return self.portal_catalog.SQLConnectionIDs()

  def getArchiveIdList(self):
    """
    Return list of usable archive displayed to user
    """
    return ["%s - %s" %(x.getId(), x.getTitle()) for x in \
            self.portal_catalog(portal_type="Archive",
                                validation_state="ready")]


  def getCurrentArchive(self):
    """
    Return the archive used for the current catalog
    """
    current_catalog = self.portal_catalog.default_sql_catalog_id
    current_archive_list = [x.getObject() for x in self.searchFolder(validation_state="validated") \
                            if x.getCatalogId() == current_catalog]
    if len(current_archive_list) == 0:
      return None
    else:
      return current_archive_list[0]


  def getArchiveList(self):
    """
    Return the list of archive use by catalog
    """
    def _getArchiveList():
      return [x.getPath() for x in self.objectValues() if x.getValidationState() == "validated"]

    #     getArchiveList = CachingMethod(_getArchiveList,
    #                                    id='getArchiveList',
    #                                    cache_factory='erp5_content_short')
    
    return _getArchiveList()


  def manage_archive(self, destination_archive_id,
                     archive_id,
                     update_destination_sql_catalog=None,
                     update_archive_sql_catalog=None,
                     clear_destination_sql_catalog=None,
                     clear_archive_sql_catalog=None,                                            
                     REQUEST=None, RESPONSE=None):
    """
    This method is used to populate an archive from the current catalog
    It is base on hot reindexing, we start from a current catalog
    in order to create a new current catalog plus an archive catalog.
    Archives are defined in portal_archives, they are predicate thus
    we use test method to know in which catalog objects must go.
    At the end it creates inventories in order to have
    consistent data within the new catalog
    """
    # First check parameter for destination catalog
    if destination_archive_id == archive_id:
      raise ValueError, "Archive and destination archive can't be the same"
    portal_catalog =self.portal_catalog
    # Guess connection id from current catalog
    source_catalog = portal_catalog.getSQLCatalog()
    source_catalog_id = source_catalog.getId()
    source_connection_id = None
    source_deferred_connection_id = None
    for method in source_catalog.objectValues():
      if method.meta_type == "Z SQL Method":
        if 'deferred' in method.connection_id:
          source_deferred_connection_id = method.connection_id
        elif 'transactionless' not in method.connection_id:
          source_connection_id = method.connection_id
        if source_connection_id is not None and \
           source_deferred_connection_id is not None:
          break

    if source_connection_id is None or source_deferred_connection_id is None:
      raise ValueError, "Unable to determine connection id for the current catalog"

    # Get destination property from archive
    destination_archive_id = destination_archive_id.split(' - ')[0]
    destination_archive = self._getOb(destination_archive_id)
    destination_sql_catalog_id = destination_archive.getCatalogId()
    destination_connection_id = destination_archive.getConnectionId()
    destination_deferred_connection_id = destination_archive.getDeferredConnectionId()

    # Get archive property from archive
    archive_id = archive_id.split(' - ')[0]
    archive = self._getOb(archive_id)
    archive_sql_catalog_id = archive.getCatalogId()
    archive_connection_id = archive.getConnectionId()
    archive_deferred_connection_id = archive.getDeferredConnectionId()
    
    # Check we don't use same connection id for source and destination
    if destination_sql_catalog_id == source_catalog_id:
      raise ValueError, "Destination and source catalog can't be the same"
    if destination_connection_id == source_connection_id:
      raise ValueError, "Destination and source connection can't be the same"
    if destination_deferred_connection_id == source_deferred_connection_id:
      raise ValueError, "Destination and source deferred connection can't be the same"
    # Same for source and archive
    if archive_sql_catalog_id == source_catalog_id:
      raise ValueError, "Archive and source catalog can't be the same"
    if archive_connection_id == source_connection_id:
      raise ValueError, "Archive and source connection can't be the same"
    if archive_deferred_connection_id == source_deferred_connection_id:
      raise ValueError, "Archive and source deferred connection can't be the same"
    # Same for destination and archive
    if archive_sql_catalog_id == destination_sql_catalog_id:
      raise ValueError, "Archive and destination catalog can't be the same"
    if archive_connection_id == destination_connection_id:
      raise ValueError, "Archive and destination connection can't be the same"
    if archive_deferred_connection_id == destination_deferred_connection_id:
      raise ValueError, "Archive and destination deferred connection can't be the same"
        
    # Update connection id in destination and archive catalog if asked
    destination_sql_catalog = getattr(portal_catalog, destination_sql_catalog_id)
    if update_destination_sql_catalog:
      sql_connection_id_dict = {source_connection_id : destination_connection_id,
                                source_deferred_connection_id : destination_deferred_connection_id}
      portal_catalog.changeSQLConnectionIds(destination_sql_catalog,
                                  sql_connection_id_dict)

    archive_sql_catalog = getattr(portal_catalog, archive_sql_catalog_id)
    if update_archive_sql_catalog:
      sql_connection_id_dict = {source_connection_id : archive_connection_id,
                                source_deferred_connection_id : archive_deferred_connection_id}                
      portal_catalog.changeSQLConnectionIds(archive_sql_catalog,
                                  sql_connection_id_dict)

    # Clear destination and archive catalog if asked
    if clear_destination_sql_catalog:
      portal_catalog.manage_catalogClear(sql_catalog_id=destination_sql_catalog_id)
    if clear_archive_sql_catalog:
      portal_catalog.manage_catalogClear(sql_catalog_id=archive_sql_catalog_id)

    # validate archive
    archive.validate()
    destination_archive.validate()

    # Call hot reindexing
    portal_catalog.manage_hotReindexAll(source_sql_catalog_id=source_catalog_id,
                                             destination_sql_catalog_id=destination_sql_catalog_id,
                                             archive_path=archive.getPath(),
                                             source_sql_connection_id_list=[source_connection_id, \
                                                                            source_deferred_connection_id],
                                             destination_sql_connection_id_list=[destination_connection_id, \
                                                                                 destination_deferred_connection_id],
                                             REQUEST=REQUEST, RESPONSE=RESPONSE)

    # Create inventory just before finish of hot reindexing
    inventory_date = archive.getStopDateRangeMax()
    self.activate(passive_commit=1,
                  after_method_id=('playBackRecordedObjectList'),
                  priority=5).runInventoryMethod(archive.id,
                                                 source_connection_id,
                                                 destination_sql_catalog_id,
                                                 inventory_date
                                                 )
    

    self.activate(passive_commit=1,
                  after_method_id=('runInventoryMethod'),
                  after_tag="runInventoryMethod",
                  priority=5).InventoryModule_reindexMovementList(sql_catalog_id=destination_sql_catalog_id,
                                                                  final_activity_tag="InventoryModule_reindexMovementList"
                                                                  )

    if RESPONSE is not None:
      URL1 = REQUEST.get('URL1')
      RESPONSE.redirect(URL1 + '/portal_archives?portal_status_message=Archiving%20Started')


  def runInventoryMethod(self, archive_id, source_connection_id,
                         destination_sql_catalog_id, inventory_date):
    """
    Use a specific method to create inventory in order to use
    activity to execute it
    """
    archive = self._getOb(archive_id)
    inventory_method_id = archive.getInventoryMethodId()
    inventory_method = getattr(archive, inventory_method_id, None)
    if inventory_method is not None:
      inventory_method(source_connection_id, destination_sql_catalog_id,
                       inventory_date, tag='runInventoryMethod')
    

InitializeClass(ArchiveTool)
