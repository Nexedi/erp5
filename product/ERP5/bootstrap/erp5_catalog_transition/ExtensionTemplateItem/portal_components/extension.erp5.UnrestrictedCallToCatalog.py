def getTableIdsUnrestricted(self):
  """
  This fucntion calls getTableIds function from Catalog Class in ZSQLCatalog.
  The reason we need it here is that we need to get the result from the
  restricted environment which isn't possible from inside ERP5.
  
  This is because we are moving Catalog inside ERP5 and converting it to
  Folder object.
  """
  
  # Get portal object
  portal = self.getPortalObject()

  # Get current ERP5 Catalog objects
  default_erp5_catalog = portal.portal_catalog.getERP5Catalog()

  return default_erp5_catalog.getTableIds()

def getCatalogMethodIdsUnrestricted(self):
  """
  This fucntion calls getCatalogMethodIds function from Catalog Class in ZSQLCatalog.
  The reason we need it here is that we need to get the result from the
  restricted environment which isn't possible from inside ERP5.
  
  This is because we are moving Catalog inside ERP5 and converting it to
  Folder object.
  """

  # Get portal object
  portal = self.getPortalObject()

  # Get current ERP5 Catalog objects
  default_erp5_catalog = portal.portal_catalog.getERP5Catalog()

  return default_erp5_catalog.getCatalogMethodIds()

def getResultColumnIdsUnrestricted(self):
  """
  This fucntion calls getResultColumnIds function from Catalog Class in ZSQLCatalog.
  The reason we need it here is that we need to get the result from the
  restricted environment which isn't possible from inside ERP5.
  
  This is because we are moving Catalog inside ERP5 and converting it to
  Folder object.
  """

  # Get portal object
  portal = self.getPortalObject()

  # Get current ERP5 Catalog objects
  default_erp5_catalog = portal.portal_catalog.getERP5Catalog()

  return default_erp5_catalog.getResultColumnIds()

def getColumnIdsUnrestricted(self):
  """
  This fucntion calls getCOlumnIds function from Catalog Class in ZSQLCatalog.
  The reason we need it here is that we need to get the result from the
  restricted environment which isn't possible from inside ERP5.
  
  This is because we are moving Catalog inside ERP5 and converting it to
  Folder object.
  """

  # Get portal object
  portal = self.getPortalObject()

  # Get current ERP5 Catalog objects
  default_erp5_catalog = portal.portal_catalog.getERP5Catalog()

  return default_erp5_catalog.getColumnIds()

def getSortColumnIdsUnrestricted(self):
  """
  This fucntion calls getSortColumnIds function from Catalog Class in ZSQLCatalog.
  The reason we need it here is that we need to get the result from the
  restricted environment which isn't possible from inside ERP5.
  
  This is because we are moving Catalog inside ERP5 and converting it to
  Folder object.
  """

  # Get portal object
  portal = self.getPortalObject()

  # Get current ERP5 Catalog objects
  default_erp5_catalog = portal.portal_catalog.getERP5Catalog()

  return default_erp5_catalog.getSortColumnIds()

def getPythonMethodIdsUnrestricted(self):
  """
  This fucntion calls getPythonMethodIds function from Catalog Class in ZSQLCatalog.
  The reason we need it here is that we need to get the result from the
  restricted environment which isn't possible from inside ERP5.
  
  This is because we are moving Catalog inside ERP5 and converting it to
  Folder object.
  """

  # Get portal object
  portal = self.getPortalObject()

  # Get current ERP5 Catalog objects
  default_erp5_catalog = portal.portal_catalog.getERP5Catalog()

  return default_erp5_catalog.getPythonMethodIds()

def getSQLCatalogIdListUnrestricted(self):
  """
  This fucntion calls getSQLCatalogIdList function from ZCatalog Class.
  The reason we need it here is that we need to get the result from the
  restricted environment which isn't possible from inside ERP5.
  
  This is because we are moving Catalog inside ERP5 and converting it to
  Folder object.
  """

  # Get portal object
  portal = self.getPortalObject()

  return portal.portal_catalog.getSQLCatalogIdList()
