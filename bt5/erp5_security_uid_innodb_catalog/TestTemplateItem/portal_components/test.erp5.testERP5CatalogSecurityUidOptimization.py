# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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

from six.moves import urllib
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class SecurityUidOptimizationTestCase(ERP5TypeTestCase):

  def afterSetUp(self):
    self.login()
    # this test is expected to run on an empty site
    self.assertFalse(self.portal.person_module.contentValues())

    group = self.portal.portal_categories.group
    if 'g1' not in group.objectIds():
      group.newContent(portal_type='Category', id='g1', codification='GROUP1')
    if 'g2' not in group.objectIds():
      group.newContent(portal_type='Category', id='g2', codification='GROUP2')
    local_role_group = self.portal.portal_categories.local_role_group
    if 'Alternate' not in local_role_group.objectIds():
      local_role_group.newContent(
        portal_type='Category',
        reference='Alternate',
        id='Alternate')
    if 'Other' not in local_role_group.objectIds():
      local_role_group.newContent(
        portal_type='Category',
        reference='Other',
        id='Other')

  def beforeTearDown(self):
    self.abort()
    for portal_type in (
      self.portal.portal_types.Organisation,
      self.portal.portal_types.Person,
    ):
      portal_type.manage_delObjects(ids=[
        ri.getId() for ri in portal_type.contentValues(
          portal_type='Role Information')])
    for module in (
      self.portal.organisation_module,
      self.portal.person_module,
    ):
      if list(module.objectIds()):
        module.manage_delObjects(ids=list(module.objectIds()))
    self.tic()


class TestSecurityUidOptimizationCatalog(SecurityUidOptimizationTestCase):

  def test_search_catalog(self):
    """Test usage of local_roles_group_id when searching catalog.
    """
    sql_connection = self.getSQLConnection()
    sql_catalog = self.portal.portal_catalog.getSQLCatalog()

    # configure security on person, each user will be able to see his own
    # person thanks to an Auditor role on "Alternate" local roles group id.
    self.portal.portal_types.Person.newContent(
      portal_type='Role Information',
      role_name='Auditor',
      role_base_category_script_id='ERP5Type_getSecurityCategoryFromSelf',
      role_base_category='agent',
      local_role_group_value=self.portal.portal_categories.local_role_group.Alternate)
    # add another role information that does not grant view permission
    self.portal.portal_types.Person.newContent(
      portal_type='Role Information',
      role_name='Unknown',
      role_category_list=('group/g1', ),
      role_base_category='group',
      local_role_group_value=self.portal.portal_categories.local_role_group.Alternate)
    self.tic()

    # create persons and users
    user1 = self.portal.person_module.newContent(portal_type='Person',
      reference='user1')
    user1_id = user1.Person_getUserId()
    user1.newContent(portal_type='Assignment', group='g1').open()
    user1.newContent(portal_type='ERP5 Login', reference='user1').validate()
    user1.updateLocalRolesOnSecurityGroups()
    self.assertEqual(user1.__ac_local_roles__.get(user1_id), ['Auditor'])
    self.assertEqual(user1.__ac_local_roles__.get('GROUP1'), ['Unknown'])

    user2 = self.portal.person_module.newContent(portal_type='Person',
      reference='user2')
    user2_id = user2.Person_getUserId()
    user2.newContent(portal_type='Assignment', group='g1').open()
    user2.newContent(portal_type='ERP5 Login', reference='user2').validate()
    user2.updateLocalRolesOnSecurityGroups()
    self.assertEqual(user2.__ac_local_roles__.get(user2_id), ['Auditor'])
    self.assertEqual(user2.__ac_local_roles__.get('GROUP1'), ['Unknown'])
    self.tic()

    # security_uid_dict in catalog contains entries for user1 and user2:
    user1_alternate_security_uid = sql_catalog.security_uid_dict[
      ('Alternate', ('user:' + user1_id, 'user:' + user1_id + ':Auditor'))]
    user2_alternate_security_uid = sql_catalog.security_uid_dict[
      ('Alternate', ('user:' + user2_id, 'user:' + user2_id + ':Auditor'))]

    # those entries are in alternate security table
    alternate_roles_and_users = sql_connection.manage_test(
      "SELECT uid, alternate_security_uid from alternate_roles_and_users "
      "WHERE alternate_security_uid is not null"
    ).dictionaries()
    self.assertIn(dict(uid=user1.getUid(),
                          alternate_security_uid=user1_alternate_security_uid),
                    alternate_roles_and_users)
    self.assertIn(dict(uid=user2.getUid(),
                          alternate_security_uid=user2_alternate_security_uid),
                    alternate_roles_and_users)

    # low level check of the security query of a logged in user
    self.loginByUserName('user1')
    security_query = self.portal.portal_catalog.getSecurityQuery()
    # XXX: this test is introspecting too much, but there is currently no
    # obvious better way.
    # security_query can be:
    # - None if caller is superuser (must not be the case here)
    # - a SimpleQuery if caller has no view permissions at all (must not be
    #   the case here)
    # - a ComplexQuery containing SimpleQueries detailing security conditions
    #   (this is what is expected here)
    alternate_security_query, = [
      q for q in security_query.query_list
      if q.column == 'alternate_security_uid'
    ]
    self.assertEqual(user1_alternate_security_uid,
      alternate_security_query.value)

    # high level check that that logged in user can see document
    self.assertEqual([user1],
      [o.getObject() for o in self.portal.portal_catalog(portal_type='Person')])
    # also with local_roles= argument which is used in worklists
    self.assertEqual([user1],
      [o.getObject() for o in self.portal.portal_catalog(portal_type='Person',
        local_roles='Auditor')])

    # searches still work for other users
    self.loginByUserName('user2')
    self.assertEqual([user2],
      [o.getObject() for o in self.portal.portal_catalog(portal_type='Person')])

    self.login()
    self.assertSameSet([user1, user2],
      [o.getObject() for o in
        self.portal.portal_catalog(portal_type='Person')])

    # portal types that acquire roles properly acquire the local role group
    # id mapping
    self.assertTrue(self.portal.portal_types.Career.getTypeAcquireLocalRole())
    career = user1.newContent(portal_type='Career')
    self.tic()

    alternate_roles_and_users = sql_connection.manage_test(
      "SELECT uid, alternate_security_uid from alternate_roles_and_users "
      "WHERE alternate_security_uid is not null"
    ).dictionaries()
    self.assertIn(dict(uid=career.getUid(),
                          alternate_security_uid=user1_alternate_security_uid),
                    alternate_roles_and_users)
    self.loginByUserName('user1')
    self.assertEqual([career],
      [o.getObject() for o in self.portal.portal_catalog(portal_type='Career')])
    self.loginByUserName('user2')
    self.assertEqual([],
      [o.getObject() for o in self.portal.portal_catalog(portal_type='Career')])


