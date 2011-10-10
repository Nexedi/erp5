import zope
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Document import newTempDocument
import hashlib

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

  def _getSignature(self, field_list):
    field_list.sort()
    signature = ''
    for k, v in field_list:
      signature += v + '+'
    signature += self.getServicePassword()
    return hashlib.sha1(signature).hexdigest()

  def _getFieldList(self, payzen_dict):
    field_list = [
      ('vads_action_mode', self.getPayzenVadsActionMode()),
      ('vads_ctx_mode', self.getPayzenVadsCtxMode()),
      ('vads_contrib', 'ERP5'),
      ('vads_page_action', self.getPayzenVadsPageAction()),
      ('vads_payment_config', 'SINGLE'),
      ('vads_site_id', self.getServiceUsername()),
      ('vads_version', self.getPayzenVadsVersion())
    ]
    # fetch all prepared vads_ values and remove them from dict
    for k,v in payzen_dict.iteritems():
      field_list.append((k, v))
    signature = self._getSignature(field_list)
    field_list.append(('signature', signature))
    return field_list

  def navigate(self, page_template, payzen_dict, REQUEST=None, **kw):
    """Returns configured template used to do the payment"""
    self.Base_checkConsistency()
    temp_document = newTempDocument(self, 'id')
    temp_document.edit(
      link_url_string=self.getLinkUrlString(),
      title='title',
      field_list=self._getFieldList(payzen_dict),
      # append the rest of transmitted parameters page template
      **kw
    )
    return getattr(temp_document, page_template)()

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
