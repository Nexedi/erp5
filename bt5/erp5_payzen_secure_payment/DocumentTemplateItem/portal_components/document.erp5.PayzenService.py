import zope
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
import hashlib
from zLOG import LOG, WARNING
import base64
import datetime
import os
import time
import requests
from Products.ERP5Type.Core.Workflow import ValidationFailed
import six

present = False
tz = None
if 'TZ' in os.environ:
  present = True
  tz = os.environ['TZ']
os.environ['TZ'] = 'UTC'
time.tzset()
def setUTCTimeZone(fn):
  def wrapped(*args, **kwargs):
    present = False
    tz = None
    if 'TZ' in os.environ:
      present = True
      tz = os.environ['TZ']
    os.environ['TZ'] = 'UTC'
    time.tzset()
    try:
      return fn(*args, **kwargs)
    finally:
      if present:
        os.environ['TZ'] = tz
      else:
        del(os.environ['TZ'])
      time.tzset()
  return wrapped

if present:
  os.environ['TZ'] = tz
else:
  del(os.environ['TZ'])
time.tzset()

class PayzenREST:
  """REST communication

  Methods are returning list of:
    * parsed response
    * sent Data
    * received Data
  """

  def callPayzenApi(self, URL, payzen_dict):
    base64string = base64.encodebytes(
      ('%s:%s' % (
        self.getServiceUsername(),
        self.getServiceApiKey())).encode()).decode().replace('\n', '')
    header = {"Authorization": "Basic %s" % base64string}
    LOG('callPayzenApi', WARNING,
        "data = %s URL = %s" % (str(payzen_dict), URL), error=False)
    # send data
    result = requests.post(URL, data=payzen_dict, headers=header)
    try:
      data = result.json()
    except Exception:
      data = {}
      LOG('PayzenService', WARNING,
        'Issue during processing data_kw:', error=True)
    return data, result.text


  @setUTCTimeZone
  def rest_getInfo(self, transmissionDate, transactionId):
    """Returns getInfo as dict, booelan, string, string

    transmissionDate is "raw" date in format YYYYMMDD, without any marks
    transactionId is id of transaction for this date

    As soon as communication happeneded does not raise.
    """
    URL = "https://api.payzen.eu/api-payment/V4/Order/Get"
    kw = dict(
      orderId=transactionId,
    )
    sent_data = str(kw)
    data_kw, received_data = self.callPayzenApi(URL, kw)
    return [data_kw, sent_data, received_data]


from erp5.component.interface.IPaymentService import IPaymentService
@zope.interface.implementer(IPaymentService)
class PayzenService(XMLObject, PayzenREST):
  meta_type = 'Payzen Service'
  portal_type = 'Payzen Service'

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

  def _getSignature(self, ob, sorted_key_list):
    """Calculates signature from ob

    ob can be dict or getattr capable object

    in case if ob is a dict all .strftime callable values
    are converted to datetime soapish format
    """
    if isinstance(ob, dict):
      isdict = True
    else:
      isdict = False

    signature = ''
    for k in sorted_key_list:
      if isdict:
        v = ob[k]
      else:
        v = getattr(ob, k, None)
      if v is None:
        # empty or not transmitted -- add as empty
        v = ''
      elif isinstance(v, datetime.datetime):
        # for sure date
        v = v.strftime('%Y%m%d')
      elif isinstance(v, bool):
        v = str(int(v))
      else:
        # anything else cast to string
        v = str(v)
      signature += v + '+'
    signature += self.getServicePassword()
    return hashlib.sha1(signature.encode('utf-8')).hexdigest()

  def _getFieldList(self, payzen_dict):
    payzen_dict.update(
      vads_action_mode=self.getPayzenVadsActionMode(),
      vads_ctx_mode=self.getPayzenVadsCtxMode(),
      vads_contrib='ERP5',
      vads_page_action=self.getPayzenVadsPageAction(),
      vads_payment_config='SINGLE',
      vads_site_id=self.getServiceUsername(),
      vads_version=self.getPayzenVadsVersion()
    )
    # fetch all prepared vads_ values and remove them from dict
    signature = self._getSignature(payzen_dict, sorted(six.iterkeys(payzen_dict)))
    payzen_dict['signature'] = signature
    return sorted(six.iteritems(payzen_dict))

  def navigate(self, page_template, payzen_dict, REQUEST=None, **kw):
    """Returns configured template used to do the payment"""
    check_result = self.checkConsistency()
    message_list = []
    for err in check_result:
      if getattr(err, 'getTranslatedMessage', None) is not None:
        message_list.append(err.getTranslatedMessage())
      else:
        # backward compatibility:
        message_list.append(err[3])
    if message_list:
      raise ValidationFailed(message_list)

    temp_document = self.newContent(temp_object=True, portal_type='Document', id='id')
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
