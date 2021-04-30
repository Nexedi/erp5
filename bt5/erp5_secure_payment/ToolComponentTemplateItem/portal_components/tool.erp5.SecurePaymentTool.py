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

from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products import ERP5Security
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl import getSecurityManager

class SecurePaymentTool(BaseTool):
  """
    This tool manages payment gateway like PayPal, PayBox ...

    It is used as a central point of managment
  """
  id = 'portal_secure_payments'
  meta_type = 'ERP5 Secure Payment Tool'
  portal_type = 'Secure Payment Tool'
  title = 'Secure Payments'

  def find(self, service_reference="default"):
    """Search a payment service by reference"""
    if service_reference:
      result = self.searchFolder(reference=service_reference)
      if len(result) > 0:
        return result[0].getObject().__of__(self)

    raise ValueError("Impossible to find a payment service with '%s' reference" % service_reference)

  def _loginAsSuperUser(self):
    user = getSecurityManager().getUser()
    if not('Member' in user.getRoles()):
      newSecurityManager(None,
       self.getPortalObject().acl_users.getUserById(ERP5Security.SUPER_USER))

  def _getParametersFromSelection(self,service,selection):
    if selection is not None:
      params = self.portal_selections.getSelectionParamsFor(selection)
      service = params.pop('service', service)
      self.portal_selections.manage_deleteSelection(selection)
    else:
      params =  {}
    return service, params

  def initialize(self, service="default",
                       REQUEST=None, **kw):
    """Initialize the transaction with a service"""
    self._loginAsSuperUser()
    return self.find(service).initialize(REQUEST, **kw)

  def navigate(self, service="default",
                       REQUEST=None, **kw):
    """Navigate to service payment page"""
    return self.find(service).navigate(REQUEST, **kw)

  #Use selection to minimize fallback url length. In exemple, Paybox limit to
  #150 chars.
  def notifySuccess(self, service='default',selection=None, REQUEST=None):
    """Notify the user of successful transaction"""
    service, params = self._getParametersFromSelection(service,selection)
    return self.find(service).notifySuccess(REQUEST=REQUEST, **params)

  def notifyFail(self, service='default',selection=None, REQUEST=None):
    """Notify the user of failed transaction"""
    service, params = self._getParametersFromSelection(service,selection)
    return self.find(service).notifyFail(REQUEST=REQUEST, **params)

  def notifyCancel(self, service='default',selection=None, REQUEST=None):
    """Notify the user of cancelled transaction"""
    service, params = self._getParametersFromSelection(service,selection)
    return self.find(service).notifyCancel(REQUEST=REQUEST, **params)

  def reportPaymentStatus(self, service='default', REQUEST=None):
    """Notify the service of cancelled transaction"""
    self._loginAsSuperUser()
    return self.find(service).reportPaymentStatus(REQUEST=REQUEST)
