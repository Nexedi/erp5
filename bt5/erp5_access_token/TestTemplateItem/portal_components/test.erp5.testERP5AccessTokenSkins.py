# Copyright (c) 2002-2013 Nexedi SA and Contributors. All Rights Reserved.

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import transaction

class TestERP5AccessTokenSkins(ERP5TypeTestCase):

  test_token_extraction_id = 'test_erp5_access_token_extraction'

  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_access_token')

  def generateNewId(self):
    return str(self.portal.portal_ids.generateNewId(
         id_group=('erp5_access_token_test_id')))

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.portal = self.getPortalObject()
    self.new_id = self.generateNewId()
    self._setupAccessTokenExtraction()
    transaction.commit()
    self.tic()

  def _setupAccessTokenExtraction(self):
    pas = self.portal.acl_users
    access_extraction_list = [q for q in pas.objectValues() \
        if q.meta_type == 'ERP5 Access Token Extraction Plugin']
    if len(access_extraction_list) == 0:
      dispacher = pas.manage_addProduct['ERP5Security']
      dispacher.addERP5AccessTokenExtractionPlugin(self.test_token_extraction_id)
      getattr(pas, self.test_token_extraction_id).manage_activateInterfaces(
        ('IExtractionPlugin', 'IAuthenticationPlugin'))
    elif len(access_extraction_list) == 1:
      self.test_token_extraction_id = access_extraction_list[0].getId()
    elif len(access_extraction_list) > 1:
      raise ValueError
    transaction.commit()

  def _createPerson(self, new_id):
    """Creates a person in person module, and returns the object, after
    indexing is done. """
    person_module = self.getPersonModule()
    person = person_module.newContent(portal_type='Person',
      user_id='TESTP-' + new_id)
    person.newContent(portal_type = 'Assignment').open()
    transaction.commit()
    return person

  def _getTokenCredential(self, request):
    """Authenticate the request and return (user_id, login) or None if not authorized."""
    plugin = getattr(self.portal.acl_users, self.test_token_extraction_id)
    return plugin.authenticateCredentials(plugin.extractCredentials(request))

  def _createRestrictedAccessToken(self, new_id, person, method, url_string):
    access_token = self.portal.access_token_module.newContent(
                    portal_type="Restricted Access Token",
                    url_string=url_string,
                    url_method=method,
                  )
    if person:
      access_token.edit(agent_value=person)
    return access_token

  def _createOneTimeRestrictedAccessToken(self, new_id, person, method, url_string):
    access_token = self.portal.access_token_module.newContent(
                    portal_type="One Time Restricted Access Token",
                    url_string=url_string,
                    url_method=method,
                  )
    if person:
      access_token.edit(agent_value=person)
    return access_token

  def test_working_token(self):
    person = self.person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST.form["access_token"] = access_token.getId()
    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url
    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    result = self._getTokenCredential(self.portal.REQUEST)
    self.assertTrue(result)
    user_id, login = result
    self.assertEqual(user_id, person.Person_getUserId())
    # tokens have a login value, for auditing purposes
    self.assertIn('token', login)

  def test_bad_token(self):
    person = self.person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST.form["access_token"] = "XYSYDT-YDTYSD"
    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url
    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    result = self._getTokenCredential(self.portal.REQUEST)
    self.assertFalse(result)

  def test_RestrictedAccessToken_getUserId(self):
    person = self.person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url
    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    result = access_token.RestrictedAccessToken_getUserId()

    self.assertEqual(result, person.Person_getUserId())
    self.assertEqual(access_token.getValidationState(), 'validated')

  def test_RestrictedAccessToken_getUserId_access_token_secret(self):
    person = self.person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url

    result = access_token.RestrictedAccessToken_getUserId()
    self.assertEqual(result, None)

    self.portal.REQUEST.form["access_token_secret"] = "XYXYXYXY"
    self.assertEqual(result, None)

    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    result = access_token.RestrictedAccessToken_getUserId()

    self.assertEqual(result, person.Person_getUserId())
    self.assertEqual(access_token.getValidationState(), 'validated')

  def test_RestrictedAccessToken_getUserId_no_agent(self):
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        None,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url
    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    result = access_token.RestrictedAccessToken_getUserId()
    self.assertEqual(result, None)

  def test_RestrictedAccessToken_getUserId_wrong_values(self):
    person = self.person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    self.tic()
    result = access_token.RestrictedAccessToken_getUserId()
    self.assertEqual(result, None)

    access_token.validate()
    self.tic()

    self.portal.REQUEST["REQUEST_METHOD"] = "POST"
    self.portal.REQUEST["ACTUAL_URL"] = access_url
    self.portal.REQUEST.form["access_token_secret"] = access_token.getReference()

    result = access_token.RestrictedAccessToken_getUserId()
    self.assertEqual(result, None)

    self.portal.REQUEST["ACTUAL_URL"] = "http://exemple.com/foo.bar"

    result = access_token.RestrictedAccessToken_getUserId()
    self.assertEqual(result, None)

    access_token.invalidate()
    self.tic()

    result = access_token.RestrictedAccessToken_getUserId()
    self.assertEqual(result, None)


  def test_OneTimeRestrictedAccessToken_getUserId(self):
    person = self.person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "GET"
    access_token = self._createOneTimeRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    access_token.validate()
    self.tic()

    self.portal.REQUEST["REQUEST_METHOD"] = access_method
    self.portal.REQUEST["ACTUAL_URL"] = access_url

    result = access_token.OneTimeRestrictedAccessToken_getUserId()

    self.assertEqual(result, person.Person_getUserId())
    self.assertEqual(access_token.getValidationState(), 'invalidated')

  def test_OneTimeRestrictedAccessToken_getUserId_wrong_values(self):
    person = self.person = self._createPerson(self.new_id)
    access_url = "http://exemple.com/foo"
    access_method = "POST"
    access_token = self._createOneTimeRestrictedAccessToken(self.new_id,
                        person,
                        access_method,
                        access_url)
    self.tic()
    result = access_token.OneTimeRestrictedAccessToken_getUserId()
    self.assertEqual(result, None)

    access_token.validate()
    self.tic()

    self.portal.REQUEST["REQUEST_METHOD"] = "GET"
    self.portal.REQUEST["ACTUAL_URL"] = access_url

    result = access_token.OneTimeRestrictedAccessToken_getUserId()
    self.assertEqual(result, None)

    self.portal.REQUEST["ACTUAL_URL"] = "http://exemple.com/foo.bar"

    result = access_token.OneTimeRestrictedAccessToken_getUserId()
    self.assertEqual(result, None)
