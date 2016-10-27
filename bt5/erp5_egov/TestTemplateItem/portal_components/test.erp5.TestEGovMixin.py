##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
#                  Fabien Morin <fabien@nexedi.com>
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
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from AccessControl.SecurityManagement import getSecurityManager
from Products.ERP5Type.tests.utils import DummyMailHost
from Testing import ZopeTestCase
from Products.ERP5Type.tests.Sequence import Step, Sequence, SequenceList
from zLOG import LOG
import random
import email
from email.header import decode_header, make_header
from email.utils import parseaddr

class TestEGovMixin(SecurityTestCase):
  """Usefull methods for eGov Unit Tests."""
  
  # define all username corresponding to all roles used in eGov
  assignor_login = 'chef'
  assignee_login = 'agent'
  assignee_login_2 = 'agent_2'
  associate_login = 'agent_requested'

  organisation_1_login = 'societe_a'
  organisation_2_login = 'societe_b'

  all_username_list = ( assignor_login,
                        assignee_login,
                        assignee_login_2,
                        #associate_login,
                        organisation_1_login,
                        organisation_2_login)

  all_role_list = ( 'Manager',
                    'Assignor',
                    'Assignee',
                    'Author',
                    'Associate',
                    'Auditor',)

  #Permissions
  VIEW = 'View'
  ACCESS = 'Access contents information'
  ADD = 'Add portal content'
  MODIFY = 'Modify portal content'
  DELETE = 'Delete objects'


  # use modified method to render a more verbose output
  def play(self, context, sequence=None, sequence_number=0, quiet=0):
    if sequence is None:
      for idx, step in enumerate(self._step_list):
        step.play(context, sequence=self, quiet=quiet)
        # commit transaction after each step
        self.commit()
  Sequence.play = play

  def play(self, context, sequence=None, quiet=0):
    method_name = 'step' + self._method_name
    method = getattr(context,method_name)
    # We can in same cases replay many times the same step,
    # or not playing it at all
    nb_replay = random.randrange(0,self._max_replay+1)
    if self._required:
      if nb_replay==0:
        nb_replay=1
    for i in range(0,nb_replay):
      if not quiet:
        ZopeTestCase._print('\n  Playing step %s' % self._method_name)
        ZopeTestCase._print('\n    -> %s' % method.__doc__)
        LOG('Step.play', 0, '  Playing step %s' % self._method_name)
        LOG('Step.play', 0, '    -> %s' % method.__doc__)
      method(sequence=sequence)
  Step.play = play

  def playSequence(self, sequence_string, quiet=0) :
    ZopeTestCase._print('\n\n\n---------------------------------------------------------------------')
    ZopeTestCase._print('\nStarting New Sequence %s :' % self._TestCase__testMethodName)
    ZopeTestCase._print('\n * %s... \n' % self._TestCase__testMethodDoc)
    LOG('Sequence.play', 0, 'Starting New Sequence %s :' % self._TestCase__testMethodName)
    LOG('Sequence.play', 0, ' * %s... \n' % self._TestCase__testMethodDoc)
    sequence_list = SequenceList()
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    self.createManagerAndLogin()

    # add a dummy mailhost not to send real messages
    if 'MailHost' in self.portal.objectIds():
      self.portal.manage_delObjects(['MailHost'])
    self.portal._setObject('MailHost', DummyMailHost('MailHost'))

    # remove all message in the message_table because
    # the previous test might have failed
    message_list = self.getPortal().portal_activities.getMessageList()
    for message in message_list:
      self.getPortal().portal_activities.manageCancel(message.object_path,
                                                      message.method_id)
    self.createUsers()
    self.createOrganisations()

    # XXX quick hack not to have mysql database pre-fill.
    self.portal.__class__.DeclarationTVA_zGetSIGTASInformation \
        = lambda x,**kw: []

    self.tic()
    
  def beforeTearDown(self):
    """Clean up."""
    for module in self.portal.objectValues(spec=('ERP5 Folder',)):
      # we want to keep some IDs
      module.manage_delObjects([x for x in module.objectIds()
                                if x not in ('EUR',)])
    self.tic()

  def getUserFolder(self) :
    return getattr(self.getPortal(), 'acl_users', None)

  loginAsUser = PortalTestCase.login

  diff_list = lambda self,x,y: [i for i in x if i not in y] 

  def createManagerAndLogin(self):
    """
      Create a simple user in user_folder with manager rights.
      This user will be used to initialize data in the method afterSetup
    """
    self.getUserFolder()._doAddUser('manager', 'manager', self.all_role_list, 
                                    [])
    self.login('manager')
  
  def createOneUser(self, username, function=None, group=None):
     """Create one person that will be users."""
     person_module = self.getPersonModule()
     user = person_module.newContent(
                              portal_type='Person',
                              reference=username,
                              title=username,
                              id=username,
                              password='secret')
     assignment = user.newContent(portal_type='Assignment')
     if function is not None:
       assignment.setFunction(function)
       self.assertNotEqual(assignment.getFunctionValue(), None)
     if group is not None:
       assignment.setGroup(group)
       self.assertNotEqual(assignment.getGroupValue(), None)
     assignment.open()

  def createUsers(self):
    """Create persons that will be users."""
    module = self.getPersonModule()
    if len(module.getObjectIds()) == 0:
      # create users
      self.createOneUser(self.assignor_login, 'function/section/chef', 
          'group/dgid/di/cge')
      self.createOneUser(self.assignee_login, 'function/impots/inspecteur', 
          'group/dgid/di/cge')
      self.createOneUser(self.assignee_login_2, 'function/impots/inspecteur', 
          'group/dgid/di/cge')
      self.createOneUser(self.associate_login, 'function/section/chef', 
          'group/dgid/di/csf/bf')

      # make this available to catalog
      self.tic()

  def createOneOrganisation(self, username, role=None, function=None, 
                            group=None):
    """Create one organisation that will be user."""
    organisation_module = self.getOrganisationModule()
    user = organisation_module.newContent(
                             portal_type='Organisation',
                             title=username,
                             id=username,
                             reference=username,
                             password='secret')
    user.setRole(role)
    user.setFunction(function)
    user.setGroup(group)

    self.assertEqual(user.getRole(), role)
    self.assertEqual(user.getFunction(), function)
    self.assertEqual(user.getGroup(), group)
    self.assertEqual(user.getReference(), username)
  
  def createOrganisations(self):
    """Create organisations that will be users."""
    module = self.getOrganisationModule()
    if len(module.getObjectIds()) == 0:
      self.createOneOrganisation(self.organisation_1_login, 
          role='entreprise/siege')
      self.createOneOrganisation(self.organisation_2_login, 
          role='entreprise/siege')

      # make this available to catalog
      self.tic()

  def checkRights(self, object_list, security_mapping, username):
    self.loginAsUser(username)
    user = getSecurityManager().getUser()
    if type(object_list) != type([]):
      object_list = [object_list,]
    for object in object_list:
      for permission, has in security_mapping.items():
        if user.has_permission(permission, object) and not has:
          self.fail('%s Permission should be Unauthorized on %s' % \
                                                ( permission,
                                                  object.getRelativeUrl()))
        if not(user.has_permission(permission, object)) and has:
          self.fail('%s Permission should be Authorized on %s' % \
                                                ( permission,
                                                  object.getRelativeUrl()))

  def checkTransition(self, object_list, possible_transition_list, 
                      not_possible_transition_list, username):
    
    if type(object_list) != type([]):
      object_list = [object_list,]
    for object in object_list:
      for transition in possible_transition_list:
        self.failUnlessUserCanPassWorkflowTransition(username, transition, 
                                                     object)
      for transition in not_possible_transition_list:
        self.failIfUserCanPassWorkflowTransition(username, transition, object)

  # Copied from ERP5Type/patches/CMFMailIn.py
  def decode_email(self, file):
    # Prepare result
    theMail = {
      'attachment_list': [],
      'body': '',
      # Place all the email header in the headers dictionary in theMail
      'headers': {}
    }
    # Get Message
    msg = email.message_from_string(file)
    # Back up original file
    theMail['__original__'] = file
    # Recode headers to UTF-8 if needed
    for key, value in msg.items():
      decoded_value_list = decode_header(value)
      unicode_value = make_header(decoded_value_list)
      new_value = unicode_value.__unicode__().encode('utf-8')
      theMail['headers'][key.lower()] = new_value
    # Filter mail addresses
    for header in ('resent-to', 'resent-from', 'resent-cc', 'resent-sender',
                   'to', 'from', 'cc', 'sender', 'reply-to'):
      header_field = theMail['headers'].get(header)
      if header_field:
          theMail['headers'][header] = parseaddr(header_field)[1]
    # Get attachments
    body_found = 0
    for part in msg.walk():
      content_type = part.get_content_type()
      file_name = part.get_filename()
      # multipart/* are just containers
      # XXX Check if data is None ?
      if content_type.startswith('multipart'):
        continue
      # message/rfc822 contains attached email message
      # next 'part' will be the message itself
      # so we ignore this one to avoid doubling
      elif content_type == 'message/rfc822':
        continue
      elif content_type in ("text/plain", "text/html"):
        charset = part.get_content_charset()
        payload = part.get_payload(decode=True)
        #LOG('CMFMailIn -> ',0,'charset: %s, payload: %s' % (charset,payload))
        if charset:
          payload = unicode(payload, charset).encode('utf-8')
        if body_found:
          # Keep the content type
          theMail['attachment_list'].append((file_name,
                                             content_type, payload))
        else:
          theMail['body'] = payload
          body_found = 1
      else:
        payload = part.get_payload(decode=True)
        # Keep the content type
        theMail['attachment_list'].append((file_name, content_type,
                                           payload))
    return theMail

  def _assertUserExists(self, login, password):
    """Checks that a user with login and password exists and can log in to the
    system.
    """
    from Products.PluggableAuthService.interfaces.plugins import\
                                                      IAuthenticationPlugin
    uf = self.getUserFolder()
    self.assertNotEquals(uf.getUserById(login, None), None)
    for plugin_name, plugin in uf._getOb('plugins').listPlugins(
                                IAuthenticationPlugin ):
      if plugin.authenticateCredentials(
                  {'login':login, 'password':password}) is not None:
        break
    else:
      self.fail("No plugin could authenticate '%s' with password '%s'" %
              (login, password))

  def checkWorklist(self, portal_type, count, validation_state, login):
    '''
      check that there is 'count' item in the worklist for 'portal_type' and
      'validation_state' logged with 'login'
    '''

    # save previous user
    previous_user = getSecurityManager().getUser().getIdOrUseName()
    self.loginAsUser(login)

    worklist_dict = self.portal.getPortalTypeWorklistDictForWorkflow(\
        self.portal,
        workflow_list=['egov_universal_workflow', 'egov_anonymous_workflow'])
    self.assertNotEquals(worklist_dict, {})
    self.assertEqual(worklist_dict.has_key(portal_type), True)
    portal_type_dict = worklist_dict[portal_type]
    self.assertEqual(portal_type_dict.has_key(validation_state), True)
    self.assertEqual(portal_type_dict[validation_state]['count'], count)

    # relog with previous user
    if previous_user in ('Anonymous User', 'ERP5TypeTestCase'):
      self.logout()
    else:
      self.loginAsUser(previous_user)
 

