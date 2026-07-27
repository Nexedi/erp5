# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
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
"""Tests for the erp5_artificial_agent business template (Slice 1: skeleton).

Scope of this test module is deliberately narrow -- it covers ONLY user-id
resolution for the new Artificial Agent portal type, as agreed for the first
code slice (PLAN.md section 6, tests #1). The capping / security-group-mask
tests (#3, #4, #5, #6, #9, #10) and the credential-swap tests (#2) are left as
skipped TODO stubs at the bottom of this file; they belong to Slice 2 (the
product-code change against nxd/master) and Slice 3 (OAuth2 wiring), which are
explicitly out of scope here.

Patterns mirror product/ERP5Security/tests/testERP5Security.py
(UserManagementTestCase) and bt5/erp5_access_token testERP5AccessToken.py.
"""

import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.PluggableAuthService.interfaces.plugins import \
    IAuthenticationPlugin


class TestArtificialAgent(ERP5TypeTestCase):
  """Slice 1: Artificial Agent user-id resolution."""

  def getBusinessTemplateList(self):
    return (
      'erp5_full_text_mroonga_catalog',
      'erp5_base',
      'erp5_artificial_agent',
    )

  def afterSetUp(self):
    self.portal = self.getPortal()
    self.artificial_agent_module = self.portal.artificial_agent_module

  def beforeTearDown(self):
    """Clear the artificial agent module between tests."""
    self.abort()
    module = self.artificial_agent_module
    module.manage_delObjects(list(module.objectIds()))
    self.tic()

  # -- helpers ---------------------------------------------------------------

  def _makeArtificialAgent(self, owner_person=None, tic=True, **kw):
    """Create an Artificial Agent in the module and return it after indexing.

    The init_script (ArtificialAgent_init -> initUserId ->
    ArtificialAgent_initUserId) mints the 'A%i' user id on creation.
    """
    agent = self.artificial_agent_module.newContent(
      portal_type='Artificial Agent', **kw)
    if owner_person is not None:
      # Owner link reuses the existing 'subordination' base category (D3).
      agent.setSubordinationValue(owner_person)
    if tic:
      self.tic()
    return agent

  def _makeOwnerPerson(self, tic=True, **kw):
    person = self.portal.person_module.newContent(portal_type='Person', **kw)
    if tic:
      self.tic()
    return person

  # -- Slice 1 tests: user-id resolution -------------------------------------

  def test_ArtificialAgentGetsUserIdWithAPrefix(self):
    """PLAN #1: a created Artificial Agent gets a user id with the 'A' prefix.

    Person user ids use 'P%i' (document.erp5.Person.initUserId); the Artificial
    Agent type overrides that through the type-based hook
    ArtificialAgent_initUserId with an 'A%i' prefix.
    """
    agent = self._makeArtificialAgent()
    user_id = agent.getUserId()
    self.assertNotEqual(None, user_id)
    self.assertTrue(
      user_id.startswith('A'),
      "Artificial Agent user id %r should start with 'A'" % (user_id,))
    self.assertTrue(
      user_id[1:].isdigit(),
      "Artificial Agent user id %r should be 'A' + integer" % (user_id,))

  def test_ArtificialAgentUserIdIsUnique(self):
    """Two Artificial Agents get distinct user ids."""
    agent_a = self._makeArtificialAgent()
    agent_b = self._makeArtificialAgent()
    self.assertNotEqual(agent_a.getUserId(), agent_b.getUserId())

  def test_ArtificialAgentResolvableByUserIdWithZeroLogins(self):
    """PLAN #1 / study section 2.1: the agent is enumerable/resolvable by user
    id even with ZERO ERP5 Login documents.

    This is the whole point of attaching the ERP5User property sheet at the
    portal-type level: ERP5LoginUserManager resolves users by user id
    independently of any Login document.
    """
    agent = self._makeArtificialAgent()
    user_id = agent.getUserId()

    # No ERP5 Login documents exist on the agent.
    self.assertEqual(
      [], agent.contentValues(portal_type='ERP5 Login'))

    acl_users = self.portal.acl_users
    user_list = acl_users.searchUsers(id=user_id, exact_match=True)
    self.assertEqual(
      1, len(user_list),
      "expected exactly one PAS user for id %r, got %r" % (
        user_id, user_list))
    # With no Login document, the resolved login is None (ERP5LoginUserManager).
    self.assertEqual(None, user_list[0]['login'])
    self.assertEqual([], user_list[0]['login_list'])

    # And the user object itself is resolvable by user id.
    self.assertNotEqual(None, acl_users.getUserById(user_id))

  def test_ArtificialAgentGetUserIdResolutionFallsBackToReference(self):
    """PLAN #1(c): the Person_getUserId resolution helper returns the user id,
    falling back to the reference when no user id is set (BBB ERP5User-style
    users, see erp5_base Person_getUserId).

    The Artificial Agent type_class is Person, so it inherits Person_getUserId.
    """
    agent = self._makeArtificialAgent()
    user_id = agent.getUserId()

    # Primary path: resolution returns the minted 'A%i' user id.
    self.assertEqual(user_id, agent.Person_getUserId())

    # Fallback path: with the user id unset, resolution falls back to the
    # reference.
    agent.setUserId(None)
    agent.setReference('AGENT-REF-1')
    self.tic()
    self.assertEqual(None, agent.getUserId())
    self.assertEqual('AGENT-REF-1', agent.Person_getUserId())

  def test_ArtificialAgentCannotPasswordAuthenticate(self):
    """PLAN #1(d): document the authenticateCredentials non-Person behavior.

    An Artificial Agent is created WITHOUT any ERP5 Login document (D7: no
    password login on the agent). It must therefore not be authenticable by
    any IAuthenticationPlugin via a login/password pair -- even though it is a
    perfectly resolvable PAS user by user id (see test above).

    Note for Slice 2: ERP5LoginUserManager._isUserValueValid hardcodes the
    ('Person',) portal-type tuple on the password/login path
    (ERP5LoginUserManager.py, guard around line 143). Adding 'Artificial Agent'
    to that tuple (PLAN.md D5) is defense-in-depth ONLY; it guards a path the
    agent never uses, and is deferred to the product-code slice against
    nxd/master. This test simply asserts the agent cannot log in with a
    password today, which already holds because no Login exists.
    """
    agent = self._makeArtificialAgent(reference='agent_no_login')
    acl_users = self.portal.acl_users
    for _, plugin in acl_users._getOb('plugins').listPlugins(
        IAuthenticationPlugin):
      self.assertEqual(
        None,
        plugin.authenticateCredentials(
          {'login': 'agent_no_login', 'password': 'secret'}),
        "no plugin should authenticate a password for a login-less agent")

  # -- Slice 2/3 stubs: capping & credential swap (deferred, see PLAN.md) -----

  @unittest.skip("Slice 2: security-group mask / capping enforcement "
                 "(product code vs nxd/master, PLAN.md section 4.4). Not part "
                 "of the skeleton slice.")
  def test_Capping_AgentEffectiveGroupsSubsetOfOwner(self):
    """PLAN #3 (variant A): agent's effective groups == groups(agent) INTERSECT
    groups(owner); an agent-only group is stripped. Deferred to Slice 2."""
    raise NotImplementedError

  @unittest.skip("Slice 2: capping invariant matrix (PLAN.md section 6, #10). "
                 "Must include a reversed workflow (leave_request_workflow).")
  def test_Capping_InvariantMatrix(self):
    """PLAN #10: for a grid of (state x role-pair),
    allowed(agent, D, P) implies allowed(owner, D, P) on all four surfaces.
    Deferred to Slice 2."""
    raise NotImplementedError

  @unittest.skip("Slice 3: OAuth2 credential swap (createSessionForUser), "
                 "requires erp5_oauth2_authorisation + an OAuth2 Client. "
                 "PLAN.md section 4.3.")
  def test_CredentialSwap_MintsSessionForAgentSubject(self):
    """PLAN #2: the connect dialog mints a session for the agent subject; the
    owner-authorisation check refuses a non-owner caller. Deferred to Slice 3.
    """
    raise NotImplementedError


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestArtificialAgent))
  return suite
