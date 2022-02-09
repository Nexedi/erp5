##############################################################################
# coding: utf-8
# Copyright (c) 2019 Nexedi SA and Contributors. All Rights Reserved.
#                     Jérome Perrin <jerome@nexedi.com>
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

from textwrap import dedent

from MySQLdb import OperationalError
from Shared.DC.ZRDB.DA import DA
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestTableStructureMigrationTestCase(ERP5TypeTestCase):
  def beforeTearDown(self):
    self.portal.erp5_sql_connection().query('DROP table if exists X')
    self.portal.erp5_sql_connection().query('DROP table if exists `table`')
    self.commit()

  def query(self, q):
    return self.portal.erp5_sql_connection().query(q)

  def check_upgrade_schema(self, previous_schema, new_schema, table_name='X'):
    self.query(previous_schema)
    da = DA(
        id=self.id(),
        title=self.id(),
        connection_id=self.portal.erp5_sql_connection.getId(),
        arguments=(),
        template=new_schema).__of__(self.portal)
    self.assertTrue(da._upgradeSchema(src__=True))
    da._upgradeSchema()
    self.assertFalse(da._upgradeSchema(src__=True))
    self.assertEqual(
        new_schema,
        self.query('SHOW CREATE TABLE `%s`' % table_name)[1][0][1])

  def test_add_column(self):
    self.check_upgrade_schema(
        dedent(
            """\
      CREATE TABLE `X` (
        `a` int(11) DEFAULT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""),
        dedent(
            """\
      CREATE TABLE `X` (
        `a` int(11) DEFAULT NULL,
        `b` int(11) DEFAULT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""))
    self.query("SELECT a, b FROM X")

  def test_remove_column(self):
    self.check_upgrade_schema(
        dedent(
            """\
      CREATE TABLE `X` (
        `a` int(11) DEFAULT NULL,
        `b` int(11) DEFAULT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""),
        dedent(
            """\
      CREATE TABLE `X` (
        `b` int(11) DEFAULT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""))
    self.query("SELECT b FROM X")
    with self.assertRaisesRegexp(OperationalError,
                                 "Unknown column 'a' in 'field list'"):
      self.query("SELECT a FROM X")

  def test_rename_column(self):
    self.check_upgrade_schema(
        dedent(
            """\
      CREATE TABLE `X` (
        `a` int(11) DEFAULT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""),
        dedent(
            """\
      CREATE TABLE `X` (
        `b` int(11) DEFAULT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""))
    self.query("SELECT b FROM X")
    with self.assertRaisesRegexp(OperationalError,
                                 "Unknown column 'a' in 'field list'"):
      self.query("SELECT a FROM X")

  def test_change_column_type(self):
    self.check_upgrade_schema(
        dedent(
            """\
      CREATE TABLE `X` (
        `a` int(11) DEFAULT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""),
        dedent(
            """\
      CREATE TABLE `X` (
        `a` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""))
    # insterting 1 will be casted as string
    self.query("INSERT INTO X VALUES (1)")
    self.assertEqual(('1',), self.query("SELECT a FROM X")[1][0])

  def test_change_column_default(self):
    self.check_upgrade_schema(
        dedent(
            """\
      CREATE TABLE `X` (
        `a` int(11) DEFAULT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""),
        dedent(
            """\
      CREATE TABLE `X` (
        `a` int(11) DEFAULT 123
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""))
    self.query("INSERT INTO X VALUES ()")
    self.assertEqual((123,), self.query("SELECT a FROM X")[1][0])

  def test_change_column_comment(self):
    self.check_upgrade_schema(
        dedent(
            """\
      CREATE TABLE `X` (
        `a` int(11) NOT NULL COMMENT 'old comment'
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8"""),
        dedent(
            """\
      CREATE TABLE `X` (
        `a` int(11) NOT NULL COMMENT 'new comment'
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8"""))
    self.assertEqual(
        ('a', 'new comment'),
        self.query(
            dedent(
                """\
                SELECT COLUMN_NAME, COLUMN_COMMENT
                FROM information_schema.COLUMNS
                WHERE TABLE_NAME='X'
                """))[1][0],
    )

  def test_add_index(self):
    self.check_upgrade_schema(
        dedent(
            """\
      CREATE TABLE `X` (
        `a` int(11) DEFAULT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""),
        dedent(
            """\
      CREATE TABLE `X` (
        `a` int(11) DEFAULT NULL,
        KEY `idx_a` (`a`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""))
    self.query("SELECT * FROM X USE INDEX (`idx_a`)")

  def test_remove_index(self):
    self.check_upgrade_schema(
        dedent(
            """\
      CREATE TABLE `X` (
        `a` int(11) DEFAULT NULL,
        KEY `idx_a` (`a`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""),
        dedent(
            """\
      CREATE TABLE `X` (
        `a` int(11) DEFAULT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""))
    with self.assertRaisesRegexp(OperationalError,
                                 "Key 'idx_a' doesn't exist in table 'X'"):
      self.query("SELECT * FROM X USE INDEX (`idx_a`)")

  def test_escape(self):
    self.check_upgrade_schema(
        dedent(
            """\
      CREATE TABLE `table` (
        `drop` int(11) DEFAULT NULL,
        `alter` int(11) DEFAULT NULL,
        KEY `CASE` (`drop`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""),
        dedent(
            """\
      CREATE TABLE `table` (
        `and` int(11) DEFAULT NULL,
        `alter` varchar(255) COLLATE utf8_unicode_ci DEFAULT 'BETWEEN',
        KEY `use` (`alter`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""),
        table_name='table')
    self.query(
        "SELECT `alter`, `and` FROM `table` USE INDEX (`use`)")

  def test_change_table_engine(self):
    self.check_upgrade_schema(
        dedent(
            """\
            CREATE TABLE `X` (
              `a` int(11) DEFAULT NULL
            ) ENGINE=MyISAM DEFAULT CHARSET=utf8"""),
        dedent(
            """\
            CREATE TABLE `X` (
              `a` int(11) DEFAULT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8"""))
    self.assertEqual(
        ('X', 'InnoDB'),
        self.query(
            dedent(
                """\
                SELECT TABLE_NAME, ENGINE
                FROM information_schema.TABLES
                WHERE TABLE_NAME='X'
                """))[1][0],
    )

  def test_change_table_comment(self):
    self.check_upgrade_schema(
        dedent(
            """\
            CREATE TABLE `X` (
              `a` int(11) DEFAULT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='old comment'"""),
        dedent(
            """\
            CREATE TABLE `X` (
              `a` int(11) DEFAULT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='new comment'"""))
    self.assertEqual(
        ('X', 'new comment'),
        self.query(
            dedent(
                """\
                SELECT TABLE_NAME, TABLE_COMMENT
                FROM information_schema.TABLES
                WHERE TABLE_NAME='X'
                """))[1][0],
    )
