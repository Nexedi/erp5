##############################################################################
#
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
#
# Copyright (c) Digital Creations.  All rights reserved.
#
# This license has been certified as Open Source(tm).
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
#
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
#
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
#
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
#
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
#
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
#
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
#
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
#
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
#
#
# Disclaimer
#
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
#
#
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
#
##############################################################################

'''$Id: db.py,v 1.20 2002/03/14 20:24:54 adustman Exp $'''
__version__='$Revision: 1.20 $'[11:-2]

import os
import re
import _mysql
import MySQLdb
import warnings
from contextlib import contextmanager, nested
from _mysql_exceptions import OperationalError, NotSupportedError, ProgrammingError
MySQLdb_version_required = (0,9,2)

_v = getattr(_mysql, 'version_info', (0,0,0))
if _v < MySQLdb_version_required:
    raise NotSupportedError, \
        "ZMySQLDA requires at least MySQLdb %s, %s found" % \
        (MySQLdb_version_required, _v)

from MySQLdb.converters import conversions
from MySQLdb.constants import FIELD_TYPE, CR, ER, CLIENT
from Shared.DC.ZRDB.TM import TM
from DateTime import DateTime
from zLOG import LOG, ERROR, WARNING
from ZODB.POSException import ConflictError

import sys

hosed_connection = (
    CR.SERVER_GONE_ERROR,
    CR.SERVER_LOST
    )

query_syntax_error = (
    ER.BAD_FIELD_ERROR,
    )

