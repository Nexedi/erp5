import six
import os
import re
import MySQLdb
from MySQLdb import OperationalError, NotSupportedError, ProgrammingError, _mysql
import sqlite3
import warnings
from contextlib import contextmanager
from zLOG import LOG
if six.PY2:
    @contextmanager
    def nullcontext():
        yield
else:
  from contextlib import nullcontext
from Products.ERP5Type.Timeout import TimeoutReachedError, getTimeLeft

from MySQLdb.converters import conversions
from MySQLdb.constants import FIELD_TYPE, CR, ER, CLIENT
from App.config import getConfiguration
from Shared.DC.ZRDB.TM import TM
from DateTime import DateTime
from zLOG import LOG, ERROR, WARNING
from ZODB.POSException import ConflictError
import time
from sqlite3 import OperationalError

hosed_connection = (
    CR.SERVER_GONE_ERROR,
    CR.SERVER_LOST,
    CR.COMMANDS_OUT_OF_SYNC,
    1927, # ER_CONNECTION_KILLED "Connection was killed" in MariaDB
    )

query_syntax_error = (
    ER.BAD_FIELD_ERROR,
    )

lock_error = (
    ER.LOCK_WAIT_TIMEOUT,
    ER.LOCK_DEADLOCK,
    )

query_timeout_error = (
    1969, # ER_STATEMENT_TIMEOUT in MariaDB
)

key_types = {
    "PRI": "PRIMARY KEY",
    "MUL": "INDEX",
    "UNI": "UNIQUE",
    }

field_icons = "bin", "date", "datetime", "float", "int", "text", "time"

icon_xlate = {
    "varchar": "text", "char": "text",
    "enum": "what", "set": "what",
    "double": "float", "numeric": "float",
    "blob": "bin", "mediumblob": "bin", "longblob": "bin",
    "tinytext": "text", "mediumtext": "text",
    "longtext": "text", "timestamp": "datetime",
    "decimal": "float", "smallint": "int",
    "mediumint": "int", "bigint": "int",
    }

type_xlate = {
    "double": "float", "numeric": "float",
    "decimal": "float", "smallint": "int",
    "mediumint": "int", "bigint": "int",
    "int": "int", "float": "float",
    "timestamp": "datetime", "datetime": "datetime",
    "time": "datetime",
    }


# DateTime(str) is slow. As the date format is part of the specifications,
# parse it ourselves to save time.
def DATETIME_to_DateTime_or_None(s):
    try:
        date, time = s.split(' ')
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        return DateTime(
            int(year),
            int(month),
            int(day),
            int(hour),
            int(minute),
            float(second),
            'UTC',
        )
    except Exception:
        return None

def DATE_to_DateTime_or_None(s):
    try:
        year, month, day = s.split('-')
        return DateTime(
            int(year),
            int(month),
            int(day),
            0,
            0,
            0,
            'UTC',
        )
    except Exception:
        return None

def ord_or_None(s):
    if s is not None:
        return ord(s)

match_select = re.compile(
    br'(?:SET\s+STATEMENT\s+(.+?)\s+FOR\s+)?SELECT\s+(.+)',
    re.IGNORECASE | re.DOTALL,
).match

class SQLiteResult:
    def __init__(self, rows, description):
        _rows = rows or []
        self._description = description
        self._index = 0
        self._rows = []
        if _rows:
            for row in _rows:
                new_row = []
                for val, col_desc in zip(row, self._description):
                    col_name = col_desc[0]
                    if col_name.endswith('date') and isinstance(val, str):
                        if ' ' in val:
                            new_row.append(DATETIME_to_DateTime_or_None(val))
                        else:
                            new_row.append(DATE_to_DateTime_or_None(val))
                    else:
                        if isinstance(val, str):
                            val = val.replace('\\0', '\0')
                        new_row.append(val)

                self._rows.append(tuple(new_row))


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
        """
        MySQL-style describe():
        returns cursor.description-like tuples
        """
        return self._description

    def num_rows(self):
        return len(self._rows)

    def eof(self):
        return self._index >= len(self._rows)

    def fetchall(self):
        return self._rows

