# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#               Hervé Poulain <herve@nexedi.com>
#               Mayoro DIAGNE <mayoro@gmail.com>
#               Mohamadou MBENGUE <mmbengue@gmail.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from erp5.component.module.TioSafeBaseConduit import TioSafeBaseConduit
from erp5.component.module.SyncMLConstant import XUPDATE_INSERT_OR_ADD_LIST
from zLOG import LOG

class ERP5PaymentTransactionConduit(TioSafeBaseConduit):
  """
    This is the conduit use to synchonize tiosafe payment transaction and ERP5
  """
  def __init__(self):
    # Define the object_tag element to add object
    self.xml_object_tag = 'transaction'

  def getObjectAsXML(self, object, domain): # pylint: disable=redefined-builtin
    return object.PaymentTransaction_asTioSafeXML(context_document=domain)

  def updateNode(self, xml=None, object=None, previous_xml=None, force=0, # pylint: disable=redefined-builtin
      simulate=0,  **kw):
    raise Exception('updateNode: Impossible to update transaction')

  def deleteNode(self, xml=None, object=None, previous_xml=None, force=0, # pylint: disable=redefined-builtin
      simulate=0,  **kw):
    raise Exception('deleteNode: Impossible to delete transaction')

  def _createSaleTradeCondition(self, object, **kw): # pylint: disable=redefined-builtin
    """ Link payment transaction to a sale trade condition so that
      we can filter payment transaction based on the plugin they came from
    """
    site = self.getIntegrationSite(kw.get('domain'))
    default_stc = site.getSourceTrade()

    stc_title = "%s %s" % (site.getReference(), object.getTitle())

    #if the stc already exist, invalidate it
    stc_list = [x.getObject() for x in
		object.getPortalObject().sale_trade_condition_module.searchFolder(title=stc_title,
		       								 validation_state='validated')]
    for sale_trade_cond in stc_list:
      #Get the related objet and invalidate related payment transaction
      for payment_transaction in sale_trade_cond.Base_getRelatedObjectList(portal_type="Payment Transaction",
                                                 			   simulation_state="confirmed"):

        transaction = payment_transaction.getObject()
        transaction.cancel()
      #Invalidate the STC
      sale_trade_cond.invalidate()

    # Create the STC
    stc = object.getPortalObject().sale_trade_condition_module.newContent(title=stc_title,
		    specialise=default_stc,
		    version='001')
    stc.validate()

    return stc

  def _deleteSaleTradeCondition(self, object, **kw): # pylint: disable=redefined-builtin
    """ Unvalidate sale trade condition so that
        we can filter payment transaction based on the plugin they came from
    """
    stc_list = object.Base_getRelatedObjectList(portal_type="Sale Trade Condition",
                                                validation_state="validated")
    for stc in stc_list:
      stc.getObject().invalidate()

  def _createContent(self, xml=None, object=None, object_id=None, sub_object=None, # pylint: disable=redefined-builtin
      reset_local_roles=0, reset_workflow=0, simulate=0, **kw):
    """
      This is the method calling to create an object
    """
    if object_id is None:
      object_id = self.getAttribute(xml, 'id')
    if True: #object_id is not None:
      if sub_object is None and object_id:
        try:
          sub_object = object._getOb(object_id)
        except (AttributeError, KeyError, TypeError):
          sub_object = None
      if sub_object is None: # If so, it doesn't exist
        portal_type = ''
        if xml.xpath('local-name()') == self.xml_object_tag:
          portal_type = self.getObjectType(xml)
        elif xml.xpath('name()') in XUPDATE_INSERT_OR_ADD_LIST: # Deprecated ???
          portal_type = self.getXupdateContentType(xml) # Deprecated ???
        sub_object, reset_local_roles, reset_workflow = self.constructContent(
            object,
            object_id,
            portal_type,
        )

        # Define the Bank Account and the currency by using the one defined on IS
        integration_site = self.getIntegrationSite(kw.get('domain'))
        price_currency = integration_site.getDefaultPriceCurrency().split("/")[-1]
        link_object = object.portal_catalog.getResultValue(
           portal_type='Currency',
           reference=price_currency,
        )
        sub_object.setPriceCurrencyValue(link_object)
        bank_account_object = integration_site.getDefaultSourcePaymentValue()
        sub_object.setDefaultSourcePaymentValue(bank_account_object)
        sub_object.setSourceSectionValue(bank_account_object.getParentValue())

        # Mapping between tag and element
        node_dict = {
            'arrow': self.visitArrow,
            'movement': self.visitMovement,
        }
        # if exist namespace retrieve only the tag
        index = 0
        if xml.nsmap not in [None, {}]:
          index = -1

        # Browse the list of arrows and movements
        for node in xml.getchildren():
          # Only works on right tags, and no on the comments, ...
          if not isinstance(node.tag, str):
            continue
          # Build the tag (without is Namespace)
          tag = node.tag.split('}')[index]
          # Treat sub-element
          if len(node.getchildren()):
            if tag in node_dict:
              node_dict[tag](document=sub_object, xml=node, **kw)
            else:
              raise ValueError("This is an unknown sub-element %s on %s" %(tag, sub_object.getPath()))
          elif tag in ['start_date', 'stop_date']:
            if not node.text:
              node.text = None
          elif tag  == "payment_mode":
            sub_object.setPaymentMode(node.text)
      # Build the content of new Payment Transaction
      self.newObject(
          object=sub_object,
          xml=xml,
          simulate=simulate,
          reset_local_roles=reset_local_roles,
          reset_workflow=reset_workflow,
      )

      # Add the stc and create relation with the new object
      sale_trade_condition = self._createSaleTradeCondition(sub_object, **kw)
      sub_object.setSpecialise(sale_trade_condition.getRelativeUrl())

    return sub_object


  def afterNewObject(self, object, **kw): # pylint: disable=redefined-builtin
    """ Confirm the payment transaction and, add the grants on this one. """
    if object.getPortalType() in ['Payment Transaction',]:
      ## first delete default generated accounting transaction line: bank,
      ## receivable and payable to have "No diff" on XML diff between pub and sub
      removable_id_list = ["bank", "receivable", "payable"]
      object.manage_delObjects(removable_id_list)
      object.confirm()
    object.updateLocalRolesOnSecurityGroups()


  def visitArrow(self, document=None, xml=None, **kw):
    """ Manage the addition of sources and destination in the payment transaction. """

    return

  def visitMovement(self, document=None, xml=None, **kw):
    """ Manage the addition of the Sale Order Line. """

    # dictionary of the value of a movement
    movement_dict_value = {'category': []}

    # if exist namespace retrieve only the tag
    index = 0
    if xml.nsmap not in [None, {}]:
      index = -1

    integration_site = self.getIntegrationSite(kw.get('domain'))
    #default_resource = integration_site.getResourceValue()
    #default_resource_gid = integration_site.product_module.getSourceSectionValue().getGidFromObject(default_resource, encoded=False)

    # browse the xml and save the sale order line values
    for subnode in xml.getchildren():
      # only works on tags, no on the comments or other kind of tag
      if not isinstance(subnode.tag, str):
        continue
      tag = subnode.tag.split('}')[index]
      # set line values in the dict
      if subnode.text is not None:
        movement_dict_value[tag] = subnode.text#.encode('utf-8')
    LOG("visitMovement", 300, "movement_dict_value = %s" %(movement_dict_value))

    # no variations will be use for the unknown product
    # Create the new Sale Order Line
    payment_transaction_line = document.newContent(portal_type='Accounting Transaction Line')
    source_account = integration_site.getSource()
    payment_transaction_line.setSource(source_account)
    # define the setters of the accounting transaction line
    mapping_of_setter = {
        'title': payment_transaction_line.setTitle,
        'reference': payment_transaction_line.setReference,
    }

    # set on the sale order line or on cell the values
    for key in movement_dict_value:
      if key in mapping_of_setter:
        mapping_of_setter[key](movement_dict_value[key])
      elif key == "price":
        price =float(movement_dict_value[key])
        if price > 0:
          payment_transaction_line.setSourceCredit(price)
        else:
          payment_transaction_line.setSourceDebit(-price)

  def editDocument(self, object=None, **kw): # pylint: disable=redefined-builtin
    """
      This is the default editDocument method. This method
      can easily be overwritten.
    """
    # Mapping of the PropertySheet
    mapping = {
        'title': 'title',
        'start_date': 'start_date',
        'stop_date': 'stop_date',
        'reference': 'reference',
        'causality': 'comment',
    }
    property_ = {}
    # Translate kw with the good PropertySheet
    for k, v in kw.items():
      k = mapping.get(k, k)
      property_[k] = v
    object._edit(**property_)

