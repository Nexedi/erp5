import six
import re
import sqlite3
import threading
from sqlite3 import OperationalError
from contextlib import contextmanager

try:
    from contextlib import nullcontext
except ImportError:
    @contextmanager
    def nullcontext():
        yield

from zLOG import LOG, ERROR
from Products.ERP5Type.Timeout import TimeoutReachedError

from Shared.DC.ZRDB.TM import TM
from DateTime import DateTime
from ..db import BaseDB, DATETIME_to_DateTime_or_None, DATE_to_DateTime_or_None, match_select
from ZODB.POSException import ConflictError
import time
import unicodedata
from datetime import datetime as stdlib_datetime, date as stdlib_date
from App.special_dtml import HTMLFile
from .. import DA

database_type = 'SQLite'

# Primary SQLite result codes that mean the connection/handle is broken (as
# opposed to a query error), for which _query retries once after reconnecting.
# Compared against the primary code (sqlite_errorcode & 0xFF) so extended
# variants (e.g. the many SQLITE_IOERR_*) are covered too.
_connection_lost_codes = frozenset((
    sqlite3.SQLITE_CANTOPEN,
    sqlite3.SQLITE_IOERR,
))

_icon_xlate = {
    'int': 'int', 'integer': 'int', 'smallint': 'int', 'bigint': 'int',
    'real': 'float', 'float': 'float', 'double': 'float', 'numeric': 'float', 'decimal': 'float',
    'text': 'text', 'varchar': 'text', 'char': 'text', 'clob': 'text',
    'blob': 'bin',
    'date': 'date', 'datetime': 'datetime', 'timestamp': 'datetime', 'time': 'time',
}

_trailing_limit_search = re.compile(br'\bLIMIT\b[^()]*$', re.I).search

_file_lock_registry = {}
_file_lock_registry_guard = threading.Lock()

def _get_file_lock(path):
    with _file_lock_registry_guard:
        file_lock = _file_lock_registry.get(path)
        if file_lock is None:
            file_lock = _file_lock_registry[path] = threading.RLock()
        return file_lock

# ---------------------------------------------------------------------------
# UTF-8 collation (approximates utf8mb4_general_ci)
# ---------------------------------------------------------------------------

def utf8mb4_general_ci(a, b):
    def normalize(text):
        if text is None:
            return ""
        if not isinstance(text, str):
            text = str(text)
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))
        return text.casefold()
    na, nb = normalize(a), normalize(b)
    return (na > nb) - (na < nb)


class SQLiteResult:
    def __init__(self, rows, description):
        _rows = rows or []
        description = [list(col) for col in description] if description else description
        self._index = 0
        self._rows = []

        if _rows and description:
            for row in _rows:
                new_row = []
                for val, col_desc in zip(row, description):
                    col_name = col_desc[0]
                    lowered = col_name.lower()
                    if isinstance(val, stdlib_datetime):
                        val = DateTime(val.year, val.month, val.day,
                                       val.hour, val.minute,
                                       val.second + val.microsecond / 1e6,
                                       'UTC')
                    elif isinstance(val, stdlib_date):
                        val = DateTime(val.year, val.month, val.day,
                                       0, 0, 0, 'UTC')
                    elif isinstance(val, str):
                        if lowered == 'date' or lowered.endswith('_date'):
                            converted = (DATETIME_to_DateTime_or_None(val)
                                         if ' ' in val
                                         else DATE_to_DateTime_or_None(val))
                            val = converted if converted is not None \
                                else val.replace('\\0', '\0')
                        else:
                            val = val.replace('\\0', '\0')
                    # Infer type code for items[] from the first non-NULL value
                    if col_desc[1] is None and val is not None:
                        if isinstance(val, (bool, int)):
                            col_desc[1] = "i"
                        elif isinstance(val, float):
                            col_desc[1] = "n"
                        elif isinstance(val, DateTime):
                            col_desc[1] = "d"
                        else:
                            col_desc[1] = "t"
                    new_row.append(val)
                self._rows.append(tuple(new_row))

        if description:
            for col_desc in description:
                if col_desc[1] is None:
                    col_desc[1] = "t"

        self._description = [tuple(col) for col in description] if description else description

    def fetch_row(self, size=1):
        if self._index >= len(self._rows):
            return ()
        if size in (0, None):
            result = self._rows[self._index:]
            self._index = len(self._rows)
            return tuple(result)
        end = self._index + size
        chunk = self._rows[self._index:end]
        self._index = end
        return tuple(chunk)

    def describe(self):
        return self._description

    def num_rows(self):
        return len(self._rows)

    def eof(self):
        return self._index >= len(self._rows)

    def fetchall(self):
        return self._rows

