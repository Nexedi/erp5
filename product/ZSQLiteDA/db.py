import six
import os
import re
import sqlite3
import threading
from sqlite3 import OperationalError
import warnings
from contextlib import contextmanager

try:
    from contextlib import nullcontext
except ImportError:
    @contextmanager
    def nullcontext():
        yield

from zLOG import LOG, ERROR
from Products.ERP5Type.Timeout import TimeoutReachedError

from App.config import getConfiguration
from Shared.DC.ZRDB.TM import TM
from DateTime import DateTime
from ZODB.POSException import ConflictError
import time
import unicodedata

_icon_xlate = {
    'int': 'int', 'integer': 'int', 'smallint': 'int', 'bigint': 'int',
    'real': 'float', 'float': 'float', 'double': 'float', 'numeric': 'float', 'decimal': 'float',
    'text': 'text', 'varchar': 'text', 'char': 'text', 'clob': 'text',
    'blob': 'bin',
    'date': 'date', 'datetime': 'datetime', 'timestamp': 'datetime', 'time': 'time',
}

# ---------------------------------------------------------------------------
# Type converters
# ---------------------------------------------------------------------------

def DATETIME_to_DateTime_or_None(s):
    try:
        date, time_part = s.split(' ')
        year, month, day = date.split('-')
        hour, minute, second = time_part.split(':')
        return DateTime(
            int(year), int(month), int(day),
            int(hour), int(minute), float(second),
            'UTC',
        )
    except Exception:
        return None


def DATE_to_DateTime_or_None(s):
    try:
        year, month, day = s.split('-')
        return DateTime(int(year), int(month), int(day), 0, 0, 0, 'UTC')
    except Exception:
        return None


def ord_or_None(s):
    if s is not None:
        return ord(s)


match_select = re.compile(
    br'(?:SET\s+STATEMENT\s+(.+?)\s+FOR\s+)?SELECT\s+(.+)',
    re.IGNORECASE | re.DOTALL,
).match


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
                    # Date/datetime conversion by column name heuristic
                    if col_name.endswith('date') and isinstance(val, str):
                        if ' ' in val:
                            val = DATETIME_to_DateTime_or_None(val)
                        else:
                            val = DATE_to_DateTime_or_None(val)
                    else:
                        if isinstance(val, str):
                            val = val.replace('\\0', '\0')
                    # Infer type code for items[]
                    value_type = col_desc[1]
                    if value_type is None:
                        if isinstance(val, bool):
                            value_type = "i"
                        elif isinstance(val, int):
                            value_type = "i"
                        elif isinstance(val, float):
                            value_type = "n"
                        elif isinstance(val, DateTime):
                            value_type = "d"
                        else:
                            value_type = "t"
                        col_desc[1] = value_type
                    new_row.append(val)
                self._rows.append(tuple(new_row))

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


# ---------------------------------------------------------------------------
# Shared sqlite3 connections
#
# SQLite allows only one writer at a time per database file. In ERP5, multiple
# Z*DA instances (catalog, activity, deferred, transactionless) each open their
# own sqlite3 connection but point to the same file, which serializes all
# writers through the OS-level write lock. During a long Zope transaction
# (e.g. BT install) the first DA holds the write lock for tens of seconds,
# and any other DA trying to BEGIN IMMEDIATE times out.
#
# Workaround: cache a single sqlite3.Connection per file path and share it
# across DB instances. Transaction boundaries are coordinated with a refcount:
# the first participant issues BEGIN IMMEDIATE; the last issues COMMIT (or
# ROLLBACK if any participant aborted). Transactionless DAs (connection string
# prefixed with '-') keep their own connection so their writes auto-commit
# independently.
# ---------------------------------------------------------------------------

_shared_connections = {}
_shared_connections_lock = threading.Lock()


