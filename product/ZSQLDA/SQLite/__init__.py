database_type = 'SQLite'
__doc__ = '''%s Database Connection''' % database_type

from App.special_dtml import HTMLFile
from .. import DA
from .db import DB, DeferredDB

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
