database_type = 'MySQL'
__doc__ = '''%s Database Connection''' % database_type

from App.special_dtml import HTMLFile
from .. import DABase
from ..DABase import database_connection_pool
from .db import DB, DeferredDB

manage_addZMySQLConnectionForm = HTMLFile('connectionAdd', globals())


class Connection(DABase.Connection):
    """MySQL Connection Object"""
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


def manage_addZMySQLConnection(self, id, title, connection_string,
                               check=None, deferred=False, REQUEST=None):
    """Add a Z MySQL Database Connection to a folder."""
    cls = DeferredConnection if deferred else Connection
    connection = cls(id, title, connection_string)
    self._setObject(id, connection)
    if check:
        connection.connect(connection_string)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


# BBB: Allow loading of deferred connections that were created
#      before the merge of ZMySQLDDA into ZMySQLDA.
import sys, types
m = 'Products.ZMySQLDDA'
assert m not in sys.modules, "please remove obsolete ZMySQLDDA product"
sys.modules[m] = types.ModuleType(m)
m += '.DA'
sys.modules[m] = m = types.ModuleType(m)
m.DeferredConnection = DeferredConnection
del m


__ac_permissions__ = (
    ('Add Z MySQL Database Connections',
     ('manage_addZMySQLConnectionForm',
      'manage_addZMySQLConnection')),
)

misc_ = DABase.build_misc_()
