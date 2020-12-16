from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool

""" ERP5 portal_integrations tool """
class IntegrationTool(BaseTool):
  """
    The IntegrationTool is used to exchange with the differents external management systems.
  """

  id = 'portal_integrations'
  title = 'Integrations'
  meta_type = 'ERP5 Integration Tool'
  portal_type = 'Integration Tool'
  allowed_type = ()

InitializeClass(IntegrationTool)

