# Copyright (c) 2002-2012 Nexedi SA and Contributors. All Rights Reserved.

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime

class TestERP5BearerToken(ERP5TypeTestCase):
  """
  ERP5 Bearer Token extraction
  """

  test_token_extraction_id = 'bearer_test_extraction'

  def generateNewId(self):
    return str(self.portal.portal_ids.generateNewId(
                                     id_group=('bearer_token_test_id')))

  def getTokenCredential(self, request):
    plugin = getattr(self.portal.acl_users, self.test_token_extraction_id)
    return plugin.extractCredentials(request).get('external_login')

  def createPerson(self, reference):
    """Creates a person in person module, and returns the object, after
    indexing is done. """
    person_module = self.getPersonModule()
    person = person_module.newContent(portal_type='Person',
      reference='P' + reference)
    person.newContent(portal_type = 'Assignment').open()
    self.tic()
    return person

  def setUpBearerTokenKey(self):
    self.preference = self.portal.portal_preferences.newContent(
      portal_type='System Preference',
      priority=1,
      preferred_bearer_token_key=self.test_id)
    self.preference.enable()
    self.tic()

  def setupBearerExtraction(self):
    pas = self.portal.acl_users
    bearer_extraction_list = [q for q in pas.objectValues() \
        if q.meta_type == 'ERP5 Bearer Extraction Plugin']
    if len(bearer_extraction_list) == 0:
      dispacher = pas.manage_addProduct['ERP5Security']
      dispacher.addERP5BearerExtractionPlugin(self.test_token_extraction_id)
      getattr(pas, self.test_token_extraction_id).manage_activateInterfaces(
        ('IExtractionPlugin',))
    elif len(bearer_extraction_list) > 1:
      raise ValueError
    self.commit()

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.portal = self.getPortalObject()
    self.test_id = self.generateNewId()
    self.person = self.createPerson(self.test_id)
    self.setUpBearerTokenKey()
    self.setupBearerExtraction()
    self.tic()

  def beforeTearDown(self):
    self.portal.portal_preferences.deleteContent(self.preference.getId())
    self.tic()

  def test_working_token(self):
    token, expiration_time = self.person.Person_getBearerToken()
    self.portal.REQUEST._auth = 'Bearer %s' % token
    reference = self.getTokenCredential(self.portal.REQUEST)
    self.assertEqual(reference, self.person.Person_getUserId())

  def test_different_user_agent(self):
    token, expiration_time = self.person.Person_getBearerToken()
    self.portal.REQUEST._auth = 'Bearer %s' % token
    self.portal.REQUEST.environ['USER_AGENT'] = 'different user agent'
    reference = self.getTokenCredential(self.portal.REQUEST)
    self.assertEqual(reference, None)

  def test_different_remote_addr(self):
    token, expiration_time = self.person.Person_getBearerToken()
    self.portal.REQUEST._auth = 'Bearer %s' % token
    self.portal.REQUEST.environ['REMOTE_ADDR'] = 'different remote addr'
    reference = self.getTokenCredential(self.portal.REQUEST)
    self.assertEqual(reference, None)

  def test_no_bearer_token_key(self):
    self.preference.edit(preferred_bearer_token_key='')
    self.tic()
    self.assertRaises(ValueError, self.person.Person_getBearerToken)

  def test_changed_bearer_token_key(self):
    token, expiration_time = self.person.Person_getBearerToken()
    self.portal.REQUEST._auth = 'Bearer %s' % token
    self.preference.edit(preferred_bearer_token_key='changed')
    self.tic()
    reference = self.getTokenCredential(self.portal.REQUEST)
    self.assertEqual(reference, None)

  def test_expired_token(self):
    # create expired token
    # as everything in scripts is publishable and for now logic is in scripts
    # they are not allowing to pass arguments, so lets hack in test
    token = {
      'expiration_timestamp': DateTime()-1,
      'reference': self.person.Person_getUserId(),
      'user-agent': self.portal.REQUEST.getHeader('User-Agent'),
      'remote-addr': self.portal.REQUEST.get('REMOTE_ADDR')
    }
    hmac = self.portal.Base_getHMAC(self.portal.Base_getBearerTokenKey(), str(
      token).encode('utf-8'))
    self.portal.Base_setBearerToken(hmac, token)
    reference = self.getTokenCredential(self.portal.REQUEST)
    self.assertEqual(reference, None)
