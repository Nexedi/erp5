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

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase



class TestERP5CatalogSecurityUidOptimization(ERP5TypeTestCase):
  """
    TestERP5CatalogSecurityUidOptimization tests security_uid optmization.
    It is in a different test than TestERP5Catalog as it requires erp5_security_uid_innodb_catalog
    bt5 to be installed in advance.
    XXX: Inherit from TestERP5Catalog so we test default and security_uid optmization with same tests.
  """
  business_template_list = ['erp5_security_uid_innodb_catalog',
                            'erp5_full_text_mroonga_catalog','erp5_base']

  def getBusinessTemplateList(self):
    return self.business_template_list

  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    group = portal.portal_categories.group
    if 'g1' not in group.objectIds():
      group.newContent(portal_type='Category', id='g1', codification='GROUP1')

  def test_local_roles_group_id_on_role_information(self):
    """Test usage of local_roles_group_id when searching catalog.
    """
    sql_connection = self.getSQLConnection()
    sql_catalog = self.portal.portal_catalog.getSQLCatalog()

    # Add a catalog table (uid, alternate_security_uid)
    sql_connection.manage_test(
      """DROP TABLE IF EXISTS alternate_roles_and_users""")

    sql_connection.manage_test("""
CREATE TABLE alternate_roles_and_users (
  `uid` BIGINT UNSIGNED NOT NULL,
  `alternate_security_uid` INT UNSIGNED) """)

    # make it a search table
    current_sql_search_tables = sql_catalog.sql_search_tables
    sql_catalog.sql_search_tables = sql_catalog.sql_search_tables + [
      'alternate_roles_and_users']

    # Configure sql method to insert this table
    sql_catalog.newContent(portal_type='SQL Method',
          id='z_catalog_alternate_roles_and_users_list',
          title='',
          connection_id='erp5_sql_connection',
          arguments_src="\n".join(['uid', 'alternate_security_uid']),
          src="""REPLACE INTO alternate_roles_and_users VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
( <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="alternate_security_uid[loop_item]" type="int" optional>
)<dtml-unless sequence-end>,</dtml-unless>
</dtml-in>""")

    current_sql_catalog_object_list = sql_catalog.sql_catalog_object_list
    sql_catalog.sql_catalog_object_list = \
      current_sql_catalog_object_list + \
         ('z_catalog_alternate_roles_and_users_list',)

    # configure Alternate local roles group id to go in alternate_security_uid
    current_sql_catalog_security_uid_columns =\
      sql_catalog.sql_catalog_security_uid_columns
    sql_catalog.sql_catalog_security_uid_columns = (
      ' | security_uid',
      'Alternate | alternate_security_uid', )

    # add category
    self.portal.portal_categories.local_role_group.newContent(
      portal_type='Category',
      reference = 'Alternate',
      id = 'Alternate')

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
      role_category_list=('group/g1'),
      role_base_category='group',
      local_role_group_value=self.portal.portal_categories.local_role_group.Alternate)

    self.portal.portal_caches.clearAllCache()
    self.tic()

    try:
      # create two persons and users
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
        "SELECT * from alternate_roles_and_users").dictionaries()
      self.assertTrue(dict(uid=user1.getUid(),
                           alternate_security_uid=user1_alternate_security_uid) in
                      alternate_roles_and_users)
      self.assertTrue(dict(uid=user2.getUid(),
                           alternate_security_uid=user2_alternate_security_uid) in
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
        "SELECT * from alternate_roles_and_users").dictionaries()
      self.assertTrue(dict(uid=career.getUid(),
                           alternate_security_uid=user1_alternate_security_uid) in
                      alternate_roles_and_users)
      self.loginByUserName('user1')
      self.assertEqual([career],
        [o.getObject() for o in self.portal.portal_catalog(portal_type='Career')])
      self.loginByUserName('user2')
      self.assertEqual([],
        [o.getObject() for o in self.portal.portal_catalog(portal_type='Career')])

    finally:
      # restore catalog configuration
      sql_catalog.sql_search_tables = current_sql_search_tables
      sql_catalog.sql_catalog_object_list = current_sql_catalog_object_list
      sql_catalog.sql_catalog_security_uid_columns =\
        current_sql_catalog_security_uid_columns
      self.portal.portal_types.Person.manage_delObjects(
        [role.getId() for role in
        self.portal.portal_types.Person.contentValues(
          portal_type='Role Information')])

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5CatalogSecurityUidOptimization))
  return suite
