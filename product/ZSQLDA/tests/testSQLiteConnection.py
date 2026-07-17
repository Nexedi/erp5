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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import os
import sqlite3
import tempfile

from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import skipUnlessSQLite
from Products.ZSQLDA.SQLite import DB, DeferredDB


def _remove_db(path):
  for suffix in ('', '-wal', '-shm'):
    try:
      os.remove(path + suffix)
    except OSError:
      pass


def _safe_close(db):
  try:
    db.db.close()
  except Exception:
    pass


@skipUnlessSQLite
class TestSQLiteConnection(ERP5TypeTestCase):
  """Unit tests for the ZSQLDA SQLite adapter.

  A transactionless connection ('-' prefix) is used so that TM registration
  does not interfere with the ERP5TypeTestCase transaction.
  """

  def _make_db(self, transactionless=True):
    fd, path = tempfile.mkstemp(suffix='.sqlite')
    os.close(fd)
    self.addCleanup(_remove_db, path)
    db = DB(('-' if transactionless else '') + path)
    self.addCleanup(_safe_close, db)
    return db

  def test_transactionless_does_not_use_TM(self):
    db = self._make_db()
    self.assertFalse(db._use_TM)
    self.assertEqual(db._transactions, 0)

  def test_query_returns_items_and_rows(self):
    db = self._make_db()
    db.query(b"CREATE TABLE t (i INTEGER, n REAL, s TEXT, d DATE)")
    db.query(b"INSERT INTO t VALUES (1, 1.5, 'hello', '2020-01-02')")
    items, rows = db.query(b"SELECT i, n, s, d FROM t")
    type_by_name = {it['name']: it['type'] for it in items}
    self.assertEqual(type_by_name['i'], 'i')
    self.assertEqual(type_by_name['n'], 'n')
    self.assertEqual(type_by_name['s'], 't')
    self.assertEqual(type_by_name['d'], 'd')
    self.assertEqual(len(rows), 1)
    i, n, s, d = rows[0]
    self.assertEqual((i, n, s), (1, 1.5, 'hello'))
    self.assertIsInstance(d, DateTime)

  def test_string_date_column_is_converted(self):
    db = self._make_db()
    db.query(b"CREATE TABLE d (foo_date TEXT)")
    db.query(b"INSERT INTO d VALUES ('2020-01-02 03:04:05')")
    items, rows = db.query(b"SELECT foo_date FROM d")
    self.assertEqual(items[0]['type'], 'd')
    self.assertIsInstance(rows[0][0], DateTime)

  def test_type_code_uses_first_non_null_value(self):
    db = self._make_db()
    db.query(b"CREATE TABLE nn (x INTEGER)")
    db.query(b"INSERT INTO nn VALUES (NULL)")
    db.query(b"INSERT INTO nn VALUES (5)")
    items, rows = db.query(b"SELECT x FROM nn ORDER BY rowid")
    self.assertIsNone(rows[0][0])
    self.assertEqual(rows[1][0], 5)
    self.assertEqual(items[0]['type'], 'i')

  def test_type_code_defaults_to_text_when_all_null(self):
    db = self._make_db()
    db.query(b"CREATE TABLE an (x INTEGER)")
    db.query(b"INSERT INTO an VALUES (NULL)")
    items, rows = db.query(b"SELECT x FROM an")
    self.assertEqual(items[0]['type'], 't')

  def test_max_rows_appends_limit(self):
    db = self._make_db()
    db.query(b"CREATE TABLE m (a INTEGER)")
    for value in range(10):
      db.query(b"INSERT INTO m VALUES (%d)" % value)
    _, rows = db.query(b"SELECT a FROM m", max_rows=3)
    self.assertEqual(len(rows), 3)

  def test_max_rows_wraps_existing_limit(self):
    db = self._make_db()
    db.query(b"CREATE TABLE m (a INTEGER)")
    for value in range(10):
      db.query(b"INSERT INTO m VALUES (%d)" % value)
    _, rows = db.query(b"SELECT a FROM m LIMIT 100", max_rows=3)
    self.assertEqual(len(rows), 3)

  def test_string_literal(self):
    db = self._make_db()
    self.assertEqual(db.string_literal(None), b'NULL')
    self.assertEqual(db.string_literal(b'\x00\xff'), b"x'00ff'")
    self.assertEqual(db.string_literal("O'Brien"), b"'O''Brien'")

  def test_null_byte_round_trip(self):
    db = self._make_db()
    literal = db.string_literal("a\0b")
    db.query(b"CREATE TABLE sl (v TEXT)")
    db.query(b"INSERT INTO sl (v) VALUES (" + literal + b")")
    _, rows = db.query(b"SELECT v FROM sl")
    self.assertEqual(rows[0][0], "a\0b")

  def test_parameter_binding(self):
    db = self._make_db()
    db.query(b"CREATE TABLE ab (k INTEGER, v TEXT)")
    db.query(b"INSERT INTO ab VALUES (1, 'one')")
    db.query(b"INSERT INTO ab VALUES (2, 'two')")
    _, rows = db.query("SELECT v FROM ab WHERE k = ?", args=(2,))
    self.assertEqual(rows[0][0], 'two')

  def test_tables_and_columns(self):
    db = self._make_db()
    db.query(b"CREATE TABLE things (id INTEGER PRIMARY KEY, label TEXT)")
    names = [t['TABLE_NAME'] for t in db.tables()]
    self.assertIn('things', names)
    by_name = {c['Name']: c for c in db.columns('things')}
    self.assertEqual(by_name['id']['Icon'], 'int')
    self.assertTrue(by_name['id']['PrimaryKey'])
    self.assertEqual(by_name['label']['Icon'], 'text')

  def test_columns_missing_table_returns_empty(self):
    db = self._make_db()
    self.assertEqual(db.columns('no_such_table'), [])

  def test_upgrade_schema_rename_add_remove(self):
    db = self._make_db()
    db.query(b"CREATE TABLE X (a INTEGER, b INTEGER)")
    db.query(b"INSERT INTO X VALUES (1, 2)")
    new_schema = "CREATE TABLE X (a INTEGER, c INTEGER, d INTEGER)"

    self.assertTrue(db.upgradeSchema(new_schema, src__=1))
    db.upgradeSchema(new_schema)

    self.assertFalse(db.upgradeSchema(new_schema, src__=1))
    _, rows = db.query(b"SELECT a FROM X")
    self.assertEqual(rows[0][0], 1)
    self.assertEqual({c['Name'] for c in db.columns('X')}, {'a', 'c', 'd'})

  def test_upgrade_schema_survives_leftover_probe_table(self):
    db = self._make_db()
    db.query(b"CREATE TABLE X (a INTEGER, b INTEGER)")
    db.query(b"INSERT INTO X VALUES (1, 2)")
    # a probe table left behind by a run that died before its own drop
    db.query(b"CREATE TABLE _X_new (garbage INTEGER)")
    db.upgradeSchema("CREATE TABLE X (a INTEGER, c INTEGER)")
    self.assertEqual({c['Name'] for c in db.columns('X')}, {'a', 'c'})

  def test_upgrade_schema_create_if_not_exists(self):
    db = self._make_db()
    create_sql = "CREATE TABLE Y (a INTEGER)"
    self.assertEqual(
      db.upgradeSchema(create_sql, create_if_not_exists=True), create_sql)
    self.assertIn('Y', [t['TABLE_NAME'] for t in db.tables()])

  def test_reconnect_on_broken_handle(self):
    db = self._make_db()
    db.query(b"CREATE TABLE r (a INTEGER)")
    db.query(b"INSERT INTO r VALUES (42)")

    class _FakeCursor:
      def execute(self, *args, **kw):
        error = sqlite3.OperationalError("unable to open database file")
        error.sqlite_errorcode = sqlite3.SQLITE_CANTOPEN
        raise error

      def close(self):
        pass

    class _ConnProxy:
      def __init__(self, real):
        self._real = real
        self.fail = True

      def cursor(self):
        if self.fail:
          self.fail = False
          return _FakeCursor()
        return self._real.cursor()

      def __getattr__(self, name):
        return getattr(self._real, name)

    db.db = _ConnProxy(db.db)

    calls = []
    original_force = db._forceReconnection

    def counting_force():
      calls.append(1)
      original_force()

    db._forceReconnection = counting_force

    _, rows = db.query(b"SELECT a FROM r")
    self.assertEqual(calls, [1])
    self.assertEqual(rows[0][0], 42)