def _classify_txn_statement(query):
    """If `query` is a standalone transaction-control statement, return one of
    'BEGIN', 'COMMIT', 'ROLLBACK'. Otherwise return None. Strips SQL line
    comments and is case-insensitive.
    """
    cleaned = []
    for line in query.split('\n'):
        idx = line.find('--')
        if idx >= 0:
            line = line[:idx]
        cleaned.append(line)
    s = ' '.join(cleaned).strip().rstrip(';').strip()
    if not s:
        return None
    tokens = s.upper().split()
    if not tokens:
        return None
    head = tokens[0]
    if head == 'COMMIT' and (len(tokens) == 1 or tokens[1:] in (['WORK'], ['TRANSACTION'])):
        return 'COMMIT'
    if head == 'ROLLBACK' and (len(tokens) == 1 or tokens[1:] in (['WORK'], ['TRANSACTION'])):
        return 'ROLLBACK'
    if head == 'BEGIN' and (len(tokens) == 1
            or tokens[1] in ('IMMEDIATE', 'EXCLUSIVE', 'DEFERRED', 'TRANSACTION', 'WORK')):
        return 'BEGIN'
    return None


class _SharedSQLiteConnection:
    """Wraps a sqlite3.Connection shared by multiple DB instances pointing to
    the same database file. Reference-counts transaction state so that only
    one BEGIN/COMMIT cycle is issued per Zope transaction across all
    participants.
    """

    def __init__(self, path, setup):
        self.path = path
        self.conn = sqlite3.connect(
            path,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES,
            isolation_level=None,
            timeout=60,
        )
        setup(self.conn)
        self.state_lock = threading.RLock()
        self.refcount = 0
        self.aborted = False
        self._savepoint_counter = 0
        self._savepoint_stack = []

    def _exec(self, sql):
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
        finally:
            cursor.close()

    def enter(self):
        """Begin a new (possibly nested) transaction scope.

        Outermost scope opens a real SQLite transaction; nested scopes use
        SAVEPOINT. Returns True if a new SAVEPOINT was pushed (nested case),
        False if this opened the outer transaction.
        """
        with self.state_lock:
            if self.refcount == 0:
                self._exec("BEGIN IMMEDIATE")
                self.aborted = False
                self.refcount = 1
                return False
            self._savepoint_counter += 1
            name = "_sp_%d" % self._savepoint_counter
            self._savepoint_stack.append(name)
            self._exec("SAVEPOINT %s" % name)
            self.refcount += 1
            return True

    def exit_commit(self):
        """Close the most recently opened transaction scope successfully.

        At refcount 1, COMMIT (or ROLLBACK if any participant aborted).
        Otherwise RELEASE the most recent SAVEPOINT.
        """
        with self.state_lock:
            if self.refcount == 0:
                return
            if self.refcount > 1 and self._savepoint_stack:
                name = self._savepoint_stack.pop()
                self._exec("RELEASE SAVEPOINT %s" % name)
                self.refcount -= 1
                return
            # Outermost
            self._exec("ROLLBACK" if self.aborted else "COMMIT")
            self.refcount = 0
            self.aborted = False
            del self._savepoint_stack[:]

    def exit_rollback(self, propagate):
        """Close the most recently opened transaction scope unsuccessfully.

        `propagate` distinguishes outer aborts (from Zope TM, in which case
        the outer transaction must roll back even if other DA participants
        try to commit later) from inner rollbacks (from explicit SQL
        ROLLBACK statements, which only roll back the inner block).
        """
        with self.state_lock:
            if self.refcount == 0:
                return
            if self.refcount > 1 and self._savepoint_stack:
                # Inner scope: ROLLBACK TO + RELEASE SAVEPOINT only.
                name = self._savepoint_stack.pop()
                self._exec("ROLLBACK TO SAVEPOINT %s" % name)
                self._exec("RELEASE SAVEPOINT %s" % name)
                self.refcount -= 1
                if propagate:
                    self.aborted = True
                return
            # Outermost
            self._exec("ROLLBACK")
            self.refcount = 0
            self.aborted = False
            del self._savepoint_stack[:]


