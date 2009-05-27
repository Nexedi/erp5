##############################################################################
# -*- coding: utf8 -*-
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import transaction
from DateTime import DateTime

class TestAcknowledgementTool(ERP5TypeTestCase):

  def getTitle(self):
    return "AcknowledgementTool"

  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_crm',)

  def test_01_checkAcknowledgementToolWithOneEvent(self):
    """
    Create an event of type site message, post it and check that the
    acknowledgement tool is able to see it
    """
    event_type = "Site Message"
    portal = self.getPortalObject()
    module = portal.getDefaultModule(event_type)
    event = module.newContent(portal_type=event_type)
    person_module = portal.getDefaultModule('Person')
    person = person_module.newContent(portal_type='Person', title='Seb',
                                      reference='seb')
    now = DateTime()
    event.edit(destination_value=person,
               text_content="A Nice Message",
               text_format="text/plain",
               title="foo",
               start_date = now-2,
               stop_date = now+2)
    portal.portal_workflow.doActionFor(event, 'start_action')
    self.assertEqual(event.getSimulationState(), 'started')
    transaction.commit()
    self.tic()

    acknowledgement_tool_kw = {}
    acknowledgement_tool_kw['user_name'] = 'seb'
    acknowledgement_tool_kw['portal_type'] = event_type
    document_url_list = portal.portal_acknowledgements\
                         .getUnreadDocumentUrlList(**acknowledgement_tool_kw)
    self.assertTrue(event.getRelativeUrl() in document_url_list)

    # function in order to retrieve many times the list of acknowledgements
    def getEventAcknowlegementList():
      acknowledgement_list = portal.portal_acknowledgements\
                         .getUnreadAcknowledgementList(
                                 **acknowledgement_tool_kw)
      event_acknowledgement_list = [x for x in acknowledgement_list 
         if x.getCausality() == event.getRelativeUrl()]
      return event_acknowledgement_list

    # We should have unread acknowledgement
    event_acknowledgement_list = getEventAcknowlegementList()
    self.assertEqual(1, len(event_acknowledgement_list))

    # Check that the content is retrieved on the original event
    event_acknowledgement = event_acknowledgement_list[0]
    self.assertEqual(event_acknowledgement.getTextContent(), "A Nice Message")

    # We know acknowledge the event
    acknowledgement = portal.portal_acknowledgements.acknowledge(
         path=event.getRelativeUrl(),
         user_name='seb')
    # Make sure that we have a new acknowledge document wich is a proxy of 
    # the event
    self.assertEqual(acknowledgement.getPortalType(), 'Acknowledgement')
    self.assertEqual(acknowledgement.getTextContent(), "A Nice Message")
    transaction.commit()

    # We should not have any acknowledgements, we just commited previous
    # transaction, this means that we look if the mechanism that looks at
    # activity tags is working or not
    event_acknowledgement_list = getEventAcknowlegementList()
    # We should not have any acknowledgements, tic is finished
    # the code should look directly for acnowledgement documents
    self.tic()
    event_acknowledgement_list = getEventAcknowlegementList()
    self.assertEqual(0, len(event_acknowledgement_list))

    # We should have one acknowledgement in the event module



def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAcknowledgementTool))
  return suite