class SqliteDB(TM):
    """This is the ZMySQLDA Database Connection Object."""

    conv=conversions.copy()
    _sort_key = TM._sort_key
    db = None

    def __init__(self,connection):
        """
          Parse the connection string.
          Initiate a trial connection with the database to check
          transactionality once instead of once per DB instance.
        """
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

    def _parse_connection_string(self):
        self._mysql_lock = self._try_transactions = None
        self._kw_args = kwargs = {'conv': self.conv}
        items = self._connection.split()
        if not items:
            return
        if items[0][0] == "%":
            cert_base_name = items.pop(0)[1:]
            instancehome = getConfiguration().instancehome
            kwargs['ssl'] = {
              'ca': os.path.join(instancehome, 'etc', 'zmysqlda', cert_base_name + '-ca.pem'),
              'cert': os.path.join(instancehome, 'etc', 'zmysqlda', cert_base_name + '-cert.pem'),
              'key': os.path.join(instancehome, 'etc', 'zmysqlda', cert_base_name + '-key.pem'),
            }
        if items[0] == "~":
            kwargs['compress'] = True
            del items[0]
        if items[0][0] == "*":
            self._mysql_lock = items.pop(0)[1:]
        db = items.pop(0)
        if '@' in db:
            db, host = db.split('@', 1)
            if os.path.isabs(host):
                kwargs['unix_socket'] = host
            else:
                if host.startswith('['):
                    host, port = host[1:].split(']', 1)
                    if port.startswith(':'):
                      kwargs['port'] = int(port[1:])
                elif ':' in host:
                    host, port = host.split(':', 1)
                    kwargs['port'] = int(port)
                kwargs['host'] = host
        if db:
            if db[0] in '+-':
                self._try_transactions = db[0]
                db = db[1:]
            if db:
                kwargs['db'] = db
        if items:
            kwargs['user'] = items.pop(0)
            if items:
                kwargs['passwd'] = items.pop(0)
                if items: # BBB
                    assert 'unix_socket' not in kwargs
                    warnings.warn("use '<db>@<unix_socket> ...' syntax instead",
                                  DeprecationWarning)
                    kwargs['unix_socket'] = items.pop(0)

    defs={
        FIELD_TYPE.CHAR: "i", FIELD_TYPE.DATE: "d",
        FIELD_TYPE.DATETIME: "d", FIELD_TYPE.DECIMAL: "n",
        FIELD_TYPE.DOUBLE: "n", FIELD_TYPE.FLOAT: "n", FIELD_TYPE.INT24: "i",
        FIELD_TYPE.LONG: "i", FIELD_TYPE.LONGLONG: "l",
        FIELD_TYPE.SHORT: "i", FIELD_TYPE.TIMESTAMP: "d",
        FIELD_TYPE.TINY: "i", FIELD_TYPE.YEAR: "i",
        }

    _p_oid=_p_changed=_registered=None

    def __del__(self):
      if self.db is not None:
        self.db.close()

    def _forceReconnection(self):
      db = self.db
      if db is not None:
        try:
          db.close()
        except Exception:
            pass

      self.db = sqlite3.connect(self._connection, check_same_thread=False)
      def subdate(date_str, days):
        if date_str.lower() in ('current_date', 'now'):
            dt = Datetime()
        else:
            dt = DateTime(date_str)
        dt -= days
        return dt.earliestTime().strftime("%Y-%m-%d %H:%M:%S")

      self.db.create_function("SLEEP", 1, lambda x: time.sleep(x) or 0)
      self.db.create_function("SUBDATE", 2, subdate)

      #self.db.execute("PRAGMA journal_mode=WAL")
      #self.db.execute("PRAGMA foreign_keys=ON")


    def tables(self, rdb=0,
               _care=('TABLE', 'VIEW')):
        """Returns a list of tables in the current database."""
        r=[]
        a=r.append
        result = self._query(b"SELECT name FROM sqlite_master WHERE type='table';")
        row = result.fetch_row(1)
        while row:
            a({'TABLE_NAME': row[0][0], 'TABLE_TYPE': 'TABLE'})
            row = result.fetch_row(1)
        return r

    def columns(self, table_name):
        """Column metadata via PRAGMA."""
        cursor = self.db.execute(f"PRAGMA table_info('{table_name}')")

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

    def _query(self, query, allow_reconnect=False, query_value = None):
        try:
            cursor = self.db.cursor()
            query = query.decode()
            # Intercept raw COMMIT / ROLLBACK
            if query.upper() == "COMMIT":
                self.db.commit()
                return
            elif query.upper() == "ROLLBACK":
                self.db.rollback()
                return
            else:
                if query_value:
                    cursor.executemany(query, query_value)
                elif 'create table' in query.lower():
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
                return self._query(query, allow_reconnect=False, query_value = query_value)

            else:
                LOG('SQLITEDA', ERROR, f'query failed: {query}')
                raise

        except ProgrammingError as m:
            if allow_reconnect:
                self._forceReconnection()
                return self._query(query, allow_reconnect=False, query_value = query_value)
            else:
                LOG('SQLITEDA', ERROR, f'query failed: {query}')
                raise
        finally:
            cursor.close()
      
    def query(self, query_string, max_rows=1000, query_value = None):
        """Execute 'query_string' and return at most 'max_rows'."""
        self._use_TM and self._register()
        desc = None
        
        if isinstance(query_string, six.text_type):
            query_string = query_string.encode('utf-8')
        # XXX deal with a typical mistake that the user appends
        # an unnecessary and rather harmful semicolon at the end.
        # Unfortunately, MySQLdb does not want to be graceful.
        if query_string[-1:] == b';':
          query_string = query_string[:-1]

        for qs in query_string.split(b'\0'):
            qs = qs.strip()
            if qs:
                select_match = match_select(qs)
                if select_match:
                    # XXXX statement
                    #query_timeout = getTimeLeft()
                    #if query_timeout is not None:
                    statement, select = select_match.groups()
                    qs = b"SELECT %s" % select

                    if max_rows:
                        qs = b"%s LIMIT %d" % (qs, max_rows)
                        #qs = b"SELECT * FROM (%s) AS t LIMIT %d" % (qs, max_rows)

                c = self._query(qs, query_value = query_value)
                if c:
                    if desc is not None is not c.describe():
                        raise Exception(
                            'Multiple select schema are not allowed'
                            )
                    desc = c.describe()
                    result = c.fetch_row(max_rows)
        if desc is None:
            return (), ()
        get_def = self.defs.get
        items = [{'name': d[0],
                  'type': get_def(d[1], "t"),
                  'width': d[2],
                  'null': d[6]
                 } for d in desc]
        return items, result

    def string_literal(self, s):
        if s is None:
            return b'NULL'
        if isinstance(s, bytes):
            bval = s
        elif isinstance(s, str):
            bval = s.encode()
        else:
            bval = str(s).encode()


        if bval.startswith(b'\x80'):
            return b"x'" + bval.hex().encode("ascii") + b"'"

        tmp = b"'%s'" % (bval
            .replace(b'\\', b'\\\\')
            .replace(b'\0', b'\\0')
            .replace(b'\n', b'\\n')
            .replace(b'\r', b'\\r')
            .replace(b'\32', b'\\Z')
            .replace(b"'", b"\\'")
        )
        return tmp

    def _begin(self, *ignored):
        """Begin a transaction (when TM is enabled)."""
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
        """Commit a transaction (when TM is enabled)."""
        if not self._transaction_begun:
            return
        self._transaction_begun = False
        if self._transactions:
            self._query(b"COMMIT")

    def _abort(self, *ignored):
        """Rollback a transaction (when TM is enabled)."""
        if not self._transaction_begun:
            return
        self._transaction_begun = False
        # Hide hosed connection exceptions:
        # - if the disconnection caused the abort, we would then hide the
        #   original error traceback
        # - if the disconnection happened during abort, then we cannot recover
        #   anyway as the transaction is bound to its connection anyway
        # Note: in any case, we expect server to notice the disconnection and
        # trigger an abort on its side.
        try:
            if self._transactions:
                self._query(b"ROLLBACK")
            else:
                LOG('SQLiteDA', ERROR, "aborting when non-transactional")
        except OperationalError as m:
            LOG('SQLiteDA', ERROR, "exception during _abort",
                error=True)
            if m.args[0] not in hosed_connection:
                raise

    def getMaxAllowedPacket(self):
        return 4 * 1024 * 1024

    @contextmanager
    def lock(self):
        yield

    def _getTableSchema(self, name,
            create_lstrip = re.compile(r"[^(]+\(\s*").sub,
            create_rmatch = re.compile(r"(.*\S)\s*\)\s*(.*)$", re.DOTALL).match,
            create_split  = re.compile(r",\n\s*").split,
            column_match  = re.compile(r"`(\w+)`\s+(.+)").match,
            ):
        #(('CREATE TABLE altered_table (a int)',),)
        result = self.query(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{name}'")[1]
        if not result:
            raise OperationalError("NO SUCH TABLE")


        col_query = f"PRAGMA table_info({name})"
        col_result = self.query(col_query)[1]
        columns = [(r[1], r[2]) for r in col_result]

        idx_query = f"PRAGMA index_list({name})"
        idx_result = self.query(idx_query)[1]
        key_set = set(r[1] for r in idx_result)

        table_options = ""
        return columns, key_set, table_options

    _create_search = re.compile(r'\bCREATE\s+TABLE\s+(`?)(\w+)\1\s+',
                                re.I).search
    _key_search = re.compile(r'\bKEY\s+(`[^`]+`)\s+(.+)').search

    def upgradeSchema(self, create_sql, create_if_not_exists=False,
                            initialize=None, src__=0):
        m = self._create_search(create_sql)
        if m is None:
            return

        name = m.group(2)
        new_name = f"_{name}_new"
        with (nullcontext if src__ else self.lock)():
            try:
                old_list, _, _ = self._getTableSchema(name)
            except OperationalError as e:
                if "no such table" not in str(e).lower() or not create_if_not_exists:
                    raise
                if not src__:
                    self.query(create_sql)
                return create_sql

            # Build migration SQL
            old_cols = {c for c, _ in old_list}

            # Inspect new schema using temp table
            self.query(f"CREATE TABLE {new_name} {create_sql[m.end():]}")
            try:
                new_list, _, _ = self._getTableSchema(new_name)
            finally:
                self.query(f"DROP TABLE {new_name}")

            changed = False
            if len(new_list) != len(old_list):
                changed = True
            else:
                for index in range(len(new_list)):
                    if new_list[index] != old_list[index]:
                        changed = True
                        break
            if changed:
                new_cols = [c for c, _ in new_list if c in old_cols]
                col_sql = ", ".join(f'"{c}"' for c in new_cols)

                migration = [
                    f"CREATE TABLE {new_name} {create_sql[m.end():]}",
                ]

                if new_cols:
                    migration.append(
                        f"INSERT INTO {new_name} ({col_sql}) "
                        f"SELECT {col_sql} FROM {name}"
                    )

                migration += [
                    f"DROP TABLE {name}",
                    f"ALTER TABLE {new_name} RENAME TO {name}",
                ]

                src_sql = ";\n".join(migration)

                if src__:
                    return src_sql

                # Execute migration
                for stmt in migration:
                    self.query(stmt)

                # Initialize newly added columns
                if initialize:
                    added = [c for c, _ in new_list if c not in old_cols]
                    if added:
                        initialize(self, added)

                return src_sql
       


class DeferredSqliteDB(SqliteDB):
    """
        An experimental MySQL DA which implements deferred execution
        of SQL code in order to reduce locks and provide better behaviour
        with MyISAM non transactional tables
    """
    def __init__(self, *args, **kw):
        SqliteDB.__init__(self, *args, **kw)
        #assert self._use_TM
        self._sql_string_list = []

    def query(self, query_string, max_rows=1000, query_value = None):
        self._register()
        if isinstance(query_string, six.text_type):
            query_string = query_string.encode('utf-8')
        for qs in query_string.split(b'\0'):
            qs = qs.strip()
            if qs:
                if match_select(qs):
                    raise NotSupportedError(
                        "can not SELECT in deferred connections")
                self._sql_string_list.append(qs)
        return (),()

    def _begin(self, *ignored):
        # The Deferred DB instance is sometimes used for several
        # transactions, so it is required to clear the sql_string_list
        # each time a transaction starts
        del self._sql_string_list[:]

    def _finish(self, *ignored):
        # BUG: It's wrong to execute queries here because tpc_finish must not
        #      fail. Consider moving them to commit, tpc_vote or in an
        #      after-commit hook.
        if self._sql_string_list:
            SqliteDB._begin(self)
            for qs in self._sql_string_list:
                self._query(qs)
            del self._sql_string_list[:]
            SqliteDB._finish(self)

    tpc_vote = TM.tpc_vote
    _abort = _begin
