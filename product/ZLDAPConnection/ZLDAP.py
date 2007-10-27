""" 
   An LDAP connection product.  Depends on David Leonard's ldapmodule.
   $Id: ZLDAP.py,v 1.11 2000/12/18 22:17:50 jeffrey Exp $
   Started by Anthony Baxter, <anthony@interlink.com.au>
   Continued by the folks @ CodeIt <http://www.codeit.com/>

   Now by Jeffrey P Shell <jeffrey@Digicool.com>.
"""

__version__ = "$Revision: 1.11 $"[11:-2]

import Acquisition, AccessControl, OFS, string
from Globals import HTMLFile, MessageDialog, Persistent
import ldap, urllib

import LDCAccessors
from Entry import ZopeEntry, GenericEntry, TransactionalEntry
ConnectionError='ZLDAP Connection Error'

manage_addZLDAPConnectionForm = HTMLFile('add', globals())

class NoBrainer:
    """ Empty class for mixin to EntryFactory """

class ZLDAPConnection(
    Acquisition.Implicit,
    Persistent, OFS.SimpleItem.Item,
    LDCAccessors.LDAPConnectionAccessors,
    AccessControl.Role.RoleManager):
    '''LDAP Connection Object'''

    isPrincipiaFolderish=1

    meta_type='LDAP Connection'

    manage_options=(
        {'label':'Connection Properties','action':'manage_main'},
        {'label':'Open/Close','action':'manage_connection'},
        {'label':'Browse', 'action':'manage_browse'},
        {'label':'Security','action':'manage_access'},
        )

    __ac_permissions__=(
        ('Access contents information',
         ('canBrowse',),),
        ('View management screens',('manage_tabs','manage_main'),
         ('Manager',)),
        ('Edit connection',('manage_edit',),('Manager',)),
        ('Change permissions',('manage_access',)),
        ('Open/Close Connection',('manage_connection',
                                  'manage_open','manage_close',),
         ('Manager',)),
        ('Browse Connection Entries', ('manage_browse',),('Manager',),),
        )

    manage_browse=HTMLFile('browse',globals())
    manage_connection=HTMLFile('connection',globals())

    ### dealing with browseability on the root.
    def canBrowse(self):
        """ Returns true if the connection is open *and* the '_canBrowse'
        property is set to true """
        return self.shouldBeOpen() and self.getBrowsable()


    ### constructor
    def __init__(self, id, title, host, port, basedn, bind_as, pw, openc,
                 transactional=1):
        "init method"
        self._v_conn = None
        self._v_delete = []
        self._v_openc = openc
        self.openc = openc
        self.setId(id)
        self.setTitle(title)
        self.setHost(host)
        self.setPort(port)
        self.setBindAs(bind_as)
        self.setPW(pw)
        self.setDN(basedn)
        self.setOpenConnection(openc)
        self.setTransactional(transactional)

        # if connection is specified to be open, open it up
        if openc: self._open()

    ### upgrade path...
    def __setstate__(self, state):
        # Makes sure we have an Entry class now
        self._refreshEntryClass()
        Persistent.__setstate__(self, state)

    ### Entry Factory stuff
    def _refreshEntryClass(self):
        """ This class sets up the Entry class used to return results. """
        transactional = self.getTransactional()
        if transactional:
            EntryBase = TransactionalEntry
        else:
            EntryBase = GenericEntry

        class LdapEntry(EntryBase, ZopeEntry):
            pass

        self._v_entryclass = LdapEntry
        return LdapEntry

    def _EntryFactory(self):
        """ Stamps out an Entry class to be used for every entry returned,
        taking into account transactional versus non-transactional """
        return getattr(self, '_v_entryclass', self._refreshEntryClass())

    ### Tree stuff
    def __bobo_traverse__(self, REQUEST, key):
        key=urllib.unquote(key)
        if hasattr(self, key):
            return getattr(self, key)
        return self.getRoot()[key]

    def tpId(self):
        return self.id

    def tpURL(self):
        return self.id

    def tpValues(self):
        if self.canBrowse():
            return self.getRoot().tpValues()
        else:
            return []

    #### TransactionalObjectManager stuff #####
    def tpc_begin(self,*ignored):
        #make sure we're open!
        if not self.__ping():      #we're not open
            raise (ConnectionError,
                   'LDAP Connection is not open for commiting')
        self._v_okobjects=[]

    def commit(self, o, *ignored):
        ' o = object to commit '
        # check to see if object exists
        oko=[]
        if self.hasEntry(o.dn):
            oko.append(o)
        elif o._isNew or o._isDeleted:
            oko.append(o)
        self._v_okobjects=oko
        
    def tpc_finish(self, *ignored):
        " really really commit and DON'T FAIL "
        oko=self._v_okobjects
        self._isCommitting=1
        d=getattr(self,'_v_delete',[])

        for deldn in d: self._deleteEntry(deldn)
        self._v_delete=[]

        for o in oko:
            try:
                if o._isDeleted:
                    pass
                    # we shouldn't need to do anything now that
                    # the mass delete has happened
                elif o._isNew:
                    self._addEntry(o.dn, o._data.items())
                    o._isNew=0
                    del self._v_add[o.dn]
                else:
                    o._modify()
                o._registered=0
            except:
                pass    #XXX We should log errors here

        del self._v_okobjects
        del self._isCommitting
        self.GetConnection().destroy_cache()

    def tpc_abort(self, *ignored):
        " really really rollback and DON'T FAIL "
        try:
            self._abort()
        except:
            pass        #XXX We should also log errors here

    def abort(self, o, *ignored):
        if o.dn in getattr(self,'_v_delete',()):
            self._v_delete.remove(o.dn)
        if o._isDeleted: o.undelete()
        o._rollback()
        o._registered=0
        if o._isNew:
            if o.dn in getattr(self,'_v_add',{}).keys():
                del self._v_add[o.dn]
        self.GetConnection().destroy_cache()
        
    def _abort(self):
        oko=self._v_okobjects
        for o in oko:
            self.abort(o)
        self.GetConnection().destroy_cache()
            
    def tpc_vote(self, *ignored):
        pass


    ### getting entries and attributes

    def hasEntry(self, dn):
        if getattr(self, '_v_add',{}).has_key(dn):
            #object is marked for adding
            return 1
        elif dn in getattr(self,'_v_delete',()):
            #object is marked for deletion
            return 0

        try:
            e=self._connection().search_s(dn, ldap.SCOPE_BASE,
                                          'objectclass=*')
            if e: return 1
        except ldap.NO_SUCH_OBJECT:
            return 0
        return 0

    def getRawEntry(self, dn):
        " return raw entry from LDAP module "
        if getattr(self, '_v_add',{}).has_key(dn):
            return (dn, self._v_add[dn]._data)
        elif dn in getattr(self,'_v_delete',()):
            raise ldap.NO_SUCH_OBJECT, "Entry '%s' has been deleted" % dn

        try:
            e=self._connection().search_s(
                dn, ldap.SCOPE_BASE, 'objectclass=*'
                )
            if e: return e[0]
        except:
            raise ldap.NO_SUCH_OBJECT, "Cannot retrieve entry '%s'" % dn


    def getEntry(self, dn, o=None):
        " return **unwrapped** Entry object, unless o is specified "
        Entry = self._EntryFactory()

        if getattr(self, '_v_add',{}).has_key(dn):
            e=self._v_add[dn]
        else:
            e=self.getRawEntry(dn)
            e=Entry(e[0],e[1],self)

        if o is not None:
            return e.__of__(o)
        else:
            return e

    def getRoot(self):
        " return root entry object "
        return self.getEntry(self.dn, self)

    def getAttributes(self, dn):
        " get raw attributes from entry from LDAP module "
        return self.getRawEntry(dn)[1]

    ### listing subentries

    def getRawSubEntries(self, dn):
        " get the raw entry objects of entry dn's immediate children "
        # XXX Do something soon to account for added but noncommited..?
        if dn in getattr(self,'_v_delete',()):
            raise ldap.NO_SUCH_OBJECT
        results=self._connection().search_s(
            dn, ldap.SCOPE_ONELEVEL, 'objectclass=*')
        r=[]
        for entry in results:
            #make sure that the subentry isn't marked for deletion
            if entry[0] not in getattr(self, '_v_delete',()):
                r.append(entry)
        return r

    def getSubEntries(self, dn, o=None):
        Entry = self._EntryFactory()
        
        r=[]
        se=self.getRawSubEntries(dn)

        for entry in se:
            e=Entry(entry[0],entry[1],self)
            if o is not None:
                e=e.__of__(o)
            r.append(e)

        return r

    ### modifying entries
    def _modifyEntry(self, dn, modlist):
        if not getattr(self,'_isCommitting',0):
            raise AccessError, 'Cannot modify unless in a commit'
            #someone's trying to be sneaky and modify an object
            #outside of a commit.  We're not going to allow that!
        c=self._connection()
        c.modify_s(dn, modlist)
        
    ### deleting entries
    def _registerDelete(self, dn):
        " register DN for deletion "
        d=getattr(self,'_v_delete',[])
        if dn not in d:
            d.append(dn)
        self._v_delete=d

    def _unregisterDelete(self, dn):
        " unregister DN for deletion "
        d=getattr(self, '_v_delete',[])
        if dn in d: d.remove(dn)
        self._v_delete=d

        self._unregisterAdd(dn)

    def _deleteEntry(self, dn):
        if not getattr(self, '_isCommitting',0):
            raise AccessError, 'Cannot delete unless in a commit'
        c=self._connection()
        c.delete_s(dn)

    ### adding entries
    def _registerAdd(self, o):
        a=getattr(self, '_v_add',{})
        if not a.has_key(o.dn):
            a[o.dn]=o
        self._v_add=a

    def _unregisterAdd(self, o=None, dn=None):
        a=getattr(self, '_v_add',{})
        if o and o in a.values():
            del a[o.dn]
        elif dn and a.has_key(dn):
            del a[dn]
        self._v_add=a

    def _addEntry(self, dn, attrs):
        if not getattr(self, '_isCommitting',0):
            raise AccessError, 'Cannot add unless in a commit'
        c=self._connection()
        c.add_s(dn, attrs)
        
    ### other stuff
    def title_and_id(self):
        "title and id, with conn state"
        s=ZLDAPConnection.inheritedAttribute('title_and_id')(self)
        if self.shouldBeOpen():
            s="%s (connected)" % s
        else:
            s='%s (<font color="red"> not connected</font>)' % s
        return s


    ### connection checking stuff

    def _connection(self):
        if self.openc:
            if not self.isOpen(): self._open()
            return self._v_conn
        else:
            raise ConnectionError, 'Connection Closed'

    GetConnection=_connection

    def isOpen(self):
        " quickly checks to see if the connection's open "
        if not hasattr(self, '_v_conn'):
            self._v_conn = None
        if self._v_conn is None or not self.shouldBeOpen():
            return 0
        else:
            return 1

    def __ping(self):
        " more expensive check on the connection and validity of conn "
        try:
            self._connection().search_s(self.dn,ldap.SCOPE_BASE,
                                        'objectclass=*')
            return 1
        except:
            self._close()
            return 0

    def _open(self):
        """ open a connection """
        try:
            self._close()
        except:
            pass
        self._v_conn = ldap.open(self.host, self.port)
        #Nicolas the version of pythonldap doesn't use the enable_cache method
        #self._v_conn.enable_cache()
        try:
            self._v_conn.simple_bind_s(self.bind_as, self.pw)
        except ldap.NO_SUCH_OBJECT:
            return """
   Error: LDAP Server returned `no such object' for %s. Possibly 
   the bind string or password are incorrect"""%(self.bind_as)
        self._v_openc = 1

    def manage_open(self, REQUEST=None):
        """ open a connection. """
        self.setOpenConnection(1)
        ret = self._open()
        if not getattr(self, '_v_openc', 0):
            return ret
        if REQUEST is not None:
            m='Connection has been opened.'
            return self.manage_connection(self,REQUEST,manage_tabs_message=m)

    def _close(self):
        """ close a connection """
        if self.getOpenConnection() == 0:
            #I'm already closed, but someone is still trying to close me
            self._v_conn = None
            self._v_openc = 0
        else:
            try: self._v_conn.unbind_s()
            except AttributeError: pass
            self._v_conn = None
            self._v_openc = 0

    def manage_close(self, REQUEST=None):
        """ close a connection. """
        self._close()
        if REQUEST is not None:
            m='Connection has been closed.'
            return self.manage_connection(self,REQUEST,manage_tabs_message=m)

    def manage_clearcache(self, REQUEST=None):
        """ clear the cache """
        self._connection().destroy_cache()
        if REQUEST is not None:
            m='Cache has been cleared.'
            return self.manage_connection(self,REQUEST,manage_tabs_message=m)


    manage_main=HTMLFile("edit",globals())

    def manage_edit(self, title, hostport, basedn, bind_as, pw, openc=0,
                    canBrowse=0, transactional=1, REQUEST=None):
        """ handle changes to a connection """
        self.title = title
        host, port = splitHostPort(hostport)
        if self.host != host:
            self._close()
            self.setHost(host)
        if self.port != port:
            self._close()
            self.setPort(port)
        if self.bind_as != bind_as:
            self._close()
            self.setBindAs(bind_as)
        if self.pw != pw:
            self._close()
            self.setPW(pw)
        if openc and not self.getOpenConnection():
            self.setOpenConnection(1)
            ret = self._open()
            if not self._v_openc:
                return ret
        if not openc and self.getOpenConnection():
            self.setOpenConnection(0)
            self._close()

        self.setBrowsable(canBrowse)
        self.setTransactional(transactional)
        self.setDN(basedn)

        if REQUEST is not None:
            return MessageDialog(
                title='Edited',
                message='<strong>%s</strong> has been edited.' % self.id,
                action ='./manage_main',
                )

    def _isAnLDAPConnection(self):
        return 1
    
def splitHostPort(hostport):
    import string
    l = string.split(hostport,':')
    host = l[0]
    if len(l) == 1:
        port = 389
    else:
        port = string.atoi(l[1])
    return host, port


def manage_addZLDAPConnection(self, id, title, hostport,
                              basedn, bind_as, pw, openc,
                              REQUEST=None):
    """create an LDAP connection and install it"""
    host, port = splitHostPort(hostport)
    conn = ZLDAPConnection(id, title, host, port, basedn, bind_as, pw, openc)
    self._setObject(id, conn)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)
