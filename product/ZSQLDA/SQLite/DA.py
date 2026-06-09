database_type = 'SQLite'
__doc__ = '''%s Database Connection''' % database_type

from App.special_dtml import HTMLFile
from .. import DABase
from ..DABase import database_connection_pool
from .db import DB, DeferredDB

manage_addZSQLiteConnectionForm = HTMLFile('connectionAdd', globals())


class Connection(DABase.Connection):
    """SQLite Connection Object"""
    database_type = database_type
    id = '%s_database_connection' % database_type
    meta_type = title = 'Z %s Database Connection' % database_type
    icon = 'misc_/Z%sDA/conn' % database_type

    manage_properties = HTMLFile('connectionEdit', globals())

    def factory(self):
        return DB


class DeferredConnection(Connection):
    """Experimental DA which implements deferred SQL code execution to reduce
    locking issues.
    """
    meta_type = title = 'Z %s Deferred Database Connection' % database_type

    def factory(self):
        return DeferredDB


def manage_addZSQLiteConnection(self, id, title, connection_string,
                                check=None, deferred=False, REQUEST=None):
    """Add a Z SQLite Database Connection to a folder."""
    cls = DeferredConnection if deferred else Connection
    connection = cls(id, title, connection_string)
    self._setObject(id, connection)
    if check:
        connection.connect(connection_string)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


__ac_permissions__ = (
    ('Add Z SQLite Database Connections',
     ('manage_addZSQLiteConnectionForm',
      'manage_addZSQLiteConnection')),
)

misc_ = DABase.build_misc_()
