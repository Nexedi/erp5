from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool

class My2to3TestTool(BaseTool):
  id = 'portal_my2to3test'
  meta_type = 'ERP5 My2to3Test Tool'
  portal_type = 'My2to3Test Tool'

InitializeClass(My2to3TestTool)

1 / 2