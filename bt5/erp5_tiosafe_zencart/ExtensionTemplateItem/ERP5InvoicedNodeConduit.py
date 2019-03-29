##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5TioSafe.Conduit.ERP5NodeConduit import ERP5NodeConduit


class ERP5InvoicedNodeConduit(ERP5NodeConduit):


  def _createSaleTradeCondition(self, object, **kw):
    """ Link person to a sale trade condition so that
    we can filter person based on the plugin they came from
    """
    site = self.getIntegrationSite(kw['domain'])
    default_stc = site.getSourceTrade()
    # Create the STC
    stc = object.getPortalObject().sale_trade_condition_module.newContent(title="%s %s" %(site.getReference(), object.getTitle()),
                                                                        specialise=default_stc,
                                                                        destination_decision=object.getRelativeUrl(),
                                                                        destination_administration=object.getRelativeUrl(),
                                                                        version=0o01)
    stc.validate()

  def _updateSaleTradeCondition(self, object, **kw):
    """ Link person to a sale trade condition so that
    we can filter person based on the plugin they came from
    """
    site = self.getIntegrationSite(kw['domain'])
    default_stc = site.getSourceTrade()
    # try to find the corresponding STC
    stc_list = object.getPortalObject().sale_trade_condition_module.searchFolder(title="%s %s" %(site.getReference(), object.getTitle()),
                                                                                validation_state="validated"
                                                                                )
    if len(stc_list) == 0:
      self._createSaleTradeCondition(object, **kw)
    elif len(stc_list) > 1:
      raise ValueError("Multiple trade condition (%s) retrieve for %s" %([x.path for x in stc_list], object.getTitle()))
    else:
      stc = stc_list[0].getObject()
      stc.edit(destination_decision=object.getRelativeUrl(),
               destination_administration=object.getRelativeUrl(),)


  def _deleteSaleTradeCondition(self, object):
    stc_list = object.Base_getRelatedObjectList(portal_type="Sale Trade Condition",
                                     validation_state="validated")
    for stc in stc_list:
      stc = stc.getObject()
      stc.edit(destination_decision=None,
               destination_administration=None)

