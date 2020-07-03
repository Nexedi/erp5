from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from Products.ERP5 import _dtmldir
from Products.ERP5Type import Permissions
from Products.ERP5Type.Tool.BaseTool import BaseTool

""" ERP5 portal_integrations tool """
class IntegrationTool(BaseTool):
  """
    The IntegrationTool is used to exchange with the differents external management systems.
  """

  id = 'portal_integrations'
  title = 'Integration Tool'
  meta_type = 'ERP5 Integration Tool'
  portal_type = 'Integration Tool'
  allowed_type = ()

  # Declarative Security
  security = ClassSecurityInfo()

  # ZMI Methods
  security.declareProtected(Permissions.ManagePortal, 'manage_overview')
  manage_overview = DTMLFile('explainIntegrationTool', _dtmldir)


InitializeClass(IntegrationTool)

