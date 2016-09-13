from AccessControl import getSecurityManager
from zExceptions import Unauthorized
from OFS.ObjectManager import ObjectManager

ObjectManager.__old_manage_FTPlist = ObjectManager.manage_FTPlist
def manage_FTPlist(self, REQUEST):
    """Returns a directory listing consisting of a tuple of
    (id,stat) tuples, marshaled to a string. Note, the listing it
    should include '..' if there is a Folder above the current
    one.

    In the case of non-foldoid objects it should return a single
    tuple (id,stat) representing itself."""

    if not getSecurityManager().checkPermission('Access contents information', self):
        raise Unauthorized('Not allowed to access contents.')

    return self.__old_manage_FTPlist(REQUEST)

ObjectManager.manage_FTPlist = manage_FTPlist