@skipUnlessSQLite
class TestSQLiteDeferredConnection(ERP5TypeTestCase):

  def _make_deferred_db(self):
    fd, path = tempfile.mkstemp(suffix='.sqlite')
    os.close(fd)
    self.addCleanup(_remove_db, path)
    # Make queued statements harmless should the transaction ever commit them.
    prep = DB('-' + path)
    prep.query(b"CREATE TABLE t (a INTEGER)")
    prep.db.close()
    db = DeferredDB(path)
    self.addCleanup(_safe_close, db)
    self.addCleanup(self.abort)
    return db

  def test_queues_statements_with_args(self):
    db = self._make_deferred_db()
    db.query(b"INSERT INTO t VALUES (1)")
    self.assertEqual(db._sql_string_list, [(b"INSERT INTO t VALUES (1)", None)])
    db.query("INSERT INTO t VALUES (?)", args=(2,))
    self.assertEqual(len(db._sql_string_list), 2)
    self.assertEqual(db._sql_string_list[1], (b"INSERT INTO t VALUES (?)", (2,)))

  def test_select_is_rejected(self):
    db = self._make_deferred_db()
    self.assertRaises(sqlite3.NotSupportedError, db.query, b"SELECT 1")

  def test_begin_clears_queue(self):
    db = self._make_deferred_db()
    db.query(b"INSERT INTO t VALUES (1)")
    self.assertTrue(db._sql_string_list)
    db._begin()
    self.assertEqual(db._sql_string_list, [])
