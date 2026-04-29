from collections import defaultdict
from weakref import WeakKeyDictionary
import transaction
import Shared.DC.ZRDB.Connection
from DateTime import DateTime

database_connection_pool = defaultdict(WeakKeyDictionary)

class Connection(Shared.DC.ZRDB.Connection.Connection):
    connect_on_load = False

    def factory(self):
        raise NotImplementedError

    def manage_beforeDelete(self, item, container):
        database_connection_pool.get(self._p_oid, {}).pop(self._p_jar, None)

    def connect(self, s):
        self._v_connected = ''
        if not self._p_oid:
            transaction.savepoint(optimistic=True)
        pool = database_connection_pool[self._p_oid]
        connection = pool.get(self._p_jar)
        DB = self.factory()
        if connection.__class__ is not DB or connection._connection != s:
            connection = pool[self._p_jar] = DB(s)
        self._v_database_connection = connection
        self._v_connected = DateTime()
        return self

    def sql_quote__(self, v, escapes={}):
        try:
            connection = self._v_database_connection
        except AttributeError:
            self.connect(self.connection_string)
            connection = self._v_database_connection
        return connection.string_literal(v)


class DeferredConnection(Connection):
    pass


class DB:
    pass
