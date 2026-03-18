import six
import os
import re
import sqlite3
from sqlite3 import OperationalError
import warnings
from contextlib import contextmanager, nullcontext
from zLOG import LOG, ERROR
from Products.ERP5Type.Timeout import TimeoutReachedError

from App.config import getConfiguration
from Shared.DC.ZRDB.TM import TM
from DateTime import DateTime
from ZODB.POSException import ConflictError
import time
import unicodedata


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
        self._kw_args = {'db': raw}

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    _p_oid = _p_changed = _registered = None

    def __del__(self):
        if self.db is not None:
            try:
                self.db.close()
            except Exception:
                pass

    def _forceReconnection(self):
        if self.db is not None:
            try:
                self.db.close()
            except Exception:
                pass

        self.db = sqlite3.connect(
            self._kw_args['db'],
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES # XXXXXX need to change also related column
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
        cursor = self.db.execute("PRAGMA table_info('%s')" % table_name)
        result = []
        for cid, name, col_type, notnull, default, pk in cursor.fetchall():
            result.append({
                'Name': name,
                'Type': col_type,
                'Nullable': not notnull,
                'Default': default,
                'PrimaryKey': bool(pk),
            })
        return result

    # ------------------------------------------------------------------
    # Low-level query
    # ------------------------------------------------------------------

    def _query(self, query, allow_reconnect=False):
        try:
            cursor = self.db.cursor()
            query = query.decode()
            if query.upper() == "COMMIT":
                self.db.commit()
                return
            elif query.upper() == "ROLLBACK":
                self.db.rollback()
                return
            else:
                if 'create table' in query.lower():
                    cursor.executescript(query)
                else:
                    cursor.execute(query)
                desc = cursor.description
                rows = cursor.fetchall()
                self.db.commit()
                return SQLiteResult(rows, desc)
        except OperationalError as m:
            msg = str(m).lower()
            if "syntax error" in msg:
                raise OperationalError(f"{m}: {query}")
            if "locked" in msg:
                raise ConflictError(f"{m}: {query}")
            if "timeout" in msg or "busy" in msg:
                raise TimeoutReachedError(f"{m}: {query}")
            if allow_reconnect:
                self._forceReconnection()
                return self._query(query, allow_reconnect=False)
            else:
                LOG('SQLITEDA', ERROR, f'query failed: {query}')
                raise
        except Exception as m:
            if allow_reconnect:
                self._forceReconnection()
                return self._query(query, allow_reconnect=False)
            else:
                LOG('SQLITEDA', ERROR, f'query failed: {query}')
                raise
        finally:
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
            if self._transactions:
                self._query(b"BEGIN", allow_reconnect=True)
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
        if self._transactions:
            self._query(b"COMMIT")

    def _abort(self, *ignored):
        if not self._transaction_begun:
            return
        self._transaction_begun = False
        try:
            if self._transactions:
                self._query(b"ROLLBACK")
            else:
                LOG('SQLiteDA', ERROR, "aborting when non-transactional")
        except OperationalError as m:
            LOG('SQLiteDA', ERROR, "exception during _abort",
                error=True)

    def getMaxAllowedPacket(self):
        return 4 * 1024 * 1024

    @contextmanager
    def lock(self):
        yield

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