
__version__="$Revision: 1.3 $"[11:-2]

class LDAPConnectionAccessors:
    """ getters / setters for LDAP Properties """

    __ac_permissions__ = (
        ('Access contents information',
         ('getId','getTitle','getHost','getPort','getBindAs','getBoundAs',
          'getPW','getDN','getOpenConnection','getBrowsable',
          'shouldBeOpen','getTransactional',),),
        ('Manage properties',
         ('setID','setTitle','setHost','setPort', 'setBindAs','setPW',
          'setDN','setOpenConnection','setBrowsable','setBoundAs',
          'setTransactional',),),
        )

    def getId(self):
        return self.id

    def setId(self, id):
        self.id = id

    def getTitle(self):
        return self.title

    def setTitle(self, title):
        self.title = title

    def getHost(self):
        """ returns the host that this connection is connected to """
        return self.host

    def setHost(self, host):
        self.host = host

    def getPort(self):
        """ returns the port on the host that this connection connects to """
        return self.port

    def setPort(self, port):
        self.port = port

    def getBindAs(self):
        """ return the DN that this connection is bound as """
        return self.bind_as
    getBoundAs = getBindAs

    def setBindAs(self, bindAs):
        self.bind_as = bindAs
    setBoundAs = setBindAs

    def getPW(self):
        """ return the password that this connection is connected with """
        return self.pw

    def setPW(self, pw):
        self.pw = pw

    def getDN(self):
        return self.dn

    def setDN(self, dn):
        self.dn = dn

    def getOpenConnection(self):
        """ self.openc means that the connection is open to Zope.  However,
        the connection to the LDAP server may or may not be opened.  If
        this returns false, we shouldn't even try connecting."""
        return self.openc

    def setOpenConnection(self, openc):
        self._v_openc = openc

    shouldBeOpen = getOpenConnection

    
    def getBrowsable(self):
        """ if true, connection object is set to be browsable through the
        management interface """
        return getattr(self, '_canBrowse', 0)

    def setBrowsable(self, browsable):
        self._canBrowse = browsable

    def getTransactional(self):
        """ If transactional returns TRUE, the TransactionManager stuff
        is used.  If FALSE, changes are sent to LDAP immediately. """
        # Default to '1', to emulate the original behavior
        return getattr(self, 'isTransactional', 1)


    def setTransactional(self, transactional=1):
        self.isTransactional = transactional
        self._refreshEntryClass()
        # We have a fair amount of transaction-sensitive methods that
        # only want to run during a commit, and these are the ones that
        # actually send the data to the LDAP server.  When in non-transactional
        # mode, we want these things to run at any time.  In a sense, we're
        # always committing.
        if not transactional:
            self._isCommitting = 1
        
import Globals
Globals.default__class_init__(LDAPConnectionAccessors)
