database_type = 'MySQL'
__doc__ = '''%s Database Connection''' % database_type

from App.special_dtml import HTMLFile
from .. import DABase
from .db import DB, DeferredDB

class Connection(DABase.BaseConnection):
    """MySQL Connection Object"""
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


manage_addZMySQLConnectionForm = HTMLFile(
    'connectionAdd', globals(), __name__='connectionAdd_mysql')


def manage_addZMySQLConnection(self, id, title, connection_string,
                               check=None, deferred=False, REQUEST=None):
    """Add a Z MySQL Database Connection to a folder."""
    return DABase.manage_addConnection(
        self, Connection, DeferredConnection,
        id, title, connection_string, check, deferred, REQUEST)


__ac_permissions__ = (
    ('Add Z MySQL Database Connections',
     ('manage_addZMySQLConnectionForm',
      'manage_addZMySQLConnection')),
)

