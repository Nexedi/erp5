##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Message import translateString
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin

class BusinessProcessConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Setup Rules. """

  meta_type = 'ERP5 Business Process Configurator Item'
  portal_type = 'Business Process Configurator Item'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IConfiguratorItem)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.ConfiguratorItem
                    , PropertySheet.Reference
                    )

  def _checkConsistency(self, fixit=False, filter=None, **kw):
    error_list = ["Business Process %s should be created" % self.getReference(),]
    if fixit:
      portal = self.getPortalObject()
      business_process = portal.business_process_module.newContent(
                                            portal_type="Business Process",
                                            reference=self.getReference(),
                                            title=self.getTitle())
      business_configuration = self.getBusinessConfigurationValue()
      business_configuration.setGlobalConfigurationAttr(\
                    business_process_id=business_process.getId())
      business_configuration.setGlobalConfigurationAttr(\
        business_process_path='business_process_module/%s' %business_process.getId())


      business_process_dict = self._getBusinessProcessDict()
      int_index = 0
      for path_dict in business_process_dict["Trade Model Path"]:
        int_index += 1
        path_dict.setdefault("int_index", int_index)
        title = path_dict.pop('title')
        trade_phase = path_dict.pop('trade_phase')
        trade_date = path_dict.pop('trade_date')
        for key in path_dict:
          if path_dict[key] is None:
            path_dict.pop(key)
        self._addTradeModelPath(business_process=business_process,
                                title=title,
                                trade_phase=trade_phase,
                                trade_date=trade_date,
                                **path_dict)

      int_index = 0
      for link_dict in business_process_dict["Business Link"]:
        int_index += 1
        link_dict.setdefault("int_index", int_index)
        title = link_dict.pop('title')
        trade_phase = link_dict.pop('trade_phase')
        delivery_builder = link_dict.pop('delivery_builder', None)
        predecessor = link_dict.pop('predecessor', None)
        successor = link_dict.pop('successor', None)
        for key in path_dict:
          if path_dict[key] is None:
            path_dict.pop(key)

        self._addBusinessLink(business_process=business_process,
                              title=title,
                              trade_phase = trade_phase,
                              predecessor = predecessor,
                              successor = successor,
                              delivery_builder = delivery_builder,
                              **link_dict)

      business_process.validate(comment=translateString('Validated by configurator'))
      self.install(business_process, business_configuration)

    return error_list

  def _getBusinessProcessDict(self):
    """ Read the spreadsheet and return the configuration for
        Trade Model Paths and Business Links.
    """
    return self.ConfigurationTemplate_readOOCalcFile(
                      "standard_business_process.ods",
                      data=self.getDefaultConfigurationSpreadsheetData())



  def _addTradeModelPath(self, business_process, title, trade_phase,
                                                       trade_date, **kw):
    """ Add a trade model path to the business process.
    """
    reference = "TMP-%s" % "-".join(title.upper().strip().split(" "))
    path_id = "%s_path" %  "_".join(title.lower().strip().split(" "))
    trade_model_path = business_process.newContent(
                                portal_type = "Trade Model Path",
                                id = path_id,
                                title = title,
                                reference = reference, **kw)

    trade_model_path.setTradePhase(trade_phase)
    if trade_date is not None:
      trade_model_path.setTradeDate('trade_phase/%s' % trade_date)

  def _addBusinessLink(self, business_process, title, trade_phase, predecessor,
                             successor, delivery_builder, **kw):
    link_id = "%s_link" %  "_".join(title.lower().strip().split(" "))
    business_link = business_process.newContent(
                                portal_type = "Business Link",
                                id=link_id,
                                title = title,**kw)

    completed_state = kw.pop("completed_state", None)
    if completed_state is not None:
      business_link.setCompletedStateList(completed_state.split(","))

    frozen_state = kw.pop("frozen_state", None)
    if frozen_state is not None:
      business_link.setFrozenStateList(frozen_state.split(","))

    business_link.setTradePhase(trade_phase)
    if successor is not None:
      business_link.setSuccessor("trade_state/%s" % successor)
    if predecessor is not None:
      business_link.setPredecessor("trade_state/%s" % predecessor)

    if delivery_builder is not None:
      business_link.setDeliveryBuilderList(
             ["delivery_builder/portal_deliveries/%s" % \
                  i for i in delivery_builder.split(",")])
