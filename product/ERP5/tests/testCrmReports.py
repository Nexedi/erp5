#############################################################################
#
# Copyright  2007 Nexedi SA Contributors. All Rights Reserved.
#              Thierry Brettnacher <tb@nexedi.com>
#              Daniel Feliubadalo <daniel@sip2000.com>
#              Jerome Perrin <jerome@nexedi.com>
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

"""Tests Standards ERP5 Crm Reports
"""
import unittest

import transaction
from DateTime import DateTime

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5ReportTestCase
from Products.ERP5Type.tests.utils import reindex
from AccessControl.SecurityManagement import newSecurityManager

class CrmTestCase(ERP5ReportTestCase):
  """Tests starts with a preference activated for self.my_organisation, logged in
  as a user with Assignee, Assignor and Author role.

  All documents created appart from this configuration will be deleted in
  teardown. So users of this test case are encouraged to create new documents
  rather than modifying default documents. 
  """
  
  username = 'username'

  
  def _doWorkflowAction(self, ob, action,**kw):
    self.portal.portal_workflow.doActionFor(ob, action, 
                                            comment = 'for unit test',**kw)
                           
  @reindex  
  def _makeOneTicket(self, portal_type='Campaign', 
                     start_date=None,
                     stop_date=None,
                     simulation_state='draft', **kw):
    """Creates an ticket, and edit it with kw.
    
    The default settings is for self.section.
    You can pass a list of mapping as lines, then lines will be created
    using this information.
    """
    kw.setdefault('start_date', start_date)
    kw.setdefault('stop_date', stop_date)
    kw.setdefault('resource', 'service_module/1')
    tk=None
    if portal_type == ('Campaign'):
      tk = self.campaign_module.newContent(portal_type=portal_type,**kw)
    elif portal_type == ('Meeting'):
      tk = self.meeting_module.newContent(portal_type=portal_type,**kw)
    elif portal_type == ('Sale Opportunity'):
      tk = self.sale_opportunity_module.newContent(portal_type=portal_type,**kw)
    elif portal_type == ('Support Request'):
      tk = self.support_request_module.newContent(portal_type=portal_type,**kw)

    # not all states are implemented here for now.
    if portal_type == 'Sale Opportunity':
      # Sale Opportunity have a different workflow.
      if simulation_state in ('contacted', 'offered',):
        tk.validate()
      if simulation_state == 'offered':
        tk.offer()
    else:
      if simulation_state == 'validated':
        tk.validate()
    
    # sanity check
    self.assertEquals(simulation_state, tk.getSimulationState())
    return tk

  def _makeOneEvent(self, portal_type='Fax Message', 
                     start_date=DateTime(),
                     simulation_state='draft', 
                     follow_up_ticket_title = "",
                     follow_up_ticket_type = "Campaign",
                     **kw):
    """Creates an event, and edit it with kw.
    
    The default settings is for self.section.
    You can pass a list of mapping as lines, then lines will be created
    using this information.
    """
    kw.setdefault('start_date', start_date)
    kw.setdefault('resource', 'service_module/2')
    ev = self.event_module.newContent(portal_type=portal_type,**kw)

    if simulation_state == 'assigned':
      ticket=self.portal.restrictedTraverse(ev.getFollowUp())
      self._doWorkflowAction(ev,'assign_action',
                         follow_up_ticket_type = ticket.getPortalType(),
                         follow_up_ticket_title = ticket.getTitle())
    elif simulation_state == 'planned':
      ev.plan()
    elif simulation_state == 'posted':
      ev.start()
    elif simulation_state == 'delivered':
      ev.start()
      ev.deliver()
    elif simulation_state == 'new':
      ev.receive()
    elif simulation_state == 'acknowledged':
      ticket=self.portal.restrictedTraverse(ev.getFollowUp())
      self._doWorkflowAction(ev,'assign_action',
                         follow_up_ticket_type = ticket.getPortalType(),
                         follow_up_ticket_title = ticket.getTitle())
      self._doWorkflowAction(ev, 'acknowledge_action')
    elif simulation_state == 'cancelled':
      ev.receive()
      ev.cancel()
    elif simulation_state == 'deleted':
      ev.delete()
    elif simulation_state == 'expired':
      ev.receive()
      ev.expire()
    elif simulation_state == 'responded':
      ev.receive()
      ev.respond()
    elif simulation_state == 'started':
      ev.start()
    elif simulation_state == 'ordered':
      ev.plan()
      ev.order()
    # sanity check
    self.assertEquals(simulation_state, ev.getSimulationState())
    return ev

  def login(self):
    """login with Manager roles."""
    uf = self.getPortal().acl_users
    uf._doAddUser('manager', 'manager', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('manager').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    """Setup the fixture.
    """
    self.event_module = self.portal.event_module
    self.campaign_module = self.portal.campaign_module
    self.meeting_module = self.portal.meeting_module
    self.sale_opportunity_module = self.portal.sale_opportunity_module
    self.support_request_module = self.portal.support_request_module
    self.organisation_module = self.portal.organisation_module
    self.person_module = self.portal.person_module
    self.portal_categories = self.portal.portal_categories
 
    # create group category
    if not self.portal_categories['group'].has_key('demo_group'): 
      group=self.portal_categories.group
      subgroup = group.newContent(portal_type='Category',
                                title='demo_group',
                                reference='demo_group',
                                id='demo_group')
    # create users and organisations
    if not self.person_module.has_key('Person_1'): 
      user = self.portal.person_module.newContent(
                              portal_type='Person',
                              reference='Person_1',
                              title='Person_1',
                              id='Person_1')
    if not self.person_module.has_key('Person_2'): 
      user = self.portal.person_module.newContent(
                              portal_type='Person',
                              reference='Person_2',
                              title='Person_2',
                              id='Person_2')
    if not self.person_module.has_key('Person_3'): 
      user = self.portal.person_module.newContent(
                              portal_type='Person',
                              reference='Person_3',
                              title='Person_3',
                              id='Person_3')
    if not self.organisation_module.has_key('Organisation_1'): 
      org = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              reference='Organisation_1',
                              title='Organisation_1',
                              id='Organisation_1')
    if not self.organisation_module.has_key('Organisation_2'): 
      org = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              reference='Organisation_2',
                              title='Organisation_2',
                              id='Organisation_2')
    if not self.organisation_module.has_key('My_organisation'): 
      org = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              reference='My_organisation',
                              title='My_organisation',
                              group_value=self.portal_categories['group'].demo_group,
                              id='My_organisation')

    # make sure documents are validated
    for module in (self.organisation_module,
                   self.person_module):
      for doc in module.objectValues():
        doc.validate()

    # and all this available to catalog
    transaction.commit()
    self.tic()


  def beforeTearDown(self):
    """Remove all documents.
    """
    transaction.abort()
    for module in (self.campaign_module,
                   self.meeting_module,
                   self.sale_opportunity_module,
                   self.support_request_module,
                   self.organisation_module,
                   self.person_module,
                   self.event_module):
      module.manage_delObjects(list(module.objectIds()))
    self.portal_categories['group'].manage_delObjects((['demo_group',]))
    transaction.commit()
    self.tic()

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_base', 'erp5_crm', )


