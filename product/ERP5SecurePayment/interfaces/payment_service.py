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
"""
Products.ERP5SecurePayment.interfaces.payment_service
"""

from zope.interface import Interface

class IPaymentService(Interface):
  """Payment Service interface specification

  IPaymentService defines the minimal method required to define a payment service
  wich can be used by the payment tool  
  """
  
  def initialize(self, REQUEST=None, **kw):
    """Initialize the service to be ready to start the transaction
    """
    
  def navigate(self, REQUEST=None, **kw):
    """Redirects User to the payment page.

    Implementation shall prepare service's expected HTTP query and return
    correct HTTP response to browser which will lead to external payment page
    with all required parameters.
    """
    
  def reportPaymentStatus(self, REQUEST=None):
    """Server side notification of payment status"""
  
  def notifySuccess(self, REQUEST=None, **kw):
    """Fallback method when transaction is a success
    """
    
  def notifyFail(self, REQUEST=None, **kw):
    """Fallback method when transaction fails
    """
    
  def notifyCancel(self, REQUEST=None, **kw):
    """Fallback method when transaction is cancelled
    """
