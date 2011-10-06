import zope
import hashlib
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
    """Navigation not implemented

    Payzen.eu assumes that POST is done directly to the website thus there is
    no need to provide "proxy" method.
    """
    raise NotImplementedError('Method will not be implemented')

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

  # proposed methods
  def getFormString(self, document, content_dict=None):
    """Returns unterminated form for current document

    The responsiblity of the caller is to finish the form."""
    self.Base_checkConsistency()
    if content_dict is None:
      content_dict = dict()
    content_dict['vads_action_mode'] = self.getPayzenVadsActionMode()
    content_dict['vads_amount'] = int(document.getTotalPrice() * 100)
    integration_tool = self.restrictedTraverse(self.getIntegrationSite())
    content_dict['vads_currency'] = integration_tool.getMappingFromCategory(
      'resource/currency_module/%s' % document.getPriceCurrencyReference()
      ).split('/')[-1]
    content_dict['vads_ctx_mode'] = self.getPayzenVadsCtxMode()
    content_dict['vads_page_action'] = self.getPayzenVadsPageAction()
    content_dict['vads_payment_config'] = document\
      .Base_getPayzenServicePaymentConfig()
    content_dict['vads_site_id'] = self.getServiceUsername()
    # date as YYYYMMDDHHMMSS
    content_dict['vads_trans_date'] = document.getStartDate().strftime(
      '%Y%m%d%H%M%S')
    content_dict['vads_trans_id'] = document.Base_getPayzenTransId()
    content_dict['vads_version'] = self.getPayzenVadsVersion()
    # all data are completed, now it is time to create signature
    sorted_keys = content_dict.keys()
    sorted_keys.sort()
    signature = ''
    form = '<FORM METHOD="POST" ACTION="%s">\n' % self.getLinkUrlString()
    for k in sorted_keys:
      v = str(content_dict[k])
      signature += v + '+'
      form += '<INPUT TYPE="HIDDEN" NAME="%s" VALUE="%s">\n' % (k, v)
    signature += self.getServicePassword()
    form += '<INPUT TYPE="HIDDEN" NAME="signature" VALUE="%s">' % \
      hashlib.sha1(signature).hexdigest()
    return form

  def getSignature(self, document):
    """Returns signature for current document"""

  def validateSignature(self, document, signature):
    """Checks if documents validates against signature"""
