# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    François-Xavier Algrain <fxalgrain@tiolive.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import zope
from urllib import urlencode
from urllib2 import urlopen, Request
from zLOG import LOG, DEBUG
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject


class PaypalService(XMLObject):
  """Paypal Service for payment"""

  meta_type = 'Paypal Service'
  portal_type = 'Paypal Service'
  security = ClassSecurityInfo()
  zope.interface.implements(interfaces.IPaymentService)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (PropertySheet.Base,
                     PropertySheet.XMLObject,
                     PropertySheet.Reference
                    )

  def initialize(self, REQUEST=None, **kw):
    """See Payment Service Interface Documentation"""

  def _getFieldList(self, paypal_dict):
    field_list = []
    for k,v in paypal_dict.iteritems():
      field_list.append((k, v))
    return field_list

  def navigate(self, REQUEST=None, **kw):
    """See Payment Service Interface Documentation"""
    page_template = kw.pop("page_template")
    paypal_dict = kw.get("paypal_dict", {})
    temp_document = self.newContent(
      portal_type='Document',
      temp_object=True,
      link_url_string=self.getLinkUrlString(),
      title=self.getTitle(),
      field_list=self._getFieldList(paypal_dict),
      # append the rest of transmitted parameters page template
      **kw
    )
    return getattr(temp_document, page_template)()

  def notifySuccess(self, redirect_path=None, REQUEST=None):
    """See Payment Service Interface Documentation"""
    return self._getTypeBasedMethod("acceptPayment")(redirect_path=redirect_path)

  def notifyFail(self, redirect_path=None, REQUEST=None):
    """See Payment Service Interface Documentation"""
    return self._getTypeBasedMethod("failInPayment")(redirect_path=redirect_path)

  def notifyCancel(self, redirect_path=None, REQUEST=None):
    """See Payment Service Interface Documentation"""
    return self._getTypeBasedMethod("abortPayment")(redirect_path=redirect_path)

  def reportPaymentStatus(self, REQUEST=None):
    """See Payment Service Interface Documentation"""
    param_dict = REQUEST.form
    LOG("PaypalService", DEBUG, param_dict)
    param_dict["cmd"] = "_notify-validate"
    if param_dict.has_key("service"):
      param_dict.pop("service")
    param_list = urlencode(param_dict)
    paypal_url = self.getLinkUrlString()
    request = Request(paypal_url, param_list)
    request.add_header("Content-type", "application/x-www-form-urlencoded")
    response = urlopen(request)
    status = response.read()
    LOG("PaypalService status", DEBUG, status)
    method_id = self._getTypeBasedMethod("reportPaymentStatus").id
    getattr(self.activate(), method_id)(response_dict=REQUEST.form)
    return status == "VERIFIED"