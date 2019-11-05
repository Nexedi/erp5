import zope
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from zLOG import LOG, WARNING
import random, string, hashlib, urllib2, socket
from urlparse import urlparse
try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET


class WechatException(Exception):
  def __init__(self, msg):
    super(WechatException, self).__init__(msg)


class WechatService(XMLObject):
  meta_type = 'Wechat Service'
  portal_type = 'Wechat Service'

  ORDER_URL = "/pay/unifiedorder" # Wechat unified order API
  QUERY_URL = "/pay/orderquery"

  zope.interface.implements(interfaces.IPaymentService)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.Reference
                    )

  def generateRandomStr(self, random_length=24):
    alpha_num = string.ascii_letters + string.digits
    random_str = ''.join(random.choice(alpha_num) for i in range(random_length))
    return random_str


  def calculateSign(self, dict_content, key):
    # Calculate the sign according to the data_dict
    # The rule was defined by Wechat (Wrote in Chinese):
    # https://pay.weixin.qq.com/wiki/doc/api/native.php?chapter=4_3

    # 1. Sort it by dict order
    params_list = sorted(dict_content.items(), key=lambda e: e[0], reverse=False)
    # 2. Concatenate the list to a string
    params_str = "&".join(u"{}={}".format(k, v) for k, v in params_list)
    # 3. Add trade key in the end
    params_str = params_str + '&key=' + key

    md5 = hashlib.md5()  # Use MD5 mode
    md5.update(params_str.encode('utf-8'))
    sign = md5.hexdigest().upper()
    return sign


  def convert_xml_to_dict(self, xml_content):
    '''
    The XML returned by Wechat is like:
      <xml>
         <return_code><![CDATA[SUCCESS]]></return_code>
         <return_msg><![CDATA[OK]]></return_msg>
         <appid><![CDATA[wx2421b1c4370ec43b]]></appid>
         <mch_id><![CDATA[10000100]]></mch_id>
         <nonce_str><![CDATA[IITRi8Iabbblz1Jc]]></nonce_str>
         <openid><![CDATA[oUpF8uMuAJO_M2pxb1Q9zNjWeS6o]]></openid>
         <sign><![CDATA[7921E432F65EB8ED0CE9755F0E86D72F]]></sign>
         <result_code><![CDATA[SUCCESS]]></result_code>
         <prepay_id><![CDATA[wx201411101639507cbf6ffd8b0779950874]]></prepay_id>
         <trade_type><![CDATA[JSAPI]]></trade_type>
      </xml>
    '''
    try:
      t = ET.XML(xml_content)
    except ET.ParseError:
      return {}
    else:
      dict_content = dict([(child.tag, child.text) for child in t])
      return dict_content


  def convert_dict_to_xml(self, d):
    xml = '<xml>'
    for key, value in d.items():
      if isinstance(value, basestring):
        xml += '<{0}><![CDATA[{1}]]></{0}>'.format(key, value)
      else:
        xml += '<{0}>{1}</{0}>'.format(key, value)
    xml += '</xml>'
    return xml


  def getSandboxKey(self):
    SANDBOX_KEY_URL = self.getLinkUrlString() + "/sandboxnew/pay/getsignkey"
    params = {}
    params['mch_id'] = self.getServiceMchId()
    params['nonce_str'] = self.generateRandomStr()
    params['sign'] = self.calculateSign(params, self.getServiceApiKey())
    LOG('WechatService', WARNING,
      "getSandboxKey : data = %s SANDBOX_KEY_URL = %s" % (self.convert_dict_to_xml(params), SANDBOX_KEY_URL), error=False)
    result = urllib2.Request(SANDBOX_KEY_URL, data=self.convert_dict_to_xml(params))
    result_data = urllib2.urlopen(result)
    result_read = result_data.read()
    result_dict_content = self.convert_xml_to_dict(result_read)
    return_code = result_dict_content.get('return_code', '')
    if return_code=="SUCCESS":
      result_msg = result_dict_content['return_msg']
      if result_msg=="ok":
        sandbox_signkey = result_dict_content['sandbox_signkey']
        return sandbox_signkey
      raise Exception(result_dict_content['result_msg'].encode('utf-8'))
    raise Exception("Get sanbox key failed: " + str(result_dict_content))

  def callWechatApi(self, URL, wechat_dict):
    portal = self.getPortalObject()
    base_url = portal.absolute_url()
    wechat_url = self.getLinkUrlString()
    if self.getWechatMode() == "SANDBOX":
      key = self.getSandboxKey()
    else:
      key = self.getServiceApiKey()
    nonce_str = self.generateRandomStr()

    result = urlparse(base_url)
    spbill_create_ip = socket.gethostbyname(result.netloc)

    # Construct parameter for calling the Wechat payment URL
    wechat_dict['appid'] = self.getServiceAppid()
    wechat_dict['mch_id'] = self.getServiceMchId()
    wechat_dict['nonce_str'] = nonce_str
    if self.getWechatMode() == "SANDBOX":
      # This is for sandbox test, sandbox need the total_fee equal to 101 exactly
      wechat_dict['total_fee'] = 101 # unit is Fen, 1 CNY = 100 Fen
      wechat_url += "/sandboxnew"
    wechat_dict['spbill_create_ip'] = spbill_create_ip

    # generate signature
    wechat_dict['sign'] = self.calculateSign(wechat_dict, key)

    LOG('callWechatApi', WARNING,
      "data = %s URL = %s" % (self.convert_dict_to_xml(wechat_dict), wechat_url + URL), error=False)
    # send data
    result = urllib2.Request(wechat_url + URL, data=self.convert_dict_to_xml(wechat_dict))
    result_data = urllib2.urlopen(result)
    result_read = result_data.read()
    result_dict_content = self.convert_xml_to_dict(result_read)
    return_code = result_dict_content['return_code']
    if return_code=="SUCCESS":
      return result_dict_content
    else:
      raise Exception(u"ERROR could not communicate with Wechat (return_code {}: {})".format(return_code, result_dict_content.get("return_msg")))

  def getWechatPaymentURL(self, wechat_dict):
    portal = self.getPortalObject()
    base_url = portal.absolute_url()
    notify_url = base_url + "/ERP5Site_receiveWechatPaymentCallback"  # Wechat payment callback method
    wechat_dict['notify_url'] = notify_url
    wechat_dict['trade_type'] = "NATIVE"
    wechat_answer = self.callWechatApi(self.ORDER_URL, wechat_dict)
    result_code = wechat_answer['result_code']
    if result_code=="SUCCESS":
      return wechat_answer['code_url']
    else:
      raise Exception(u"ERROR Wechat notified a problem (result_code {}: {})".format(result_code, wechat_answer.get("err_code_des")))

  def queryWechatOrderStatus(self, wechat_dict):
    '''
      documentation(Chinese): https://pay.weixin.qq.com/wiki/doc/api/native.php?chapter=9_2
      The dict_content atleast should contains one of following:
      - transaction_id (str): wechat order number, use this in higher priority, it will return in the payment notify callback
      - out_trade_no(str): The order ID used inside ERP5, less than 32 characters, digits, alphabets, and "_-|*@", unique in ERP5
    '''
    if "transaction_id" not in wechat_dict and "out_trade_no" not in wechat_dict:
      raise WechatException("transaction_id or out_trade_no is needed for query the Wechat Order")

    return self.callWechatApi(self.QUERY_URL, wechat_dict)

  def receiveWechatPaymentNotify(self, request, *args, **kwargs):
    '''
    Receive the asychonized callback send by Wechat after user pay the order.
    Wechat will give us something like:
    <xml>
      <appid><![CDATA[wx6509f6e240dfae50]]></appid>
      <bank_type><![CDATA[CFT]]></bank_type>
      <cash_fee><![CDATA[1]]></cash_fee>
      <fee_type><![CDATA[CNY]]></fee_type>
      <is_subscribe><![CDATA[N]]></is_subscribe>
      <mch_id><![CDATA[14323929292]]></mch_id>
      <nonce_str><![CDATA[aCJv0SAwKY5Cxfi34mtCEM5SdNKexuXgnW]]></nonce_str>
      <openid><![CDATA[oHWl5w5M34hYM-ox2mn6Xatse7yCTs]]></openid>
      <out_trade_no><![CDATA[aHQDJyacUSGC]]></out_trade_no>
      <result_code><![CDATA[SUCCESS]]></result_code>
      <return_code><![CDATA[SUCCESS]]></return_code>
      <sign><![CDATA[C4F8B5B17A3E6203491A3B790A1D87ECEA]]></sign>
      <time_end><![CDATA[201712114144230]]></time_end>
      <total_fee>1</total_fee>
      <trade_type><![CDATA[NATIVE]]></trade_type>
      <transaction_id><![CDATA[4200000031201712112434025551875]]></transaction_id>
    </xml>
    '''

    wechat_account_configuration = self.ERP5Site_getWechatPaymentConfiguration()
    params = self.convert_xml_to_dict(request.body)

    if params.get("return_code") == "SUCCESS":
      # Connection is ok
      sign = params.pop('sign')
      recalcualted_sign = self.calculateSign(params, wechat_account_configuration['API_KEY'])
      if recalcualted_sign == sign:
        if params.get("result_code", None) == "SUCCESS":  # payment is ok
          # order number
          # out_trade_no = params.get("out_trade_no")
          # Wechat payment order ID
          # This is what we should use when we search the order in the wechat
          # transaction_id = params.get("out_trade_no")
          # Save the wechat payment order ID in somewhere.
          # We recevied the payment...
          # Process something
          # XXX: display the page the payment received.
          # container.REQUEST.RESPONSE.redirect("%s/#wechat_payment_confirmed")
          # We must tell Wechat we received the response. Otherwise wechat will keep send it within 24 hours
          # xml_str = convert_dict_to_xml({"return_code": "SUCCESS"})
          # return container.REQUEST.RESPONSE(xml_str)
          return '''
              <xml>
              <return_code><![CDATA[SUCCESS]]></return_code>
              <return_msg><![CDATA[OK]]></return_msg>
              </xml>
              '''
        else:
          print(u"{0}:{1}".format(params.get("err_code"), params.get("err_code_des")))
    else:
      # Error information
      print(params.get("return_msg").encode("utf-8"))

  def initialize(self, REQUEST=None, **kw):
    """See Payment Service Interface Documentation"""
    pass

  def navigate(self, wechat_dict, REQUEST=None, **kw):
    """Returns a redirection to the payment page"""
    LOG('WechatService', WARNING,
          'In Navigate', error=False)

    portal = self.getPortalObject()
    base_url = portal.absolute_url()

    return self.REQUEST.RESPONSE.redirect(
      "%s/#wechat_payment?trade_no=%s&price=%s&payment_url=%s" % (
        base_url,
        wechat_dict['out_trade_no'],
        wechat_dict['total_fee'],
        self.getWechatPaymentURL(wechat_dict)
      )
    )

  def notifySuccess(self, REQUEST=None, **kw):
    """See Payment Service Interface Documentation"""
    raise NotImplementedError

  def notifyFail(self, REQUEST=None, **kw):
    """See Payment Service Interface Documentation"""
    raise NotImplementedError

  def notifyCancel(self, REQUEST=None, **kw):
    """See Payment Service Interface Documentation"""
    raise NotImplementedError
