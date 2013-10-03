# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2007 Nexedi SARL and Contributors. All Rights Reserved.
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
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, Constraint
from Products.ERP5.Document.PDFTypeInformation import PDFTypeInformation
from Products.ERP5Type.Core.ActionInformation import CacheableAction

#line count in pdf form of procedure hosting request
#for sections: actions, concerned services and attachments
actionCount = 38

class EGovTypeInformation(PDFTypeInformation):
  # CMF Type Definition
  meta_type = 'ERP5 EGov Type Information'
  portal_type = 'EGov Type'
  isPortalContent = 1
  isRADContent = 1  

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    )

  # Various methods to override the default implementation
  # based on information provided on the "form hosting" application form
  # TBD


  def _getOpenActionTitleList(self):
    """
    Read all lines of actions in the PDF form and return the title
    for actions which correspond to the "open" transition
    """
    open_action_title_list = []
    for i in range(actionCount+1)[1:]:
      getOpenAction = getattr(self, "getActionOpening%s" % i, None)
      if callable(getOpenAction):
        getActionTitle = getattr(self, "getActionTitle%s" % i, None)
        if getOpenAction() and getActionTitle is not None and getActionTitle()!="":
          open_action_title_list.append(getActionTitle())
    return open_action_title_list



  def _getRequestActionTitleList(self):
    """
    Read all fields in the PDF form and return the title
    for all actions which correspond to the "request" transition
    """
    request_action_title_list = []
    for i in range(actionCount+1)[1:]:
      getRequestAction = getattr(self, "getActionRequest%s" % i, None)
      if callable(getRequestAction):
        getActionTitle = getattr(self, "getActionTitle%s" % i, None)
        if getRequestAction() and getActionTitle is not None and getActionTitle()!="":
          request_action_title_list.append(getActionTitle())
    return request_action_title_list


  def _getAllocateActionTitleList(self):
    """
    Read all fields in the PDF form and return the title
    for all actions which correspond to the "allocate" transition
    """
    allocated_action_title_list = []
    for i in range(actionCount+1)[1:]:
      getAllocatedAction = getattr(self, "getActionNotice%s" % i, None)
      if callable(getAllocatedAction):
        getActionTitle = getattr(self, "getActionTitle%s" % i, None)
        if getAllocatedAction() and getActionTitle is not None and getActionTitle()!="":
          allocated_action_title_list.append(getActionTitle())
    return allocated_action_title_list

  def _getSuspendActionTitleList(self):
    """
    Read all fields in the PDF form and return the title
    for all actions which correspond to the "suspend" transition
    """
    suspended_action_title_list = []
    for i in range(actionCount+1)[1:]:
      getSuspendedAction = getattr(self, "getActionSuspension%s" % i, None)
      if callable(getSuspendedAction):
        getActionTitle = getattr(self, "getActionTitle%s" % i, None)
        if getSuspendedAction() and getActionTitle is not None and getActionTitle()!="":
          suspended_action_title_list.append(getActionTitle())
    return suspended_action_title_list

  def _getApprouveActionTitleList(self):
    """
    Read all fields in the PDF form and return the title
    for all actions which correspond to the "approuve" transition
    """
    approuved_action_title_list = []
    for i in range(actionCount+1)[1:]:
      getApprouvedAction = getattr(self, "getActionApproval%s" % i, None)
      if callable(getApprouvedAction):
        getActionTitle = getattr(self, "getActionTitle%s" % i, None)
        if getApprouvedAction() and getActionTitle is not None and getActionTitle()!="":
          approuved_action_title_list.append(getActionTitle())
    return approuved_action_title_list

  def _getRefuseActionTitleList(self):
    """
    Read all fields in the PDF form and return the title
    for all actions which correspond to the "refuse" transition
    """
    refused_action_title_list = []
    for i in range(actionCount+1)[1:]:
      getRefusedAction = getattr(self, "getActionRejection%s" % i, None)
      if callable(getRefusedAction):
        getActionTitle = getattr(self, "getActionTitle%s" % i, None)
        if getRefusedAction() and getActionTitle is not None and getActionTitle()!="":
          refused_action_title_list.append(getActionTitle())
    return refused_action_title_list

  def getCacheableActionList(self):
    action_list = PDFTypeInformation.getCacheableActionList(self)
    if self.getPortalType() == "EGov Type":
      # Add "open" type actions (if any)
      for title in self._getOpenActionTitleList():
        action_list.append(
          CacheableAction(id='open_%s' % title.lower().strip().replace(' ','_'),
                          name=title,
                          description='Open the form for study',
                          category='workflow',
                          priority=10.1,
                          icon=None,
                          action='string:${object_url}/Base_viewWorkflowActionDialog?workflow_action=open_action',
                          condition="python:object.getValidationState() in ['assigned', 'suspended', 'accepted']",
                          ),
        )

      # Add "request" type actions
      for title in self._getRequestActionTitleList():
        action_list.append(
          CacheableAction(id='request_%s' % title.lower().strip().replace(' ','_'),
                          name=title,
                          description='Request another service to process the form',
                          category='workflow',
                          priority=10.2,
                          icon=None,
                          action='string:${object_url}/Base_viewWorkflowActionDialog?workflow_action=request_action',
                          condition="python:object.getValidationState() in ['opened', 'suspended']",
                          ),
        )
      # Add "allocate" type actions (if any)
      for title in self._getAllocateActionTitleList():
        action_list.append(
          CacheableAction(id='allocate_%s' % title.lower().strip().replace(' ','_'),
                          name=title,
                          description='Allocate the form',
                          category='workflow',
                          priority=10.3,
                          icon=None,
                          action='string:${object_url}/Base_viewWorkflowActionDialog?workflow_action=allocate_action',
                          condition="python:object.getValidationState() in ['requested', 'suspended']",
                          ),
        )

      # Add "suspend" type actions (if any)
      for title in self._getSuspendActionTitleList():
        action_list.append(
          CacheableAction(id='suspend_%s' % title.lower().strip().replace(' ','_'),
                          name=title,
                          description='Suspend the form',
                          category='workflow',
                          priority=10.4,
                          icon=None,
                          action='string:${object_url}/Base_viewWorkflowActionDialog?workflow_action=suspend_action',
                          condition="python:object.getValidationState() in ['opened', 'allocated']",
                          ),
        )

      # Add "approuve" type actions (if any)
      for title in self._getApprouveActionTitleList():
        action_list.append(
          CacheableAction(id='approuve_%s' % title.lower().strip().replace(' ','_'),
                          name=title,
                          description='Approuve the form',
                          category='workflow',
                          priority=10.4,
                          icon=None,
                          action='string:${object_url}/Base_viewWorkflowActionDialog?workflow_action=approve_action',
                          condition="python:object.getValidationState() in ['completed',]",
                          ),
        )
      # Add "refuse" type actions (if any)
      for title in self._getRefuseActionTitleList():
        action_list.append(
          CacheableAction(id='reject_%s' % title.lower().strip().replace(' ','_'),
                          name=title,
                          description='Reject the form',
                          category='workflow',
                          priority=10.5,
                          icon=None,
                          action='string:${object_url}/Base_viewWorkflowActionDialog?workflow_action=reject_action',
                          condition="python:object.getValidationState() in ['completed',]",
                          ),
        )

    return action_list
