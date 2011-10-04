import zope
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject

class PayzenService(XMLObject):
  meta_type = 'Payzen Service'
  portal_type = 'Payzen Service'

  zope.interface.implements(interfaces.IPaymentService)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.Reference
                    )
  def initialize(self, REQUEST=None, **kw):
    """See Payment Service Interface Documentation"""
    pass

  def navigate(self, REQUEST=None, **kw):
    """Redirect to payzen.eu"""
    self.Base_checkConsistency()
    raise NotImplementedError

  def notifySuccess(self, REQUEST=None, **kw):
    """See Payment Service Interface Documentation"""
    raise NotImplementedError
    return self._getTypeBasedMethod("acceptPayment")(**kw)

  def notifyFail(self, REQUEST=None, **kw):
    """See Payment Service Interface Documentation"""
    raise NotImplementedError
    return self._getTypeBasedMethod("failInPayment")(**kw)

  def notifyCancel(self, REQUEST=None, **kw):
    """See Payment Service Interface Documentation"""
    raise NotImplementedError
    return self._getTypeBasedMethod("abortPayment")(**kw)