def _get_shared_connection(path, setup):
    abs_path = os.path.abspath(path)
    with _shared_connections_lock:
        entry = _shared_connections.get(abs_path)
        if entry is None:
            entry = _SharedSQLiteConnection(abs_path, setup)
            _shared_connections[abs_path] = entry
        return entry


class DB(TM):
    _sort_key = TM._sort_key
    db = None
    _transaction_begun = False

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

    _p_oid = _p_changed = _registered = None

    def __del__(self):
        # Do not close self.db here: it is a shared sqlite3.Connection owned
        # by the module-level cache and used by other DB instances. Closing
        # it would break the other participants. The cache holds the
        # connection alive for the process lifetime, which is the correct
        # behavior for the test runner.
        pass

    def _forceReconnection(self):
        def setup(conn):
            conn.create_collation("utf8mb4_general_ci", utf8mb4_general_ci)

            def subdate(date_str, days):
                if date_str.lower() in ('current_date', 'now'):
                    dt = DateTime()
                else:
                    dt = DateTime(date_str)
                dt -= days
                return dt.earliestTime().strftime("%Y-%m-%d %H:%M:%S")

            conn.create_function("SLEEP", 1, lambda x: time.sleep(x) or 0)
            conn.create_function("SUBDATE", 2, subdate)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=60000")

        # All DAs (transactional and transactionless) pointing to the same
        # SQLite file share a single sqlite3.Connection. SQLite allows only
        # one writer per file, so giving each DA its own connection just
        # serializes them through the OS-level write lock — and any DA
        # holding BEGIN IMMEDIATE for the duration of a Zope transaction
        # would block the others past busy_timeout. With a shared connection,
        # transactionless writes piggyback on the currently open transaction
        # (if any) or auto-commit when no transaction is open.
        self._shared = _get_shared_connection(self._kw_args['db'], setup)
        self.db = self._shared.conn

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
        cursor = self.db.execute("PRAGMA table_info('%s')" % table_name)
        result = []
        for cid, name, col_type, notnull, default, pk in cursor.fetchall():
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

    def _query(self, query, allow_reconnect=False):
        cursor = None
        try:
            cursor = self.db.cursor()
            if isinstance(query, bytes):
                query = query.decode()

            txn_stmt = _classify_txn_statement(query)
            # Route explicit BEGIN/COMMIT/ROLLBACK statements (e.g. from
            # DB.lock(), SQLBase's "reserve duplicates" block, or
            # IdTool_zGenerateId) through the shared connection's enter/
            # exit_commit/exit_rollback so that transaction state stays
            # consistent with refcount: the outermost BEGIN opens a real
            # SQLite transaction, while nested BEGINs use SAVEPOINTs.
            if txn_stmt == "BEGIN":
                if self._shared is not None:
                    self._shared.enter()
                else:
                    cursor.execute("BEGIN IMMEDIATE")
                return
            if txn_stmt == "COMMIT":
                if self._shared is not None:
                    self._shared.exit_commit()
                else:
                    self.db.commit()
                return
            if txn_stmt == "ROLLBACK":
                if self._shared is not None:
                    self._shared.exit_rollback(propagate=False)
                else:
                    self.db.rollback()
                return
            else:
                # cursor.execute() only accepts a single SQL statement. Some Z
                # SQL methods (e.g. z_create_category, z_drop_*) bundle several
                # DDL statements together without the '\0' delimiter. Run the
                # whole thing first; only if SQLite complains that there are
                # multiple statements do we split on ';'. We can't use
                # executescript() because it implicitly commits the current
                # transaction (breaking the shared-transaction refcount).
                try:
                    cursor.execute(query)
                except sqlite3.ProgrammingError as e:
                    if 'one statement at a time' not in str(e):
                        raise
                    for statement in query.split(';'):
                        statement = statement.strip()
                        if statement:
                            cursor.execute(statement)
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
            if allow_reconnect:
                self._forceReconnection()
                return self._query(query, allow_reconnect=False)
            else:
                LOG('SQLITEDA', ERROR, 'query failed: %s' % query)
                raise
        except Exception as m:
            if allow_reconnect:
                self._forceReconnection()
                return self._query(query, allow_reconnect=False)
            else:
                LOG('SQLITEDA', ERROR, 'query failed: %s' % query)
                raise
        finally:
            if cursor is not None:
                cursor.close()

    def query(self, query_string, max_rows=1000):
        """Execute query_string and return at most max_rows."""
        self._use_TM and self._register()
        desc = None
        result = ()

        if isinstance(query_string, six.text_type):
            query_string = query_string.encode('utf-8')
        if query_string[-1:] == b';':
            query_string = query_string[:-1]

        for qs in query_string.split(b'\0'):
            qs = qs.strip()
            if not qs:
                continue
            select_match = match_select(qs)
            if select_match:
                _, select = select_match.groups()
                qs = b"SELECT %s" % select
                if max_rows:
                    qs = b"%s LIMIT %d" % (qs, max_rows)

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

    def _begin(self, *ignored):
        try:
            self._transaction_begun = True
            if self._transactions and self._shared is not None:
                self._shared.enter()
        except:
            LOG('SQLiteDA', ERROR, "exception during _begin",
                error=True)
            raise

    def tpc_vote(self, *ignored):
        self._query(b"SELECT 1")
        return TM.tpc_vote(self, *ignored)

    def _finish(self, *ignored):
        if not self._transaction_begun:
            return
        self._transaction_begun = False
        if self._transactions and self._shared is not None:
            self._shared.exit_commit()

    def _abort(self, *ignored):
        if not self._transaction_begun:
            return
        self._transaction_begun = False
        try:
            if self._transactions and self._shared is not None:
                self._shared.exit_rollback(propagate=True)
            elif not self._transactions:
                LOG('SQLiteDA', ERROR, "aborting when non-transactional")
        except OperationalError as m:
            LOG('SQLiteDA', ERROR, "exception during _abort",
                error=True)

    def getMaxAllowedPacket(self):
        return 4 * 1024 * 1024

    @contextmanager
    def lock(self):
        try:
            self._query("BEGIN EXCLUSIVE")
            yield
        except Exception:
            self._query("ROLLBACK")
            raise
        else:
            self._query("COMMIT")

    def _getTableSchema(self, name,
            create_lstrip=re.compile(r"[^(]+\(\s*").sub,
            create_rmatch=re.compile(r"(.*\S)\s*\)\s*(.*)$", re.DOTALL).match,
            create_split=re.compile(r",\n\s*").split,
            column_match=re.compile(r"`(\w+)`\s+(.+)").match,
            ):
        result = self.query(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='%s'" % name
        )[1]
        if not result:
            raise OperationalError("no such table: %s" % name)

        col_result = self.query("PRAGMA table_info(%s)" % name)[1]
        columns = [(r[1], r[2]) for r in col_result]

        idx_result = self.query("PRAGMA index_list(%s)" % name)[1]
        key_set = set(r[1] for r in idx_result)

        return columns, key_set, ""

    _create_search = re.compile(
        r'\bCREATE\s+TABLE\s+(`?)(\w+)\1\s+', re.I
    ).search
    _key_search = re.compile(r'\bKEY\s+(`[^`]+`)\s+(.+)').search

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

            src_sql = ";\n".join(migration)

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

    def query(self, query_string, max_rows=1000):
        self._register()
        if isinstance(query_string, six.text_type):
            query_string = query_string.encode('utf-8')
        for qs in query_string.split(b'\0'):
            qs = qs.strip()
            if qs:
                if match_select(qs):
                    raise sqlite3.NotSupportedError(
                        "can not SELECT in deferred connections")
                self._sql_string_list.append(qs)
        return (), ()

    def _begin(self, *ignored):
        del self._sql_string_list[:]

    def _finish(self, *ignored):
        if self._sql_string_list:
            DB._begin(self)
            for qs in self._sql_string_list:
                self._query(qs)
            del self._sql_string_list[:]
            DB._finish(self)

    tpc_vote = TM.tpc_vote
    _abort = _begin