from AccessControl import getSecurityManager
from zExceptions import Unauthorized
from OFS.ObjectManager import ObjectManager

old_manage_FTPlist = ObjectManager.manage_FTPlist
def manage_FTPlist(self, REQUEST):
	if not getSecurityManager().checkPermission('Access contents information', self):
		raise Unauthorized('Not allowed to access contents.')
ObjectManager.manage_FTPlist = manage_FTPlist