class TestSecurityUidOptimizationWorklist(SecurityUidOptimizationTestCase):

  def assertWorklistCount(self, username, expected_count_by_worklist_id):
    self.loginByUserName(username)
    self.portal.portal_workflow.refreshWorklistCache()
    self.portal.portal_caches.clearAllCache()
    worklist_info_by_worklist_id = {
      r['worklist_id']: r
      for r in self.portal.portal_workflow.listActions(object=self.portal)
      if r['category'] == 'global'
      and r['workflow_id'] == 'security_uid_test_simulation_workflow'}
    self.assertEqual(
      {
        worklist_id: worklist_info['count']
        for (worklist_id, worklist_info)
        in worklist_info_by_worklist_id.items()},
      expected_count_by_worklist_id,
    )
    for worklist_info in worklist_info_by_worklist_id.values():
      search_kw = {
        k.replace(':list', ''): v
        for (k, v)
        in dict(urllib.parse.parse_qs(urllib.parse.urlparse(worklist_info['url']).query)).items()}
      search_kw.pop('reset', None)
      self.assertEqual(
        len(self.portal.portal_catalog(**search_kw)),
        worklist_info['count'])

  def test_worklists(self):
    # Persons
    # g1 Assignee uses default security_uid
    #   => security_uid_invalidated, security_uid_or_alternate_security_uid_draft
    # g2 Assignor uses alternate_security_uid
    #   => alternate_security_uid_validated, security_uid_or_alternate_security_uid_draft
    self.portal.portal_types.Person.newContent(
      portal_type='Role Information',
      role_name='Assignee',
      role_category_list=('group/g1', ),
      role_base_category='group',
    )
    self.portal.portal_types.Person.newContent(
      portal_type='Role Information',
      role_name='Assignor',
      role_category_list=('group/g2', ),
      role_base_category='group',
      local_role_group_value=self.portal.portal_categories.local_role_group.Alternate,
    )
    user_g1 = self.portal.person_module.newContent(
      portal_type='Person',
      user_id='user_g1')
    user_g1.newContent(portal_type='Assignment', group='g1').open()
    user_g1.newContent(portal_type='ERP5 Login', reference='user_g1').validate()
    user_g2 = self.portal.person_module.newContent(
      portal_type='Person',
      user_id='user_g2')
    user_g2.newContent(portal_type='Assignment', group='g2').open()
    user_g2.newContent(portal_type='ERP5 Login', reference='user_g2').validate()
    user_g1_g2 = self.portal.person_module.newContent(
      portal_type='Person',
      user_id='user_g1_g2')
    user_g1_g2.newContent(portal_type='Assignment', group='g1').open()
    user_g1_g2.newContent(portal_type='Assignment', group='g2').open()
    user_g1_g2.newContent(portal_type='ERP5 Login', reference='user_g1_g2').validate()
    self.tic()

    self.portal.person_module.newContent(portal_type='Person', first_name='validated').validate()
    invalidated = self.portal.person_module.newContent(portal_type='Person', first_name='invalidated')
    invalidated.validate()
    invalidated.invalidate()
    # create documents owned by users, for Owner worklists
    self.portal.person_module.manage_permission(
      'Add portal content', ['Authenticated'])
    self.loginByUserName('user_g2')
    self.portal.person_module.newContent(portal_type='Person', first_name='draft')
    self.tic()

    self.assertWorklistCount(
       'user_g1',
       {
         'security_uid_invalidated': 1,
         'security_uid_or_alternate_security_uid_draft': 4,  # 3 users + 1 draft
       }
     )
    self.assertWorklistCount(
      'user_g2',
      {
        'viewable_owner': 1,
        'alternate_security_uid_validated': 1,
        'security_uid_or_alternate_security_uid_draft': 4,
      }
    )
    self.assertWorklistCount(
      'user_g1_g2',
      {
        'alternate_security_uid_validated': 1,
        'security_uid_invalidated': 1,
        'security_uid_or_alternate_security_uid_draft': 4,
      }
    )

  def test_worklist_exclusionlist_collision(self):
    # non-regression test for an issue with multiple local role group
    self.portal.portal_types.Organisation.newContent(
      portal_type='Role Information',
      role_name='Assignee',
      role_category_list=('group/g1', ),
      role_base_category='group',
      local_role_group_value=self.portal.portal_categories.local_role_group.Alternate,
    )
    self.portal.portal_types.Organisation.newContent(
      portal_type='Role Information',
      role_name='Assignor',
      role_category_list=('group/g2', ),
      role_base_category='group',
      local_role_group_value=self.portal.portal_categories.local_role_group.Alternate,
    )
    self.portal.portal_types.Person.newContent(
      portal_type='Role Information',
      role_name='Assignee',
      role_category_list=('group/g1', ),
      role_base_category='group',
      local_role_group_value=self.portal.portal_categories.local_role_group.Other,
    )
    self.portal.portal_types.Person.newContent(
      portal_type='Role Information',
      role_name='Assignor',
      role_category_list=('group/g2', ),
      role_base_category='group',
      local_role_group_value=self.portal.portal_categories.local_role_group.Alternate,
    )

    self.portal.portal_types.Currency.newContent(
      portal_type='Role Information',
      role_name='Assignor',
      role_category_list=('group/g1', ),
      role_base_category='group',
      local_role_group_value=self.portal.portal_categories.local_role_group.Alternate,
    )
    self.portal.currency_module.newContent(portal_type='Currency')

    collision_worklist = self.portal.portal_workflow.security_uid_test_simulation_workflow.newContent(
      portal_type='Worklist',
      reference='collision_worklist',
      action_name='collision_worklist',
      action_type='global',
      action='/?portal_type:list=%(portal_type)s&local_roles:list=%(local_roles)s&validation_state=%(validation_state)s'
    )
    collision_worklist.setCriterion('portal_type', ('Organisation',))
    collision_worklist.setCriterion('local_roles', ('Assignee', 'Assignor'))
    collision_worklist.setCriterion('validation_state', ('draft',))

    def remove_worklist():
      self.portal.portal_workflow.security_uid_test_simulation_workflow.manage_delObjects(
        [collision_worklist.getId()])
      self.tic()
    self.addCleanup(remove_worklist)

    user_g1 = self.portal.person_module.newContent(
      portal_type='Person',
      user_id='user_g1')
    user_g1.newContent(portal_type='Assignment', group='g1').open()
    user_g1.newContent(portal_type='ERP5 Login', reference='user_g1').validate()
    self.tic()

    self.portal.organisation_module.newContent(portal_type='Organisation')
    self.portal.organisation_module.newContent(portal_type='Organisation').validate()
    self.tic()

    self.assertWorklistCount(
       'user_g1',
       {
         collision_worklist.getReference(): 1,
        # Worklist from business template
        'security_uid_or_alternate_security_uid_draft': 1,
       }
     )
