# -*- coding: utf-8 -*-
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

import pdb

from zLOG import LOG
import unittest
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeLiveTestCase import ERP5TypeLiveTestCase

class ViFiBOrderTest(ERP5TypeLiveTestCase):
  """Unit test of the ViFiB use case

  Summary :

  - Open Order : tells which services have been requested
    and their price. Records which contracts have been approved
    by the client (aggregate) for which product. 

    Price can be defined explicitely (for each invoiceable
    product) or through a specialise relation to a Sales Supply.

    Also sometimes tells "how many" are planned to be ordered.

  - Trade Condition : provides invoicing and payment information
    of the client, as well as tax conditions
    (WARNING: composition takes the latest condition always)

  - Software: a given service (ex. Prestashop Hosting). Different 
    releases are possible (ex. Prestashop R1, Prestashop R2)
    which may have a different price (or not). The list of releases
    can be defined through Sales Supply/aggregate... In addition,
    the list of applicable licenses (a kind of contract) can also
    be defined though aggregate relation from the software. 

    Through a relation (predecessor) tells which other products
    may be required to purchase at the same time and (successor)
    which other products could be purchased at the same time.
    Similar product (similar) are also provided.

  - Licence Contract: a document which must be approved to get a
    given Software (a.k.a. Software Licence)

  UC1 - Simple

  1- Client goes to online shop and select product (ie. software product)

  2- Client clicks "Order" (impl quantity = 1) of given software product
  and specified which software release he or she wants.

  3- System sends confirmation request (ex. an email which request payment,
  email confirmation, etc.) 

  4- Client does confirmation (ex. click on email confirmation, click on
  payment, etc.) and agrees with latest trade conditions (which 
  are displayed at the same time).

  5- System confirms order

  6a- System generates "Open Order" if no "Open Order" already existed
  for the client

  6b- System updates "Open Order" with missing pricing information applicable
  to the given order (ex. price of network, of instance hosting etc.)
  Such missing pricing information is gathered by looking at "predecessor" of
  the Sofware Product and updating the Open Order with such information.
  (explicit approach)

  6c- System updates "Open Order" with latest contractual obligations

  6d- System generates Trade Condition for the client if none existed

  6e- System updates Trade Condition specialise relation with latest
  Trade Condition parents (QUESTION: this creates an issue related to 
  versioning and composition)

  7- System generates Subscription Item, Computer Partition and Packing List
  of relevant quantity of given "Sofware Product" (license...) with
  Software Release as well as "Instance Setup" (license...) with given
  Software Release. (and it is thus possible this way to count how many
  licenses someone has...)
    ex. 10 "TioLIve Free"
        Computer Partition 1.... Computer Partition 10
        Subscription Item 1.... Subscription Item 10
        Software Instane 1.... Software Instance 10
  """
  cleanup_list = []

  def getTitle(self):
    return "SampleTest"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install. This
    is only useful for command line based tests.
    """
    return ('erp5_base',)

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    self.cleanup_list = []
    self.now = DateTime()
    
    # XXX
    #self.login('jp')    

  #def beforeClear(self):
  #  """This method should be moved up to ERP5TypeLiveTestCase
  #  or to a subclass of it
  #
  #  XXX beforeClear was removed from ERP5TypeLiveTestCase
  #  XXX when should should cleanupGarbage be called ?
  #  """
  #  self.cleanupGarbage()

  def collectGarbage(self, document):
    """Keeps a list of documents to erase at the end of the test
    """
    self.cleanup_list.append(document)

  def cleanupGarbage(self):
    for document in self.cleanup_list:
      parent = document.getParentValue()
      document_id = document.getId()
      #if document_id in parent.objectIds():
      parent.manage_delObjects(ids=[document_id])

  def step_01_selectProduct(self):
    """Client goes to online shop and select product (ie. software product)
    
    TODO: use real web site methods
    """
    portal = self.getPortalObject()
    self.logMessage('user is %s' % portal.portal_membership.getAuthenticatedMember())
    self.order = portal.sale_order_module.newContent(title="Live Test Order",
                      portal_type="Sale Order",
                      source="organisation_module/vifib_internet",
                      source_section="organisation_module/vifib_internet",
                      destination="organisation_module/vifib_client_A",
                      destination_section="organisation_module/vifib_client_A",
                      start_date=self.now,
                      stop_date=self.now,
                      specialise='sale_trade_condition_module/vifib_trade_condition',
                                                    )
    self.order_line = self.order.newContent(title="Live Test Order Line", 
                                            portal_type="Sale Order Line",
                                            # resource="service_module/vm_monthly_hosting",
                                            resource=self.portal.portal_preferences.getPreferredInstanceSetupResource(),
                                            aggregate="software_release_module/test_software_release",
                                            quantity=1,
                                            price=20.0,)
    self.collectGarbage(self.order)
        
    # Is the order is draft state ?
    self.assertEqual(self.order.getSimulationState(), 'draft')

    # Does the order have one line ?
    self.assertEqual(len(self.order.objectValues(portal_type="Sale Order Line")), 1)

    # Is the first line a hosting resource ?
    order_line = self.order.objectValues(portal_type="Sale Order Line")[0]
    self.assertEqual(order_line.getResource(),
                     self.portal.portal_preferences.\
                            getPreferredInstanceSetupResource())

    # With quantity 1
    self.assertEqual(order_line.getQuantity(), 1.0)

  def step_02_orderProduct(self):
    """Client clicks "Order" (impl quantity = 1) of given software product
    and specified which software release he or she wants.

    TODO: use real web site methods
    """
    self.order.plan()

    # Is the order is ordered state ?
    self.assertEqual(self.order.getSimulationState(), 'planned')

  def step_02_checkPlannedOrderConsistency(self):
    """
    """
    # Make sure applied rule is present in simulation
    applied_rule_list = self.order.getCausalityRelatedValueList()
    self.assertEqual(len(applied_rule_list), 1)

    # With one simulation movement inside 
    applied_rule = applied_rule_list[0]
    self.assertEqual(len(applied_rule.contentIds()), 1)

    # WIth one delivery rule inside
    simulation_movement = applied_rule.contentValues()[0]
    self.assertEqual(len(simulation_movement.contentIds()), 1)

    delivery_applied_rule = simulation_movement.contentValues()[0]
    self.assertEqual(delivery_applied_rule.getSpecialiseValue().getReference(),
                     "default_delivering_rule")

    # With one simulation movement inside 
    self.assertEqual(len(delivery_applied_rule.contentIds()), 1)

  def step_03_sendConfirmationRequest(self):
    """System sends confirmation request (ex. an email which request payment,
    email confirmation, etc.) 

    TODO: use real web site methods
    """
    # Not implemented yet (ask FX)
    pass

  def step_04_clientConfirmation(self):
    """Client does confirmation (ex. click on email confirmation, click on
    payment, etc.) and agrees with latest trade conditions (which 
    are displayed at the same time).

    TODO: use real web site methods, through acknowledgement tool
    """
    self.order.order()

    # Is the order is ordered state ?
    self.assertEqual(self.order.getSimulationState(), 'ordered')

    software_instance = self.order.software_instance_module.newContent(
      portal_type="Software Instance",
      text_content="""
"""
    )
    self.order_line.edit(
      aggregate_list=self.order_line.getAggregateList()+[software_instance.getRelativeUrl()]
    )

  def step_05_orderConfirmation(self):
    """System confirms order

    TODO: 
    """
    self.order.confirm() # This part should be automatic as the result of acknowledge

    # Is the order is confirmed state ?
    self.assertEqual(self.order.getSimulationState(), 'confirmed')

  def step_06_generateOpenOrder(self):
    """System generates "Open Order" if no "Open Order" already existed
    for the client

    TODO:
    """
    open_order_list = self.order.open_sale_order_module.searchFolder(
      destination_section_uid=self.order.getDestinationSectionUid(),
      simulation_state="started")
    self.assertEquals(len(open_order_list), 1)

  def step_07_updateOpenOrderPrice(self):
    """ System updates "Open Order" with missing pricing information applicable
    to the given order (ex. price of network, of instance hosting etc.)
    Such missing pricing information is gathered by looking at "predecessor" of
    the Sofware Product and updating the Open Order with such information.
    (explicit approach)

    TODO:
    """
    raise NotImplementedError("TODO")

  def step_08_updateOpenOrderLegal(self):
    """System updates "Open Order" with latest contractual obligations

    TODO:
    """
    raise NotImplementedError("TODO")

  def step_09_generateTradeCondition(self):
    """System generates Trade Condition for the client if none existed

    TODO:
    """
    raise NotImplementedError("TODO")

  def step_10_updateTradeCondition(self):
    """System updates Trade Condition specialise relation with latest
    Trade Condition parents (QUESTION: this creates an issue related to 
    versioning and composition)

    TODO:
    """
    raise NotImplementedError("TODO")

  def step_11_generateSubscriptionItem(self):
    """ System generates Subscription Item, Computer Partition and Packing List
    of relevant quantity of given "Sofware Product" (license...) with
    Software Release as well as "Instance Setup" (license...) with given
    Software Release. (and it is thus possible this way to count how many
    licenses someone has...)
    
    ex. 10 "TioLIve Free"
        Computer Partition 1.... Computer Partition 10
        Subscription Item 1.... Subscription Item 10
        Software Instane 1.... Software Instance 10

    TODO:
    """
    raise NotImplementedError("TODO")

  def step_12_generateInvoice(self):
    """System generated invoice for one month subscription.

    TODO:
    """
    raise NotImplementedError("TODO")

  def step_13_generateInvoiceTransaction(self):
    """System generated invoice transaction one month subscription.

    TODO:
    """
    raise NotImplementedError("TODO")

  def step_14_generatePayment(self):
    """System generated payment transaction one month subscription
    (in special account for online payment).

    TODO:
    """
    raise NotImplementedError("TODO")

  def test_01_simpleUseCase(self):
    """
    """    
    self.step_01_selectProduct()
    self.step_02_orderProduct()
    self.stepTic()
    self.step_02_checkPlannedOrderConsistency()
    self.step_03_sendConfirmationRequest()
    self.step_04_clientConfirmation()
    self.stepTic()
    self.step_05_orderConfirmation()
    self.stepTic()
    self.step_06_generateOpenOrder()
    self.step_07_updateOpenOrderPrice()
    self.step_08_updateOpenOrderLegal()
    self.step_09_generateTradeCondition()
    self.step_10_updateTradeCondition()
    self.step_11_generateSubscriptionItem()
    self.step_12_generateInvoice()
    self.step_13_generateInvoiceTransaction()
    self.step_14_generatePayment()