class DB(BaseDB):
    def __init__(self, connection):
        self._connection = connection
        self._parse_connection_string()
        self._forceReconnection()

        transactional = 1
        if self._try_transactions == '-':
            transactional = 0
        elif self._try_transactions == '+':
            transactional = 1

        self._transactions = transactional
        self._use_TM = transactional

    # ------------------------------------------------------------------
    # Connection string
    # ------------------------------------------------------------------

    def _parse_connection_string(self):
        self._try_transactions = None
        raw = self._connection.strip()
        if raw and raw[0] in '+-':
            self._try_transactions = raw[0]
            raw = raw[1:]
        self._kw_args = {'db': raw.split('@')[0]}

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    def _forceReconnection(self):
        if self.db is not None:
            try:
                self.db.close()
            except Exception:
                pass

        self.db = sqlite3.connect(
            self._kw_args['db'],
            check_same_thread=False,
            # XXXX
            # sqlite is file level lock, we can have multi write query
            # _begin  --> file level lock
            # insert  --> ok
            # insert in other thread --> raise database is locked when timeout is passed
            isolation_level=None,
            detect_types=sqlite3.PARSE_DECLTYPES 
        )

        self.db.create_collation("utf8mb4_general_ci", utf8mb4_general_ci)

        def subdate(date_str, days):
            if date_str.lower() in ('current_date', 'now'):
                dt = DateTime()
            else:
                dt = DateTime(date_str)
            dt -= days
            return dt.earliestTime().strftime("%Y-%m-%d %H:%M:%S")

        self.db.create_function("SLEEP", 1, lambda x: time.sleep(x) or 0)
        self.db.create_function("SUBDATE", 2, subdate)

        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA busy_timeout=10000")

    # ------------------------------------------------------------------
    # Schema inspection
    # ------------------------------------------------------------------

    def tables(self, rdb=0, _care=('TABLE', 'VIEW')):
        r = []
        result = self._query(b"SELECT name FROM sqlite_master WHERE type='table'")
        row = result.fetch_row(1)
        while row:
            r.append({'TABLE_NAME': row[0][0], 'TABLE_TYPE': 'TABLE'})
            row = result.fetch_row(1)
        return r

    def columns(self, table_name):
        result = []
        try:
            c = self._query("SELECT * FROM pragma_table_info(?)", args=(table_name,))
        except Exception:
            return result

        for cid, name, col_type, notnull, default, pk in c.fetch_row(0):
            short_type = col_type.lower().split('(')[0].strip()
            icon = _icon_xlate.get(short_type, 'what')
            result.append({
                'Name': name,
                'Type': col_type,
                'Nullable': not notnull,
                'Default': default,
                'PrimaryKey': bool(pk),
                'Icon': icon,
                'Description': col_type,
            })
        return result

    # ------------------------------------------------------------------
    # Low-level query
    # ------------------------------------------------------------------

    def _query(self, query, args=None, allow_reconnect=False):
        cursor = None
        try:
            cursor = self.db.cursor()
            if isinstance(query, bytes):
                query = query.decode()

            upper = query.strip().upper()
            # we can have single query like "COMMIT" OR "ROLLBACK" with no open transaction
            # use db can correctly handle such case
            if upper == "COMMIT":
                self.db.commit()
                return
            if upper == "ROLLBACK":
                self.db.rollback()
                return

            if args:
                cursor.execute(query, args)
            else:
                cursor.execute(query)
            desc = cursor.description
            rows = cursor.fetchall()
            return SQLiteResult(rows, desc)
        except OperationalError as m:
            msg = str(m).lower()
            if "syntax error" in msg:
                raise OperationalError("%s: %s" % (m, query))
            if "locked" in msg:
                raise ConflictError("%s: %s" % (m, query))
            if "timeout" in msg or "busy" in msg:
                raise TimeoutReachedError("%s: %s" % (m, query))
            code = getattr(m, "sqlite_errorcode", None)
            if (allow_reconnect or not self._use_TM) and code is not None \
                    and code & 0xFF in _connection_lost_codes:
                self._forceReconnection()
                return self._query(query, args=args, allow_reconnect=False)
            LOG('ZSQLDA.SQLite', ERROR, 'query failed: %s' % query)
            raise
        except Exception:
            LOG('ZSQLDA.SQLite', ERROR, 'query failed: %s' % query)
            raise
        finally:
            if cursor is not None:
                cursor.close()



    def _apply_max_rows(self, qs, max_rows):
        if not max_rows:
            return qs
        if _trailing_limit_search(qs):
            return b"SELECT * FROM (%s) LIMIT %d" % (qs, max_rows)
        return b"%s LIMIT %d" % (qs, max_rows)

    def query(self, query_string, max_rows=1000, args=None):
        """Execute query_string and return at most max_rows.

        If args is provided, query_string must be a single statement using `?`
        placeholders; sqlite3 binds the values. Mixing args with the `\\0`
        multi-statement separator is not supported.
        """
        self._use_TM and self._register()
        desc = None
        result = ()

        if isinstance(query_string, six.text_type):
            query_string = query_string.encode('utf-8')
        if query_string[-1:] == b';':
            query_string = query_string[:-1]

        if args:
            assert b'\0' not in query_string, (
                "parameter-bound query cannot contain \\0 separator: %r"
                % query_string)
            qs = query_string.strip()
            select_match = match_select(qs)
            if select_match:
                _, select = select_match.groups()
                qs = self._apply_max_rows(b"SELECT %s" % select, max_rows)
            c = self._query(qs, args=args)
            if c:
                desc = c.describe()
                result = c.fetch_row(max_rows)
        else:
            for qs in query_string.split(b'\0'):
                qs = qs.strip()
                if not qs:
                    continue
                select_match = match_select(qs)
                if select_match:
                    _, select = select_match.groups()
                    qs = self._apply_max_rows(b"SELECT %s" % select, max_rows)

                c = self._query(qs)
                if c:
                    if desc is not None and c.describe() is not None:
                        raise Exception('Multiple select schema are not allowed')
                    desc = c.describe()
                    result = c.fetch_row(max_rows)

        if desc is None:
            return (), ()

        items = [
            {
                'name': d[0],
                'type': d[1],
                'width': d[2],   # always None in sqlite3, harmless
                'null': d[6],    # always None in sqlite3, harmless
            }
            for d in desc
        ]
        return items, result

    # ------------------------------------------------------------------
    # String escaping
    # ------------------------------------------------------------------

    def string_literal(self, s):
        """Produce a SQLite-safe quoted string literal."""
        if s is None:
            return b'NULL'
        if isinstance(s, bytes):
            # Store raw bytes as hex blob literal
            return b"x'" + s.hex().encode('ascii') + b"'"
        if not isinstance(s, str):
            s = str(s)
        return ("'" + s.replace('\0', '\\0').replace("'", "''") + "'").encode('utf-8')

    # ------------------------------------------------------------------
    # Transaction management
    # ------------------------------------------------------------------

    # No _begin/_finish/_abort overrides: the general path runs in SQLite
    # isolation_level=None, so TM's defaults suffice
    def tpc_vote(self, *ignored):
        self._query(b"SELECT 1")
        return TM.tpc_vote(self, *ignored)

    @contextmanager
    def lock(self):
        # Can't do query way, because it's file level locked
        # we can have database is locked error
        file_lock = _get_file_lock(self._kw_args['db'])
        file_lock.acquire()
        try:
            yield
        finally:
            file_lock.release()

    def _getTableSchema(self, name, *args, **kw):
        result = self.query(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", args=(name,)
        )[1]
        if not result:
            raise OperationalError("no such table: %s" % name)

        col_result = self.query("SELECT * FROM pragma_table_info(?)", args=(name,))[1]
        columns = [(r[1], r[2]) for r in col_result]

        # key_set (PRAGMA index_list) is unused by upgradeSchema, so skip the
        # query; the empty set keeps the (columns, key_set, default) shape.
        return columns, set(), ""

    _create_search = re.compile(
        r'\bCREATE\s+TABLE\s+(`?)(\w+)\1\s+', re.I
    ).search

    def upgradeSchema(self, create_sql, create_if_not_exists=False,
                      initialize=None, src__=0):
        m = self._create_search(create_sql)
        if m is None:
            return

        name = m.group(2)
        new_name = "_%s_new" % name

        with (nullcontext() if src__ else self.lock()):
            try:
                old_list, _, _ = self._getTableSchema(name)
            except OperationalError as e:
                if "no such table" not in str(e).lower() or not create_if_not_exists:
                    raise
                if not src__:
                    self.query(create_sql)
                return create_sql

            old_cols = {c for c, _ in old_list}

            # Probe new schema via a temporary table then drop it immediately
            self.query("DROP TABLE IF EXISTS %s" % new_name)
            self.query("CREATE TABLE %s %s" % (new_name, create_sql[m.end():]))
            try:
                new_list, _, _ = self._getTableSchema(new_name)
            except Exception:
                self.query("DROP TABLE IF EXISTS %s" % new_name)
                raise
            self.query("DROP TABLE %s" % new_name)

            # Compare old vs new
            changed = (len(new_list) != len(old_list)) or any(
                new_list[i] != old_list[i] for i in range(len(new_list))
            )

            if not changed:
                return

            # Build migration statements
            new_cols = [c for c, _ in new_list if c in old_cols]
            col_sql = ", ".join('"%s"' % c for c in new_cols)

            migration = [
                "CREATE TABLE %s %s" % (new_name, create_sql[m.end():]),
            ]
            if new_cols:
                migration.append(
                    "INSERT INTO %s (%s) SELECT %s FROM %s"
                    % (new_name, col_sql, col_sql, name)
                )
            migration += [
                "DROP TABLE %s" % name,
                "ALTER TABLE %s RENAME TO %s" % (new_name, name),
            ]

            src_sql = "\0".join(migration)

            if src__:
                return src_sql

            for stmt in migration:
                self.query(stmt)

            if initialize:
                added = [c for c, _ in new_list if c not in old_cols]
                if added:
                    initialize(self, added)

            return src_sql