class TestCrmReports(CrmTestCase):
  """Test Crm reports
  
  Test basic cases of gathering data to render reports, the purpose of those
  tests is to exercise basic reporting features to make sure no regression
  happen. Input data used for tests usually contain edge cases, for example:
    * movements at the boundaries of the period.
    * movements with other simulation states.
    * movements with node in the section_category we want to exclude (Persons).
    * movements with source & destination for other sections.
  """
  def getTitle(self):
    return "Crm Reports"

  def testCampaignStatus(self):
    # Campaign Status report.
    
    # First campaign
    first = self._makeOneTicket(
              portal_type='Campaign',
              title='First One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value = self.person_module.Person_1,
              source_value = self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2),
              stop_date=DateTime(2007, 11, 30))
    # Second campaign
    second = self._makeOneTicket(
              portal_type='Campaign',
              title='Second One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))

    # creating events of first campaign
    eventOut1=self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 1 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=first.getRelativeUrl())              
    eventOut2=self._makeOneEvent(
              portal_type='Letter',
              title='Out 2 of First',
              simulation_state='planned',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              follow_up=first.getRelativeUrl())
    eventOut3=self._makeOneEvent(
              portal_type='Phone Call',
              title='Out 3 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=first.getRelativeUrl())
    eventIn1=self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Out 1 of First',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              causality=eventOut1.getRelativeUrl())
    # creating one free event for test
    eventOut1=self._makeOneEvent(
              portal_type='Fax Message',
              title='Free 1',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 2, 1, 1))
    # creating events of second campaign
    eventOut1=self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 1 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=second.getRelativeUrl())              
    eventOut2=self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 2 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2, 2, 1),
              follow_up=second.getRelativeUrl())              
    eventInt1=self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Out 1 of Second',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              #create a follow-up and causality ralationship to test that
              #only count one time by follow-up
              causality=eventOut1.getRelativeUrl(),
              follow_up=second.getRelativeUrl())              
              
    transaction.commit()
    self.tic()
    request_form = self.portal.REQUEST.other
    request_form['from_date'] = DateTime(2007, 1, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['validation_state'] = ['validated',]
    
    report_section_list = self.getReportSectionList(
                               self.portal.campaign_module,
                               'CampaignModule_viewCampaignStatusReport')
    self.assertEquals(1, len(report_section_list))
        
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 2 campaigns
    self.assertEquals(2, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['title', 'ticket_type', 'destination_section', 'destination_decision',
         'source', 'start_date', 'stop_date','validation_state','outgoing',
         'incoming','progression','efficiency'])
    
    # First campaign
    self.checkLineProperties(data_line_list[0],
                   title='First One',
                   ticket_type = first.getResourceTranslatedTitle(),
                   stop_date = DateTime(2007, 11, 30),
                   start_date = DateTime(2007, 2, 2),
                   destination_section = first.getDestinationSectionTitle(),
                   destination_decision = self.person_module.Person_1.getTitle(),
                   source = self.person_module.Person_2.getTitle(),
                   validation_state = 'Open',
                   outgoing = 3,
                   incoming = 1,
                   progression = 66.00/100,
                   efficiency = 33.00/100)    
    # Second campaign
    self.checkLineProperties(data_line_list[1],
                   title='Second One',
                   ticket_type = second.getResourceTranslatedTitle(),
                   stop_date = DateTime(2007, 12, 31),
                   start_date = DateTime(2007, 1, 2),
                   destination_section = second.getDestinationSectionTitle(),
                   destination_decision = second.getDestinationDecisionTitle(),
                   source = second.getSourceTitle(),
                   validation_state = 'Open',
                   outgoing = 2,
                   incoming = 1,
                   progression = 100.00/100,
                   efficiency = 50.00/100)
                  
  def testCampaignDetailedReport(self):
    # Campaign Detailed report.
    
    # First campaign
    first = self._makeOneTicket(
              portal_type='Campaign',
              title='First One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value = self.person_module.Person_1,
              source_value = self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2),
              stop_date=DateTime(2007, 11, 30))
    # Second campaign
    second = self._makeOneTicket(
              portal_type='Campaign',
              title='Second One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))

    # creating events of first campaign
    first_event_out1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 1 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=first.getRelativeUrl())              
    first_event_out2 = self._makeOneEvent(
              portal_type='Letter',
              title='Out 2 of First',
              simulation_state='planned',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              follow_up=first.getRelativeUrl())
    first_event_out3 = self._makeOneEvent(
              portal_type='Phone Call',
              title='Out 3 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=first.getRelativeUrl())
    first_event_inc1 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Out 1 of First',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              causality=first_event_out1.getRelativeUrl())
    # creating one free event for test
    free_event_out1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Free 1',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 2, 1, 1))
    # creating events of second campaign
    second_event_out1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 1 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=second.getRelativeUrl())              
    second_event_out2 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 2 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2, 2, 1),
              follow_up=second.getRelativeUrl())              
    second_event_inc1 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Out 1 of Second',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              #create a follow-up and causality ralationship to test that
              #only count one time by follow-up
              causality=second_event_out1.getRelativeUrl(),
              follow_up=second.getRelativeUrl())              
              
    transaction.commit()
    self.tic()
    # set request variables and render
    request_form = self.portal.REQUEST.other
    request_form['from_date'] = DateTime(2007, 1, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['validation_state'] = ['validated',]
    
    report_section_list = self.getReportSectionList(
                               self.portal.campaign_module,
                               'CampaignModule_viewCampaignDetailedReport')
    self.assertEquals(2, len(report_section_list))
        
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 7 events
    self.assertEquals(7, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['campaign', 'direction', 'title', 'type','destination_title_list',
         'source', 'start_date','stop_date','validation_state'])
    for i in range(len(data_line_list)):
      if i==0:
        ticket=first
        event=first_event_out1
        direction='Outgoing'
        campaign=ticket.getTitle()
      elif i==1:
        ticket=first
        event=first_event_inc1
        direction='Incoming'
        campaign=''
      elif i==2:
        ticket=first
        event=first_event_out2
        direction='Outgoing'
        campaign=ticket.getTitle()
      elif i==3:
        ticket=first
        event=first_event_out3
        direction='Outgoing'
        campaign=ticket.getTitle()
      elif i==4:
        ticket=second
        event=second_event_out1
        direction='Outgoing'
        campaign=ticket.getTitle()
      elif i==5:
        ticket=second
        event=second_event_out2
        direction='Outgoing'
        campaign=ticket.getTitle()
      elif i==6:
        ticket=second
        event=second_event_inc1
        direction='Incoming'
        campaign=ticket.getTitle()
      self.checkLineProperties(data_line_list[i],
                   campaign = campaign,
                   direction = direction,
                   type = event.getTranslatedPortalType(),
                   destination_title_list = event.getDestinationTitleList(),
                   title = event.getTitle(),
                   stop_date = event.getStopDate(),
                   start_date = event.getStartDate(),
                   source = event.getSourceTitle(),
                   validation_state = event.getTranslatedSimulationStateTitle())

  def testMeetingStatus(self):
    # Meeting Status report.
    
    # First Meeting
    first = self._makeOneTicket(
              portal_type='Meeting',
              title='First One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value = self.person_module.Person_1,
              source_value = self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2),
              stop_date=DateTime(2007, 11, 30))
    # Second Meeting
    second = self._makeOneTicket(
              portal_type='Meeting',
              title='Second One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))

    # creating events of first meeting
    eventOut1=self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 1 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=first.getRelativeUrl())              
    eventOut2=self._makeOneEvent(
              portal_type='Letter',
              title='Out 2 of First',
              simulation_state='planned',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              follow_up=first.getRelativeUrl())
    eventOut3=self._makeOneEvent(
              portal_type='Phone Call',
              title='Out 3 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=first.getRelativeUrl())
    eventIn1=self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Out 1 of First',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              causality=eventOut1.getRelativeUrl())
    # creating one free event for test
    eventOut1=self._makeOneEvent(
              portal_type='Fax Message',
              title='Free 1',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 2, 1, 1))
    # creating events of second meeting
    eventOut1=self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 1 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=second.getRelativeUrl())              
    eventOut2=self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 2 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2, 2, 1),
              follow_up=second.getRelativeUrl())              
    eventInt1=self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Out 1 of Second',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              #create a follow-up and causality ralationship to test that
              #only count one time by follow-up
              causality=eventOut1.getRelativeUrl(),
              follow_up=second.getRelativeUrl())              
              
    transaction.commit()
    self.tic()
    # set request variables and render
    request_form = self.portal.REQUEST.other
    request_form['from_date'] = DateTime(2007, 1, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['validation_state'] = ['validated',]
    
    report_section_list = self.getReportSectionList(
                               self.portal.meeting_module,
                               'MeetingModule_viewMeetingStatusReport')
    self.assertEquals(1, len(report_section_list))
        
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 2 meetings
    self.assertEquals(2, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['title', 'ticket_type', 'destination_section', 'destination_decision',
         'destination_title','source', 'start_date', 'stop_date',
         'validation_state','outgoing','incoming'])
 
    # First meeting
    self.checkLineProperties(data_line_list[0],
                   title='First One',
                   ticket_type = first.getResourceTranslatedTitle(),
                   stop_date = DateTime(2007, 11, 30),
                   start_date = DateTime(2007, 2, 2),
                   destination_section = first.getDestinationSectionTitle(),
                   destination_decision = self.person_module.Person_1.getTitle(),
                   destination_title = first.getDestinationTitle(),
                   source = self.person_module.Person_2.getTitle(),
                   validation_state = 'Open',
                   outgoing = 3,
                   incoming = 1)
    # Second meeting
    self.checkLineProperties(data_line_list[1],
                   title='Second One',
                   ticket_type = second.getResourceTranslatedTitle(),
                   stop_date = DateTime(2007, 12, 31),
                   start_date = DateTime(2007, 1, 2),
                   destination_section = second.getDestinationSectionTitle(),
                   destination_decision = second.getDestinationDecisionTitle(),
                   destination_title = second.getDestinationTitle(),
                   source = second.getSourceTitle(),
                   validation_state = 'Open',
                   outgoing = 2,
                   incoming = 1)
                  
  def testMeetingDetailedReport(self):
    # Meeting Detailed report.
    
    # First Meeting
    first = self._makeOneTicket(
              portal_type='Meeting',
              title='First One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value = self.person_module.Person_1,
              source_value = self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2),
              stop_date=DateTime(2007, 11, 30))
    # Second Meeting
    second = self._makeOneTicket(
              portal_type='Meeting',
              title='Second One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))

    # creating events of first Meeting
    first_event_out1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 1 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=first.getRelativeUrl())              
    first_event_out2 = self._makeOneEvent(
              portal_type='Letter',
              title='Out 2 of First',
              simulation_state='planned',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              follow_up=first.getRelativeUrl())
    first_event_out3 = self._makeOneEvent(
              portal_type='Phone Call',
              title='Out 3 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=first.getRelativeUrl())
    first_event_inc1 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Out 1 of First',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              causality=first_event_out1.getRelativeUrl())
    # creating one free event for test
    free_event_out1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Free 1',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 2, 1, 1))
    # creating events of second Meeting
    second_event_out1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 1 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=second.getRelativeUrl())              
    second_event_out2 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 2 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2, 2, 1),
              follow_up=second.getRelativeUrl())              
    second_event_inc1 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Out 1 of Second',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              #create a follow-up and causality ralationship to test that
              #only count one time by follow-up
              causality=second_event_out1.getRelativeUrl(),
              follow_up=second.getRelativeUrl())              
              
    transaction.commit()
    self.tic()
    # set request variables and render
    request_form = self.portal.REQUEST.other
    request_form['from_date'] = DateTime(2007, 1, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['validation_state'] = ['validated',]
    
    report_section_list = self.getReportSectionList(
                               self.portal.meeting_module,
                               'MeetingModule_viewMeetingDetailedReport')
    self.assertEquals(2, len(report_section_list))
        
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 7 events
    self.assertEquals(7, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['meeting', 'direction', 'title', 'type','destination_title_list',
         'source', 'start_date','stop_date','validation_state'])
    for i in range(len(data_line_list)):
      if i==0:
        ticket=first
        event=first_event_out1
        direction='Outgoing'
        meeting=ticket.getTitle()
      elif i==1:
        ticket=first
        event=first_event_inc1
        direction='Incoming'
        meeting=''
      elif i==2:
        ticket=first
        event=first_event_out2
        direction='Outgoing'
        meeting=ticket.getTitle()
      elif i==3:
        ticket=first
        event=first_event_out3
        direction='Outgoing'
        meeting=ticket.getTitle()
      elif i==4:
        ticket=second
        event=second_event_out1
        direction='Outgoing'
        meeting=ticket.getTitle()
      elif i==5:
        ticket=second
        event=second_event_out2
        direction='Outgoing'
        meeting=ticket.getTitle()
      elif i==6:
        ticket=second
        event=second_event_inc1
        direction='Incoming'
        meeting=ticket.getTitle()
      self.checkLineProperties(data_line_list[i],
                   meeting = meeting,
                   direction = direction,
                   type = event.getTranslatedPortalType(),
                   destination_title_list = event.getDestinationTitleList(),
                   title = event.getTitle(),
                   stop_date = event.getStopDate(),
                   start_date = event.getStartDate(),
                   source = event.getSourceTitle(),
                   validation_state = event.getTranslatedSimulationStateTitle())
                  
  def testSupportRequestStatus(self):
    # Support Request Status report.
    
    # First Support Request
    first = self._makeOneTicket(
              portal_type='Support Request',
              title='First One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value = self.person_module.Person_1,
              source_value = self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2),
              stop_date=DateTime(2007, 11, 30))
    # Second Support Request
    second = self._makeOneTicket(
              portal_type='Support Request',
              title='Second One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))

    # creating events of first Support Request
    first_event_inc1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Inc 1 of First',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=first.getRelativeUrl())              
    first_event_inc2 = self._makeOneEvent(
              portal_type='Letter',
              title='Inc 2 of First',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              follow_up=first.getRelativeUrl())
    first_event_inc3=self._makeOneEvent(
              portal_type='Phone Call',
              title='Inc 3 of First',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=first.getRelativeUrl())
    first_event_out1 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Inc 1 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              causality=first_event_inc1.getRelativeUrl())
    # creating one free event for test
    feEvInc1=self._makeOneEvent(
              portal_type='Fax Message',
              title='Free 1',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 2, 1, 1))
    # creating events of second Support Request
    second_event_inc1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Inc 1 of Second',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=second.getRelativeUrl())              
    second_event_inc2 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Inc 2 of Second',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2, 2, 1),
              follow_up=second.getRelativeUrl())              
    second_event_out1 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Inc 1 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              #create a follow-up and causality ralationship to test that
              #only count one time by follow-up
              causality=second_event_inc1.getRelativeUrl(),
              follow_up=second.getRelativeUrl())              
              
    transaction.commit()
    self.tic()
    # set request variables and render
    request_form = self.portal.REQUEST.other
    request_form['from_date'] = DateTime(2007, 1, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['validation_state'] = ['validated',]
    
    report_section_list = self.getReportSectionList(
                        self.portal.support_request_module,
                        'SupportRequestModule_viewSupportRequestStatusReport')
    self.assertEquals(1, len(report_section_list))
        
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 2 Support Request
    self.assertEquals(2, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['title', 'ticket_type', 'destination_section', 'destination_decision',
         'source', 'source_decision', 'start_date', 'stop_date',
         'validation_state','incoming','outgoing'])
 
    # First Support Request
    self.checkLineProperties(data_line_list[0],
                   title='First One',
                   ticket_type = first.getResourceTranslatedTitle(),
                   stop_date = DateTime(2007, 11, 30),
                   start_date = DateTime(2007, 2, 2),
                   destination_section = first.getDestinationSectionTitle(),
                   destination_decision = self.person_module.Person_1.getTitle(),
                   source_decision = first.getSourceDecisionTitle(),
                   source = self.person_module.Person_2.getTitle(),
                   validation_state = 'Open',
                   outgoing = 1,
                   incoming = 3)
    # Second Support Request
    self.checkLineProperties(data_line_list[1],
                   title='Second One',
                   ticket_type = second.getResourceTranslatedTitle(),
                   stop_date = DateTime(2007, 12, 31),
                   start_date = DateTime(2007, 1, 2),
                   destination_section = second.getDestinationSectionTitle(),
                   destination_decision = second.getDestinationDecisionTitle(),
                   source_decision = second.getSourceDecisionTitle(),
                   source = second.getSourceTitle(),
                   validation_state = 'Open',
                   outgoing = 1,
                   incoming = 2)
                                    
  def testSupportRequestDetailedReport(self):
    # Support Request Detailed report.
    
    # First Support Request
    first = self._makeOneTicket(
              portal_type='Support Request',
              title='First One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value = self.person_module.Person_1,
              source_value = self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2),
              stop_date=DateTime(2007, 11, 30))
    # Second Support Request
    second = self._makeOneTicket(
              portal_type='Support Request',
              title='Second One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))

    # creating events of first Support Request
    first_event_inc1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Inc 1 of First',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=first.getRelativeUrl())              
    first_event_inc2 = self._makeOneEvent(
              portal_type='Letter',
              title='Inc 2 of First',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              follow_up=first.getRelativeUrl())
    first_event_inc3=self._makeOneEvent(
              portal_type='Phone Call',
              title='Inc 3 of First',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=first.getRelativeUrl())
    first_event_out1 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Inc 1 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              causality=first_event_inc1.getRelativeUrl())
    # creating one free event for test
    feEvInc1=self._makeOneEvent(
              portal_type='Fax Message',
              title='Free 1',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 2, 1, 1))
    # creating events of second Support Request
    second_event_inc1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Inc 1 of Second',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=second.getRelativeUrl())              
    second_event_inc2 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Inc 2 of Second',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2, 2, 1),
              follow_up=second.getRelativeUrl())              
    second_event_out1 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Inc 1 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              #create a follow-up and causality ralationship to test that
              #only count one time by follow-up
              causality=second_event_inc1.getRelativeUrl(),
              follow_up=second.getRelativeUrl())              
              
    transaction.commit()
    self.tic()
    # set request variables and render
    request_form = self.portal.REQUEST.other
    request_form['from_date'] = DateTime(2007, 1, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['validation_state'] = ['validated',]
    
    report_section_list = self.getReportSectionList(
                      self.portal.support_request_module,
                      'SupportRequestModule_viewSupportRequestDetailedReport')
    self.assertEquals(2, len(report_section_list))
        
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 7 events
    self.assertEquals(7, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['support_request', 'direction', 'title', 'type','destination_title_list',
         'source', 'start_date','stop_date','validation_state'])
    for i in range(len(data_line_list)):
      if i==0:
        ticket=first
        event=first_event_inc1
        direction='Incoming'
        support_request=ticket.getTitle()
      elif i==1:
        ticket=first
        event=first_event_out1
        direction='Outgoing'
        support_request=''
      elif i==2:
        ticket=first
        event=first_event_inc2
        direction='Incoming'
        support_request=ticket.getTitle()
      elif i==3:
        ticket=first
        event=first_event_inc3
        direction='Incoming'
        support_request=ticket.getTitle()
      elif i==4:
        ticket=second
        event=second_event_inc1
        direction='Incoming'
        support_request=ticket.getTitle()
      elif i==5:
        ticket=second
        event=second_event_inc2
        direction='Incoming'
        support_request=ticket.getTitle()
      elif i==6:
        ticket=second
        event=second_event_out1
        direction='Outgoing'
        support_request=ticket.getTitle()
      self.checkLineProperties(data_line_list[i],
                   support_request = support_request,
                   direction = direction,
                   type = event.getTranslatedPortalType(),
                   destination_title_list = event.getDestinationTitleList(),
                   title = event.getTitle(),
                   stop_date = event.getStopDate(),
                   start_date = event.getStartDate(),
                   source = event.getSourceTitle(),
                   validation_state = event.getTranslatedSimulationStateTitle())
                  
  def testSaleOpportunityStatus(self):
    # Sale Opportunity Status report.
    
    # First Sale Opportunity
    first = self._makeOneTicket(
              portal_type='Sale Opportunity',
              title='First One',
              simulation_state='contacted',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value = self.person_module.Person_1,
              source_value = self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2),
              stop_date=DateTime(2007, 11, 30))
    # Second Sale Opportunity
    second = self._makeOneTicket(
              portal_type='Sale Opportunity',
              title='Second One',
              simulation_state='offered',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))

    # creating events of first Sale Opportunity
    eventOut1=self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 1 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=first.getRelativeUrl())              
    eventOut2=self._makeOneEvent(
              portal_type='Letter',
              title='Out 2 of First',
              simulation_state='planned',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              follow_up=first.getRelativeUrl())
    eventOut3=self._makeOneEvent(
              portal_type='Phone Call',
              title='Out 3 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=first.getRelativeUrl())
    eventIn1=self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Out 1 of First',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              causality=eventOut1.getRelativeUrl())
    # creating one free event for test
    eventOut1=self._makeOneEvent(
              portal_type='Fax Message',
              title='Free 1',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 2, 1, 1))
    # creating events of second Sale Opportunity
    eventOut1=self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 1 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=second.getRelativeUrl())              
    eventOut2=self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 2 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2, 2, 1),
              follow_up=second.getRelativeUrl())              
    eventInt1=self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Out 1 of Second',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              #create a follow-up and causality ralationship to test that
              #only count one time by follow-up
              causality=eventOut1.getRelativeUrl(),
              follow_up=second.getRelativeUrl())              
              
    transaction.commit()
    self.tic()
    # set request variables and render
    request_form = self.portal.REQUEST.other
    request_form['from_date'] = DateTime(2007, 1, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['sale_opportunity_state'] = ['contacted','offered']
    
    report_section_list = self.getReportSectionList(
                      self.portal.sale_opportunity_module,
                      'SaleOpportunityModule_viewSaleOpportunityStatusReport')
    self.assertEquals(1, len(report_section_list))
        
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 2 Sale Opportunity
    self.assertEquals(2, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['title', 'ticket_type', 'destination_section', 'destination_decision',
         'source','source_decision','start_date', 'stop_date',
         'validation_state','outgoing','incoming'])
 
    # First Sale Opportunity
    self.checkLineProperties(data_line_list[0],
                   title='First One',
                   ticket_type = first.getResourceTranslatedTitle(),
                   stop_date = DateTime(2007, 11, 30),
                   start_date = DateTime(2007, 2, 2),
                   destination_section = first.getDestinationSectionTitle(),
                   destination_decision = self.person_module.Person_1.getTitle(),
                   source_decision = first.getSourceDecisionTitle(),
                   source = self.person_module.Person_2.getTitle(),
                   validation_state = 'Prospect Contacted',
                   outgoing = 3,
                   incoming = 1)
    # Second Sale Opportunity
    self.checkLineProperties(data_line_list[1],
                   title='Second One',
                   ticket_type = second.getResourceTranslatedTitle(),
                   stop_date = DateTime(2007, 12, 31),
                   start_date = DateTime(2007, 1, 2),
                   destination_section = second.getDestinationSectionTitle(),
                   destination_decision = second.getDestinationDecisionTitle(),
                   source_decision = second.getSourceDecisionTitle(),
                   source = second.getSourceTitle(),
                   validation_state = 'Offered',
                   outgoing = 2,
                   incoming = 1)
                  
  def testSaleOpportunityDetailedReport(self):
    # Sale Opportunity Detailed report.
    
    # First Sale Opportunity
    first = self._makeOneTicket(
              portal_type='Sale Opportunity',
              title='First One',
              simulation_state='contacted',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_1,
              destination_decision_value = self.person_module.Person_1,
              source_value = self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2),
              stop_date=DateTime(2007, 11, 30))
    # Second Sale Opportunity
    second = self._makeOneTicket(
              portal_type='Sale Opportunity',
              title='Second One',
              simulation_state='offered',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))

    # creating events of Sale Opportunity
    first_event_out1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 1 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=first.getRelativeUrl())              
    first_event_out2 = self._makeOneEvent(
              portal_type='Letter',
              title='Out 2 of First',
              simulation_state='planned',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              follow_up=first.getRelativeUrl())
    first_event_out3 = self._makeOneEvent(
              portal_type='Phone Call',
              title='Out 3 of First',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=first.getRelativeUrl())
    first_event_inc1 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Out 1 of First',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              causality=first_event_out1.getRelativeUrl())
    # creating one free event for test
    free_event_out1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Free 1',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 2, 1, 1))
    # creating events of second Sale Opportunity
    second_event_out1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 1 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=second.getRelativeUrl())              
    second_event_out2 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Out 2 of Second',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 2, 2, 1),
              follow_up=second.getRelativeUrl())              
    second_event_inc1 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Response to Out 1 of Second',
              simulation_state='new',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              #create a follow-up and causality ralationship to test that
              #only count one time by follow-up
              causality=second_event_out1.getRelativeUrl(),
              follow_up=second.getRelativeUrl())              
              
    transaction.commit()
    self.tic()
    # set request variables and render
    request_form = self.portal.REQUEST.other
    request_form['from_date'] = DateTime(2007, 1, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['sale_opportunity_state'] = ['contacted','offered']
    
    report_section_list = self.getReportSectionList(
                     self.portal.sale_opportunity_module,
                    'SaleOpportunityModule_viewSaleOpportunityDetailedReport')
    self.assertEquals(2, len(report_section_list))
        
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 7 events
    self.assertEquals(7, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['sale_opportunity', 'direction', 'title', 'type','destination_title_list',
         'source', 'start_date','stop_date','validation_state'])
    for i in range(len(data_line_list)):
      if i==0:
        ticket=first
        event=first_event_out1
        direction='Outgoing'
        sale_opportunity=ticket.getTitle()
      elif i==1:
        ticket=first
        event=first_event_inc1
        direction='Incoming'
        sale_opportunity=''
      elif i==2:
        ticket=first
        event=first_event_out2
        direction='Outgoing'
        sale_opportunity=ticket.getTitle()
      elif i==3:
        ticket=first
        event=first_event_out3
        direction='Outgoing'
        sale_opportunity=ticket.getTitle()
      elif i==4:
        ticket=second
        event=second_event_out1
        direction='Outgoing'
        sale_opportunity=ticket.getTitle()
      elif i==5:
        ticket=second
        event=second_event_out2
        direction='Outgoing'
        sale_opportunity=ticket.getTitle()
      elif i==6:
        ticket=second
        event=second_event_inc1
        direction='Incoming'
        sale_opportunity=ticket.getTitle()
      self.checkLineProperties(data_line_list[i],
                   sale_opportunity = sale_opportunity,
                   direction = direction,
                   type = event.getTranslatedPortalType(),
                   destination_title_list = event.getDestinationTitleList(),
                   title = event.getTitle(),
                   stop_date = event.getStopDate(),
                   start_date = event.getStartDate(),
                   source = event.getSourceTitle(),
                   validation_state = event.getTranslatedSimulationStateTitle())

  def testEventActivity(self):
    # Event Activity report.
    
    # creating one ticket of every type
    sale_opportunity = self._makeOneTicket(
              portal_type='Sale Opportunity',
              title='Sale Opportunity One',
              simulation_state='contacted',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2007, 2, 2),
              stop_date=DateTime(2007, 11, 30))
    campaign = self._makeOneTicket(
              portal_type='Campaign',
              title='Campaign One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))
    meeting = self._makeOneTicket(
              portal_type='Meeting',
              title='Meeting One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))
    support_request = self._makeOneTicket(
              portal_type='Support Request',
              title='Support Request One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))

    # creating events in every incoming-outgoing state related with tickets
    event1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Event 1',
              simulation_state='acknowledged',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=sale_opportunity.getRelativeUrl())              
    event2 = self._makeOneEvent(
              portal_type='Letter',
              title='Event 2',
              simulation_state='assigned',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              follow_up=campaign.getRelativeUrl())
    event3 = self._makeOneEvent(
              portal_type='Phone Call',
              title='Event 3',
              simulation_state='cancelled',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=meeting.getRelativeUrl())
    event4 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Event 4',
              simulation_state='expired',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              follow_up=support_request.getRelativeUrl())
    event5 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Event 5',
              simulation_state='new',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=sale_opportunity.getRelativeUrl())
    event6 = self._makeOneEvent(
              portal_type='Letter',
              title='Event 6',
              simulation_state='responded',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=campaign.getRelativeUrl())
    event7 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Event 7',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=meeting.getRelativeUrl())
    event8 = self._makeOneEvent(
              portal_type='Phone Call',
              title='Event 8',
              simulation_state='planned',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=support_request.getRelativeUrl())
    event9 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Event 9',
              simulation_state='ordered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=sale_opportunity.getRelativeUrl())
    event10 = self._makeOneEvent(
              portal_type='Letter',
              title='Event 10',
              simulation_state='started',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=campaign.getRelativeUrl())
    # creating free event for unassigned
    free_event = self._makeOneEvent(
              portal_type='Fax Message',
              title='Free 1',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 2, 1, 1))
    free_event = self._makeOneEvent(
              portal_type='Fax Message',
              title='Free 2',
              simulation_state='new',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 2, 1, 1))
    # creating events in every non incoming-outgoing state related with tickets
    event = self._makeOneEvent(
              portal_type='Fax Message',
              title='Event deleted 1',
              simulation_state='draft',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=sale_opportunity.getRelativeUrl())              
    event = self._makeOneEvent(
              portal_type='Letter',
              title='Event deleted 2',
              simulation_state='deleted',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              follow_up=campaign.getRelativeUrl())
    # creating events in incoming-outgoing state related with tickets
    # by causality with one related event
    event = self._makeOneEvent(
              portal_type='Fax Message',
              title='Event causality 1',
              simulation_state='new',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              causality=event9.getRelativeUrl())              
    event = self._makeOneEvent(
              portal_type='Letter',
              title='Event causality 2',
              simulation_state='new',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              causality=event10.getRelativeUrl())
    # creating events related with same ticket by follow-up and causality
    # Only must count one time (follow-up)
    event = self._makeOneEvent(
              portal_type='Fax Message',
              title='Event both 1',
              simulation_state='new',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              causality=event5.getRelativeUrl(),
              follow_up=sale_opportunity.getRelativeUrl())
    event = self._makeOneEvent(
              portal_type='Letter',
              title='Event both 2',
              simulation_state='responded',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              causality=event6.getRelativeUrl(),
              follow_up=campaign.getRelativeUrl()) 
              
    transaction.commit()
    self.tic()
    # set request variables and render
    request_form = self.portal.REQUEST.other
    request_form['from_date'] = DateTime(2007, 1, 1)
    
    report_section_list = self.getReportSectionList(
                                    self.portal.event_module,
                                    'EventModule_viewEventActivityReport')
    #Obtain 2 listbox with outgoing and incoming events
    self.assertEquals(2, len(report_section_list))
    
    #Outgoing
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 6 states
    self.assertEquals(6, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['validation_state','Campaign', 'Meeting', 
         'SaleOpportunity','SupportRequest', 'unassigned','total'])
    for i in range(len(data_line_list)):
      if i==0:
        pvalidation_state = 'Acknowledged'
        pCampaign = 0
        pMeeting = 0
        pSaleOpportunity = 1
        pSupportRequest = 0
        punassigned = 0
        ptotal = 1
      elif i==1:
        pvalidation_state = 'Assigned'
        pCampaign = 1
        pMeeting = 0
        pSaleOpportunity = 0
        pSupportRequest = 0
        punassigned = 0
        ptotal = 1
      elif i==2:
        pvalidation_state = 'Cancelled'
        pCampaign = 0
        pMeeting = 1
        pSaleOpportunity = 0
        pSupportRequest = 0
        punassigned = 0
        ptotal = 1
      elif i==3:
        pvalidation_state = 'Expired'
        pCampaign = 0
        pMeeting = 0
        pSaleOpportunity = 0
        pSupportRequest = 1
        punassigned = 0
        ptotal = 1
      elif i==4:
        pvalidation_state = 'New'
        pCampaign = 1
        pMeeting = 0
        pSaleOpportunity = 3
        pSupportRequest = 0
        punassigned = 1
        ptotal = 5
      elif i==5:
        pvalidation_state = 'Responded'
        pCampaign = 2
        pMeeting = 0
        pSaleOpportunity = 0
        pSupportRequest = 0
        punassigned = 0
        ptotal = 2
      self.checkLineProperties(data_line_list[i],
                         validation_state = pvalidation_state,
                         Campaign = pCampaign,
                         Meeting = pMeeting,
                         SaleOpportunity = pSaleOpportunity,
                         SupportRequest = pSupportRequest,
                         unassigned = punassigned,
                         total = ptotal)
    # Stat Line
    stat_line = line_list[-1]
    self.failUnless(stat_line.isStatLine())
    self.assertEquals('Total', stat_line.getColumnProperty('validation_state'))
    self.assertEquals(4, stat_line.getColumnProperty('Campaign'))
    self.assertEquals(1, stat_line.getColumnProperty('Meeting'))
    self.assertEquals(4, stat_line.getColumnProperty('SaleOpportunity'))
    self.assertEquals(1, stat_line.getColumnProperty('SupportRequest'))
    self.assertEquals(1, stat_line.getColumnProperty('unassigned'))
    self.assertEquals(11, stat_line.getColumnProperty('total'))

    #Incoming
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 4 states
    self.assertEquals(4, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['validation_state','Campaign', 'Meeting', 
         'SaleOpportunity','SupportRequest', 'unassigned','total'])
    for i in range(len(data_line_list)):
      if i==0:
        pvalidation_state = 'Delivered'
        pCampaign = 0
        pMeeting = 1
        pSaleOpportunity = 0
        pSupportRequest = 0
        punassigned = 1
        ptotal = 2
      elif i==1:
        pvalidation_state = 'Outgoing'
        pCampaign = 0
        pMeeting = 0
        pSaleOpportunity = 0
        pSupportRequest = 1
        punassigned = 0
        ptotal = 1
      elif i==2:
        pvalidation_state = 'Pending'
        pCampaign = 0
        pMeeting = 0
        pSaleOpportunity = 1
        pSupportRequest = 0
        punassigned = 0
        ptotal = 1
      elif i==3:
        pvalidation_state = 'Posted'
        pCampaign = 1
        pMeeting = 0
        pSaleOpportunity = 0
        pSupportRequest = 0
        punassigned = 0
        ptotal = 1
      self.checkLineProperties(data_line_list[i],
                         validation_state = pvalidation_state,
                         Campaign = pCampaign,
                         Meeting = pMeeting,
                         SaleOpportunity = pSaleOpportunity,
                         SupportRequest = pSupportRequest,
                         unassigned = punassigned,
                         total = ptotal)
    # Stat Line
    stat_line = line_list[-1]
    self.failUnless(stat_line.isStatLine())
    self.assertEquals('Total', stat_line.getColumnProperty('validation_state'))
    self.assertEquals(1, stat_line.getColumnProperty('Campaign'))
    self.assertEquals(1, stat_line.getColumnProperty('Meeting'))
    self.assertEquals(1, stat_line.getColumnProperty('SaleOpportunity'))
    self.assertEquals(1, stat_line.getColumnProperty('SupportRequest'))
    self.assertEquals(1, stat_line.getColumnProperty('unassigned'))
    self.assertEquals(5, stat_line.getColumnProperty('total'))
                  
  def testEventDetailedReport(self):
    # Event Detailed Report report.
    
    # creating one ticket of every type
    sale_opportunity = self._makeOneTicket(
              portal_type='Sale Opportunity',
              title='Sale Opportunity One',
              simulation_state='contacted',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2007, 2, 2),
              stop_date=DateTime(2007, 11, 30))
    campaign = self._makeOneTicket(
              portal_type='Campaign',
              title='Campaign One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))
    meeting = self._makeOneTicket(
              portal_type='Meeting',
              title='Meeting One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_1,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))
    support_request = self._makeOneTicket(
              portal_type='Support Request',
              title='Support Request One',
              simulation_state='validated',
              source_section_value=self.organisation_module.My_organisation,
              destination_section_value=self.organisation_module.Organisation_2,
              start_date=DateTime(2007, 1, 2),
              stop_date=DateTime(2007, 12, 31))

    # creating events in every incoming-outgoing state related with tickets
    event1 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Event 1',
              simulation_state='acknowledged',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=sale_opportunity.getRelativeUrl())              
    event2 = self._makeOneEvent(
              portal_type='Letter',
              title='Event 2',
              simulation_state='assigned',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              follow_up=campaign.getRelativeUrl())
    event3 = self._makeOneEvent(
              portal_type='Phone Call',
              title='Event 3',
              simulation_state='cancelled',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=meeting.getRelativeUrl())
    event4 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Event 4',
              simulation_state='expired',
              destination_value=self.organisation_module.My_organisation,
              source_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 7, 1, 1),
              follow_up=support_request.getRelativeUrl())
    event5 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Event 5',
              simulation_state='new',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=sale_opportunity.getRelativeUrl())
    event6 = self._makeOneEvent(
              portal_type='Letter',
              title='Event 6',
              simulation_state='responded',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=campaign.getRelativeUrl())
    event7 = self._makeOneEvent(
              portal_type='Mail Message',
              title='Event 7',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=meeting.getRelativeUrl())
    event8 = self._makeOneEvent(
              portal_type='Phone Call',
              title='Event 8',
              simulation_state='planned',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=support_request.getRelativeUrl())
    event9 = self._makeOneEvent(
              portal_type='Fax Message',
              title='Event 9',
              simulation_state='ordered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=sale_opportunity.getRelativeUrl())
    event10 = self._makeOneEvent(
              portal_type='Letter',
              title='Event 10',
              simulation_state='started',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              follow_up=campaign.getRelativeUrl())
    # creating free event for unassigned
    free_event = self._makeOneEvent(
              portal_type='Fax Message',
              title='Free 1',
              simulation_state='delivered',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 2, 1, 1))
    free_event = self._makeOneEvent(
              portal_type='Fax Message',
              title='Free 2',
              simulation_state='new',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 2, 1, 1))
    # creating events in every non incoming-outgoing state related with tickets
    event = self._makeOneEvent(
              portal_type='Fax Message',
              title='Event deleted 1',
              simulation_state='draft',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              follow_up=sale_opportunity.getRelativeUrl())              
    event = self._makeOneEvent(
              portal_type='Letter',
              title='Event deleted 2',
              simulation_state='deleted',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              follow_up=campaign.getRelativeUrl())
    # creating events in incoming-outgoing state related with tickets
    # by causality with one related event
    event = self._makeOneEvent(
              portal_type='Fax Message',
              title='Event causality 1',
              simulation_state='new',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_1,
              start_date=DateTime(2007, 2, 2, 1, 1),
              causality=event9.getRelativeUrl())              
    event = self._makeOneEvent(
              portal_type='Letter',
              title='Event causality 2',
              simulation_state='new',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_2,
              start_date=DateTime(2007, 2, 1, 1, 1),
              causality=event10.getRelativeUrl())
    # creating events related with same ticket by follow-up and causality
    # Only must count one time (follow-up)
    event = self._makeOneEvent(
              portal_type='Fax Message',
              title='Event both 1',
              simulation_state='new',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              causality=event5.getRelativeUrl(),
              follow_up=sale_opportunity.getRelativeUrl())
    event = self._makeOneEvent(
              portal_type='Letter',
              title='Event both 2',
              simulation_state='responded',
              source_value=self.organisation_module.My_organisation,
              destination_value=self.person_module.Person_3,
              start_date=DateTime(2007, 2, 3, 1, 1),
              causality=event6.getRelativeUrl(),
              follow_up=campaign.getRelativeUrl()) 
              
    transaction.commit()
    self.tic()
    # set request variables and render
    request_form = self.portal.REQUEST.other
    request_form['from_date'] = DateTime(2007, 1, 1)
    
    report_section_list = self.getReportSectionList(
                                    self.portal.event_module,
                                    'EventModule_viewEventDetailedReport')
    #Obtain 1 listbox with outgoing and incoming events
    self.assertEquals(1, len(report_section_list))
    
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 5 lines
    self.assertEquals(5, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['ticket_title','ticket_type', 'resource', 
         'delivered', 'ordered', 'acknowledged', 'assigned', 
         'started', 'draft', 'planned', 'cancelled', 'new', 
         'expired', 'responded','total'])
    for i in range(len(data_line_list)):
      if i==0:
        pticket_title = 'Campaign One'
        pticket_type = 'Campaign'
        pdelivered = 0
        pordered = 0
        packnowledged = 0
        passigned = 1
        pstarted = 1
        pdraft = 0
        pplanned = 0
        pcancelled = 0
        pnew = 1
        pexpired = 0
        presponded = 2
        ptotal = 5
      elif i==1:
        pticket_title = 'Meeting One'
        pticket_type = 'Meeting'
        pdelivered = 1
        pordered = 0
        packnowledged = 0
        passigned = 0
        pstarted = 0
        pdraft = 0
        pplanned = 0
        pcancelled = 1
        pnew = 0
        pexpired = 0
        presponded = 0
        ptotal = 2
      elif i==2:
        pticket_title = 'Sale Opportunity One'
        pticket_type = 'Sale Opportunity'
        pdelivered = 0
        pordered = 1
        packnowledged = 1
        passigned = 0
        pstarted = 0
        pdraft = 1
        pplanned = 0
        pcancelled = 0
        pnew = 3
        pexpired = 0
        presponded = 0
        ptotal = 6
      elif i==3:
        pticket_title = 'Support Request One'
        pticket_type = 'Support Request'
        pdelivered = 0
        pordered = 0
        packnowledged = 0
        passigned = 0
        pstarted = 0
        pdraft = 0
        pplanned = 1
        pcancelled = 0
        pnew = 0
        pexpired = 1
        presponded = 0
        ptotal = 2
      elif i==4:
        pticket_title = ''
        pticket_type = 'Unassigned'
        pdelivered = 1
        pordered = 0
        packnowledged = 0
        passigned = 0
        pstarted = 0
        pdraft = 0
        pplanned = 0
        pcancelled = 0
        pnew = 1
        pexpired = 0
        presponded = 0
        ptotal = 2
      self.checkLineProperties(data_line_list[i],
                        ticket_title = pticket_title,
                        ticket_type = pticket_type,
                        delivered = pdelivered,
                        ordered = pordered,
                        acknowledged = packnowledged,
                        assigned = passigned,
                        started = pstarted,
                        draft = pdraft,
                        planned = pplanned,
                        cancelled = pcancelled,
                        new = pnew,
                        expired = pexpired,
                        responded = presponded,
                        total = ptotal)
    # Stat Line
    stat_line = line_list[-1]
    self.failUnless(stat_line.isStatLine())
    self.assertEquals('Total', stat_line.getColumnProperty('ticket_title'))
    self.assertEquals(2, stat_line.getColumnProperty('delivered'))
    self.assertEquals(1, stat_line.getColumnProperty('ordered'))
    self.assertEquals(1, stat_line.getColumnProperty('acknowledged'))
    self.assertEquals(1, stat_line.getColumnProperty('assigned'))
    self.assertEquals(1, stat_line.getColumnProperty('started'))
    self.assertEquals(1, stat_line.getColumnProperty('draft'))
    self.assertEquals(1, stat_line.getColumnProperty('planned'))
    self.assertEquals(1, stat_line.getColumnProperty('cancelled'))
    self.assertEquals(5, stat_line.getColumnProperty('new'))
    self.assertEquals(1, stat_line.getColumnProperty('expired'))
    self.assertEquals(2, stat_line.getColumnProperty('responded'))
    self.assertEquals(17, stat_line.getColumnProperty('total'))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCrmReports))
  return suite

