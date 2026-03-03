database_type = 'SQLite'
import os
from collections import defaultdict
from weakref import WeakKeyDictionary
import transaction
import Shared.DC.ZRDB
from App.Dialogs import MessageDialog
from App.special_dtml import HTMLFile
from App.ImageFile import ImageFile
from DateTime import DateTime
from . import DABase
from .db import DB, DeferredDB
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import IS_ZOPE2

SHARED_DC_ZRDB_LOCATION = os.path.dirname(Shared.DC.ZRDB.__file__)

manage_addZSQLiteConnectionForm=HTMLFile('connectionAdd',globals())

def manage_addZSQLiteConnection(self, id, title, connection_string,
                               check=None, deferred=False, REQUEST=None):
    """Add a MySQL connection to a folder.

    Arguments:
        REQUEST -- The current request
        title -- The title of the ZSQLite Connection (string)
        id -- The id of the ZSQLite Connection (string)
        connection_string -- see connectionAdd.dtml
    """
    cls = DeferredConnection if deferred else Connection
    connection = cls(id, title, connection_string)
    self._setObject(id, connection)
    if check:
        connection.connect(connection_string)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

# Connection Pool for connections to MySQL.
database_connection_pool = defaultdict(WeakKeyDictionary)

class Connection(DABase.Connection):
    """ZSQLite Connection Object
    """
    database_type=database_type
    id='%s_database_connection' % database_type
    meta_type=title='Z %s Database Connection' % database_type
    icon='misc_/Z%sDA/conn' % database_type
    security = ClassSecurityInfo()

    manage_properties=HTMLFile('connectionEdit', globals())

    connect_on_load = False

    if not IS_ZOPE2:
      zmi_icon = 'fas fa-database'

    def factory(self): return DB

    security.declarePrivate('manage_beforeDelete')
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
        # XXX If date is used as such, it can be wrong because an existing
        # connection may be reused. But this is suposedly only used as a
        # marker to know if connection was successfull.
        self._v_connected = DateTime()
        return self

    def sql_quote__(self, v, escapes={}):
        try:
            connection = self._v_database_connection
        except AttributeError:
            # The volatile attribute sometimes disappears.
            # In this case, re-assign it by calling the connect method.
            # Note that we don't call sql_quote__ recursively by intention,
            # because if connect fails to assign the volatile attribute for
            # any reason, that would generate an infinite loop.
            self.connect(self.connection_string)
            connection = self._v_database_connection
        return connection.string_literal(v)


class DeferredConnection(Connection):
    """
        Experimental MySQL DA which implements
        deferred SQL code execution to reduce locking issues
    """
    meta_type=title='Z %s Deferred Database Connection' % database_type

    def factory(self): return DeferredDB


__ac_permissions__=(
    ('Add Z SQLite Database Connections',
     ('manage_addZSQLiteConnectionForm',
      'manage_addZSQLiteConnection')),
    )

misc_={'conn': ImageFile(
    os.path.join(SHARED_DC_ZRDB_LOCATION,'www','DBAdapterFolder_icon.gif'))}

for icon in ('table', 'view', 'stable', 'what',
             'field', 'text','bin','int','float',
             'date','time','datetime'):
    misc_[icon]=ImageFile(os.path.join('icons','%s.gif') % icon, globals())