class DeferredDB(DB):
    def __init__(self, *args, **kw):
        DB.__init__(self, *args, **kw)
        assert self._use_TM
        self._sql_string_list = []

    def query(self, query_string, max_rows=1000, args=None):
        self._register()
        if isinstance(query_string, six.text_type):
            query_string = query_string.encode('utf-8')
        if args:
            assert b'\0' not in query_string, (
                "parameter-bound query cannot contain \\0 separator: %r"
                % query_string)
            qs = query_string.strip()
            if qs:
                if match_select(qs):
                    raise sqlite3.NotSupportedError(
                        "can not SELECT in deferred connections")
                self._sql_string_list.append((qs, args))
        else:
            for qs in query_string.split(b'\0'):
                qs = qs.strip()
                if qs:
                    if match_select(qs):
                        raise sqlite3.NotSupportedError(
                            "can not SELECT in deferred connections")
                    self._sql_string_list.append((qs, None))
        return (), ()

    def _begin(self, *ignored):
        del self._sql_string_list[:]

    def _finish(self, *ignored):
        if self._sql_string_list:
            DB._begin(self)
            for qs, qargs in self._sql_string_list:
                self._query(qs, args=qargs)
            del self._sql_string_list[:]
            DB._finish(self)

    tpc_vote = TM.tpc_vote
    _abort = _begin

class Connection(DA.BaseConnection):
    """SQLite Connection Object"""
    database_type = database_type

    def factory(self):
        return DB


class DeferredConnection(Connection):
    """Experimental DA which implements deferred SQL code execution to reduce
    locking issues.
    """
    deferred = True

    def factory(self):
        return DeferredDB


manage_addZSQLiteConnectionForm = HTMLFile(
    'connectionAdd', globals(), __name__='connectionAdd_sqlite')


def manage_addZSQLiteConnection(self, id, title, connection_string,
                                check=None, deferred=False, REQUEST=None):
    """Add a Z SQLite Database Connection to a folder."""
    return DA.manage_addConnection(
        self, Connection, DeferredConnection,
        id, title, connection_string, check, deferred, REQUEST)


__ac_permissions__ = (
    ('Add Z SQLite Database Connections',
     ('manage_addZSQLiteConnectionForm',
      'manage_addZSQLiteConnection')),
)