lock_error = (
    ER.LOCK_WAIT_TIMEOUT,
    ER.LOCK_DEADLOCK,
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

def _mysql_timestamp_converter(s):
        s = s.ljust(14, '0')
        parts = map(int, (s[:4],s[4:6],s[6:8],
                          s[8:10],s[10:12],s[12:14]))
        return DateTime("%04d-%02d-%02d %02d:%02d:%02d" % tuple(parts))

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

class DB(TM):
    """This is the ZMySQLDA Database Connection Object."""

    conv=conversions.copy()
    conv[FIELD_TYPE.LONG] = int
    conv[FIELD_TYPE.DATETIME] = DATETIME_to_DateTime_or_None
    conv[FIELD_TYPE.DATE] = DATE_to_DateTime_or_None
    conv[FIELD_TYPE.DECIMAL] = float
    conv[FIELD_TYPE.BIT] = ord_or_None
    del conv[FIELD_TYPE.TIME]

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
        transactional = self.db.server_capabilities & CLIENT.TRANSACTIONS
        if self._try_transactions == '-':
            transactional = 0
        elif not transactional and self._try_transactions == '+':
            raise NotSupportedError, "transactions not supported by this server"
        self._transactions = transactional
        self._use_TM = transactional or self._mysql_lock

    def _parse_connection_string(self):
        self._mysql_lock = self._try_transactions = None
        self._kw_args = kwargs = {'conv': self.conv}
        items = self._connection.split()
        if not items:
            return
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
      self.db.close()

    def _forceReconnection(self):
      db = self.db
      if db is not None:
        try:
          db.close()
        except Exception as exception:
          # XXX: MySQLdb seems to think it's smart to use such general SQL
          # exception for such a specific case error, rather than subclassing
          # it. In an attempt to be future-proof (if it ever raises the same
          # exception for unrelated reasons, like errors which would happen in
          # mysql_close), check also the exception message.
          # Anyway, this is just to avoid useless log spamming, so it's not a
          # huge deal either way.
          if not isinstance(
            exception,
            ProgrammingError,
          ) or exception.message != 'closing a closed connection':
            LOG(
              'ZMySQLDA.db',
              WARNING,
              'Failed to close pre-existing connection, discarding it',
              error=True,
            )
      self.db = MySQLdb.connect(**self._kw_args)
      self._query("SET time_zone='+00:00'")

    def tables(self, rdb=0,
               _care=('TABLE', 'VIEW')):
        """Returns a list of tables in the current database."""
        r=[]
        a=r.append
        result = self._query("SHOW TABLES")
        row = result.fetch_row(1)
        while row:
            a({'TABLE_NAME': row[0][0], 'TABLE_TYPE': 'TABLE'})
            row = result.fetch_row(1)
        return r

    def columns(self, table_name):
        """Returns a list of column descriptions for 'table_name'."""
        try:
            c = self._query('SHOW COLUMNS FROM %s' % table_name)
        except Exception:
            return ()
        from string import join
        r=[]
        for Field, Type, Null, Key, Default, Extra in c.fetch_row(0):
            info = {}
            field_default = Default and "DEFAULT %s"%Default or ''
            if Default: info['Default'] = Default
            if '(' in Type:
                end = Type.rfind(')')
                short_type, size = Type[:end].split('(', 1)
                if short_type not in ('set','enum'):
                    if ',' in size:
                        info['Scale'], info['Precision'] = \
                                       map(int, size.split(',', 1))
                    else:
                        info['Scale'] = int(size)
            else:
                short_type = Type
            if short_type in field_icons:
                info['Icon'] = short_type
            else:
                info['Icon'] = icon_xlate.get(short_type, "what")
            info['Name'] = Field
            info['Type'] = type_xlate.get(short_type,'string')
            info['Extra'] = Extra,
            info['Description'] = join([Type, field_default, Extra or '',
                                        key_types.get(Key, Key or ''),
                                        Null != 'YES' and 'NOT NULL' or '']),
            info['Nullable'] = Null == 'YES'
            if Key:
                info['Index'] = 1
            if Key == 'PRI':
                info['PrimaryKey'] = 1
                info['Unique'] = 1
            elif Key == 'UNI':
                info['Unique'] = 1
            r.append(info)
        return r

    def _query(self, query, allow_reconnect=False):
        """
          Send a query to MySQL server.
          It reconnects automatically if needed and the following conditions are
          met:
           - It has not just tried to reconnect (ie, this function will not
             attempt to connect twice per call).
           - This connection is not transactional and has set not MySQL locks,
             because they are bound to the connection. This check can be
             overridden by passing allow_reconnect with True value.
        """
        try:
            self.db.query(query)
        except OperationalError, m:
            if m[0] in query_syntax_error:
              raise OperationalError(m[0], '%s: %s' % (m[1], query))
            if m[0] in lock_error:
              raise ConflictError('%s: %s: %s' % (m[0], m[1], query))
            if (allow_reconnect or not self._use_TM) and \
              m[0] in hosed_connection:
              self._forceReconnection()
              self.db.query(query)
            else:
              LOG('ZMySQLDA', ERROR, 'query failed: %s' % (query,))
              raise
        except ProgrammingError:
          LOG('ZMySQLDA', ERROR, 'query failed: %s' % (query,))
          raise
        return self.db.store_result()

    def query(self, query_string, max_rows=1000):
        """Execute 'query_string' and return at most 'max_rows'."""
        self._use_TM and self._register()
        desc = None
        # XXX deal with a typical mistake that the user appends
        # an unnecessary and rather harmful semicolon at the end.
        # Unfortunately, MySQLdb does not want to be graceful.
        if query_string[-1:] == ';':
          query_string = query_string[:-1]
        for qs in query_string.split('\0'):
            qs = qs.strip()
            if qs:
                if qs[:6].upper() == "SELECT" and max_rows:
                    qs = "%s LIMIT %d" % (qs, max_rows)
                c = self._query(qs)
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
        return self.db.string_literal(s)

    def _begin(self, *ignored):
        """Begin a transaction (when TM is enabled)."""
        try:
            self._transaction_begun = True
            if self._transactions:
                self._query("BEGIN", allow_reconnect=True)
            if self._mysql_lock:
                self._query("SELECT GET_LOCK('%s',0)" % self._mysql_lock, allow_reconnect=not self._transactions)
        except:
            LOG('ZMySQLDA', ERROR, "exception during _begin",
                error=sys.exc_info())
            raise

    def tpc_vote(self, *ignored):
        # Raise if a disconnection is detected, to avoid detecting this later
        self._query("SELECT 1")
        return TM.tpc_vote(self, *ignored)

    def _finish(self, *ignored):
        """Commit a transaction (when TM is enabled)."""
        if not self._transaction_begun:
            return
        self._transaction_begun = False
        if self._mysql_lock:
            self._query("SELECT RELEASE_LOCK('%s')" % self._mysql_lock)
        if self._transactions:
            self._query("COMMIT")

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
            if self._mysql_lock:
                self._query("SELECT RELEASE_LOCK('%s')" % self._mysql_lock)
            if self._transactions:
                self._query("ROLLBACK")
            else:
                LOG('ZMySQLDA', ERROR, "aborting when non-transactional")
        except OperationalError, m:
            LOG('ZMySQLDA', ERROR, "exception during _abort",
                error=sys.exc_info())
            if m[0] not in hosed_connection:
                raise

    def getMaxAllowedPacket(self):
        # minus 2-bytes overhead from mysql library
        return self._query("SELECT @@max_allowed_packet-2").fetch_row()[0][0]

    @contextmanager
    def lock(self):
        """Lock for the connected DB"""
        db = self._kw_args.get('db', '')
        lock = "SELECT GET_LOCK('ZMySQLDA(%s)', 5)" % db
        unlock = "SELECT RELEASE_LOCK('ZMySQLDA(%s)')" % db
        try:
            while not self.query(lock, 0)[1][0][0]: pass
            yield
        finally:
            self.query(unlock, 0)

    def _getTableSchema(self, name,
            create_lstrip = re.compile(r"[^(]+\(\s*").sub,
            create_rmatch = re.compile(r"(.*\S)\s*\)[^)]+\s"
              "(DEFAULT(\s+(CHARSET|COLLATE)=\S+)+).*$", re.DOTALL).match,
            create_split  = re.compile(r",\n\s*").split,
            column_match  = re.compile(r"`(\w+)`\s+(.+)").match,
            ):
        (_, schema), = self.query("SHOW CREATE TABLE " + name)[1]
        column_list = []
        key_set = set()
        m = create_rmatch(create_lstrip("", schema, 1))
        for spec in create_split(m.group(1)):
            if "KEY" in spec:
                key_set.add(spec)
            else:
                column_list.append(column_match(spec).groups())
        return column_list, key_set, m.group(2)

    _create_search = re.compile(r'\bCREATE\s+TABLE\s+(`?)(\w+)\1\s+',
                                re.I).search
    _key_search = re.compile(r'\bKEY\s+(`[^`]+`)\s+(.+)').search

    def upgradeSchema(self, create_sql, create_if_not_exists=False,
                            initialize=None, src__=0):
        m = self._create_search(create_sql)
        if m is None:
            return
        name = m.group(2)
        # Lock automatically unless src__ is True, because the caller may have
        # already done it (in case that it plans to execute the returned query).
        with (nested if src__ else self.lock)():
            try:
                old_list, old_set, old_default = self._getTableSchema("`%s`" % name)
            except ProgrammingError, e:
                if e[0] != ER.NO_SUCH_TABLE or not create_if_not_exists:
                    raise
                if not src__:
                    self.query(create_sql)
                return create_sql

            name_new = '`_%s_new`' % name
            self.query('CREATE TEMPORARY TABLE %s %s'
                % (name_new, create_sql[m.end():]))
            try:
                new_list, new_set, new_default = self._getTableSchema(name_new)
            finally:
                self.query("DROP TEMPORARY TABLE " + name_new)

            src = []
            q = src.append
            if old_default != new_default:
              q(new_default)

            old_dict = {}
            new = {column[0] for column in new_list}
            pos = 0
            for column, spec in old_list:
              if column in new:
                  old_dict[column] = pos, spec
                  pos += 1
              else:
                  q("DROP COLUMN `%s`" % column)

            for key in old_set - new_set:
              if "PRIMARY" in key:
                  q("DROP PRIMARY KEY")
              else:
                  q("DROP KEY " + self._key_search(key).group(1))

            column_list = []
            pos = 0
            where = "FIRST"
            for column, spec in new_list:
                try:
                    old = old_dict[column]
                except KeyError:
                    q("ADD COLUMN `%s` %s %s" % (column, spec, where))
                    column_list.append(column)
                else:
                    if old != (pos, spec):
                        q("MODIFY COLUMN `%s` %s %s" % (column, spec, where))
                        if old[1] != spec:
                            column_list.append(column)
                    pos += 1
                where = "AFTER `%s`" % column

            for key in new_set - old_set:
                q("ADD " + key)

            if src:
                src = "ALTER TABLE `%s`%s" % (name, ','.join("\n  " + q
                                                           for q in src))
                if not src__:
                    self.query(src)
                    if column_list and initialize and self.query(
                            "SELECT 1 FROM `%s`" % name, 1)[1]:
                        initialize(self, column_list)
                return src


class DeferredDB(DB):
    """
        An experimental MySQL DA which implements deferred execution
        of SQL code in order to reduce locks and provide better behaviour
        with MyISAM non transactional tables
    """
    def __init__(self, *args, **kw):
        DB.__init__(self, *args, **kw)
        assert self._use_TM
        self._sql_string_list = []

    def query(self,query_string, max_rows=1000):
        self._register()
        for qs in query_string.split('\0'):
            qs = qs.strip()
            if qs:
                if qs[:6].upper() == "SELECT":
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
            DB._begin(self)
            for qs in self._sql_string_list:
                self._query(qs)
            del self._sql_string_list[:]
            DB._finish(self)

    tpc_vote = TM.tpc_vote
    _abort = _begin
