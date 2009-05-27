##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ben Mayhew <maybewhen@gmx.net>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
##############################################################################
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir
from Products.ERP5.Document.Acknowledgement import Acknowledgement
from zLOG import LOG
from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import Query, NegatedQuery


class AcknowledgementTool(BaseTool):
  """
    Provide an entry point to track reception of events
    
    someone who can not view the ticket or the event
    must be able to acknowledge reception of email
    or of site message sent by CRM.

    This tools take into account that for some kind of document, 
    acknowledgements are not created in advance. For Site Message, 
    acknowledgements will be created every time the user confirm that he has
    read the information.

    In the case of internal emails, acknowledgements are created in advance.
  
    Use Case: who read the emails I sent ?
    Use Case: who said OK to Site Message ?
  """
  id = 'portal_acknowledgements'
  meta_type = 'ERP5 Acknowledgement Tool'
  portal_type = 'Acknowledgement Tool'   
  allowed_types = ('ERP5 Acknowledgement',)
  # Declarative Security
  security = ClassSecurityInfo()


  security.declarePublic('getUnreadAcknowledgementList')
  def countUnread(self, *args, **kw):
    """
      counts number of acknowledgements pending
    """
    return len(self.getUnreadAcknowledgementList(*args, **kw))

  security.declarePublic('getUnreadAcknowledgementList')
  def getUnreadAcknowledgementList(self, portal_type=None, user_name=None, 
                                   url_list=None):
    """
      returns acknowledgements pending
      in the form of
      - TempAcknowledgement (for Site Message)
      - Acknowledgement (internal email)
    """
    portal = self.getPortalObject()
    return_list = []
    if url_list is None:
      url_list = self.getUnreadDocumentUrlList(portal_type=portal_type, 
                                               user_name=user_name)
    for url in url_list:
      document = portal.restrictedTraverse(url)
      if not document.isAcknowledged(user_name=user_name):
        # If the document to acknowledge is a ticket, we should return
        # a temp acknowledgement
        if document.getPortalType() in portal.getPortalEventTypeList():
          module = portal.getDefaultModule('Acknowledgement')
          temp_acknowledgement = module.newContent(
                                       portal_type='Acknowledgement',
                                       temp_object=1,
                                       document_proxy=document.getRelativeUrl(),
                                       causality=document.getRelativeUrl())
          return_list.append(temp_acknowledgement)
        else:
          # If not an event, this means that we have directly the document
          # that we must acknowledge
          return_list.append(document)
    return return_list

  security.declarePublic('getUnreadDocumentUrlList')
  def getUnreadDocumentUrlList(self, portal_type=None, user_name=None, **kw):
    """
      returns document that needs to be acknowledged : 
      - Acknowledgement (internal email)
      - Site Message

      This method will mainly be used by getUnreadAcknowledgementList. Also,
      because url are used, the result will be easy to cache.
    """
    document_list = []
    if user_name is not None:
      portal = self.getPortalObject()
      now = DateTime()
      # First look at all event that define the current user as destination
      all_document_list = [x for x in \
         self.portal_catalog(portal_type = portal_type,
              simulation_state = self.getPortalTransitInventoryStateList(),
  #           start_date = {'query':now,'range':'max'},
  #           stop_date = {'query':now,'range':'min'},
              default_destination_reference=user_name)]
      # Now we can look directly at acknowledgement document not approved yet
      # so not in a final state
      final_state_list = self.getPortalCurrentInventoryStateList()
      query = NegatedQuery(Query(simulation_state=final_state_list))
      all_document_list.extend([x for x in \
         self.portal_catalog(portal_type = portal_type,
              query=query,
  #           start_date = {'query':now,'range':'max'},
  #           stop_date = {'query':now,'range':'min'},
              destination_reference=user_name)])
      for document in all_document_list:
        # We filter manually on dates until a good solution is found for
        # searching by dates on the catalog
        if (document.getStartDate() < now < (document.getStopDate()+1)):
          acknowledged = document.isAcknowledged(user_name=user_name)
          if not acknowledged:
            document_list.append(document.getRelativeUrl())
    else:
      raise ValueError('No user name given')
    return document_list

  security.declareProtected(Permissions.AccessContentsInformation,
                            'acknowledge')
  def acknowledge(self, uid=None, path=None, user_name=None, **kw):
    """
      Create an acknowledgement document for :
      - a ticket
      - an event
      - an acknowledgement
      
      This methods needs to check if there is already ongoing ackowledgement
      for the document of for this user. We will have to use activities with
      tag and probably a serialization.
    """
    document = None
    if uid is not None:
      document = self.portal_catalog.getObject(uid)
    elif path is not None:
      document = self.restrictedTraverse(path)
    else:
      raise ValueError("No path or uid given")
    if document is None:
      raise ValueError("Ticket does not exist or you don't have access to it")
    return document.acknowledge(user_name=user_name, **kw)
 

InitializeClass(AcknowledgementTool)
