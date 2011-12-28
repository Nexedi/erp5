#from erp5.component import component, document, mixin, interface

#Base = component('Document Component', 'Base')
#Base = document.Base
#Base = document('Base', version='erp5')
from Products.ERP5Type.Base import Base

class TestDocument(Base):
  """
  """
  def getTiti(self):
    """
    """
    return "zozo"

