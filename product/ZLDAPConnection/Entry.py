"""\
LDAP Entry Objects
"""


__version__ = "$Revision: 1.13 $"[11:-2]

import Acquisition, AccessControl, OFS, string
import transaction
from App.special_dtml import HTMLFile
from App.Dialogs import MessageDialog
import ldap, urllib, UserList

ConnectionError='ZLDAP Connection Error'

def isNotBlank(s):
    #test for non-blank strings
    if type(s) is type('a') and s=='':
        return 0
    else: return 1

class AttrWrap(UserList.UserList):
    """simple attr-wrapper for LDAP attributes"""
    def __str__(self):
        return string.join(self.data,', ')

class GenericEntry(Acquisition.Implicit):
    """\
    The GenericEntry class holds all the LDAP-Entry specific information.
    """
    __ac_permissions__ = (
        ('Access contents information',
         ('get',), ('Anonymous',),),
        ('Manage Entry information',
         ('set', 'setattrs', 'setAll','remove',),),
        ('Create New Entry Objects',
         ('addSubentry',),),
        ('Delete Entry Objects',
         ('deleteSubentry',),),
        )

    __name__ = "GenericEntry"

    def __init__(self, dn, attrs=None, connection=None, isNew=0):
        self.id = ldap.explode_dn(dn)[0] # Split the DN into a list.
        self.dn = dn                    # Our actually unique ID in tree
        self.__connection = None

        if attrs is None and connection is not None:
            # We have no passed in attributes, but we do have a connection
            # to get them from.
            self._init(connection)
        elif attrs and connection is not None:
            # Attributes were passed in, so we don't need to go to our
            # connection to retrieve them
            self._data = attrs
            self.__connection = connection
        else:
            # We're totally blank and disconnected
            self._data = {}

        self._isNew = isNew
        if isNew:
            pass                        # XXX need to handle creation here
        self._isDeleted = 0             # Deletion flag
        self.__subentries = {}          # subentries
        self._mod_delete = []


    def _init(self, connection):
        self.__connection = connection
        if not self._isNew:
            self._data = connection.getAttributes(self.dn)
        else:
            self._data = {}

    def _reset(self):
        if self._isNew: self._data = {}
        else: self._data = self._connection().getAttributes(self.dn)

    def __repr__(self):
        r="<Entry instance at %s; %s>" % (id(self), self.dn)
        return r

    def _connection(self):
        if self.__connection is None:
            raise ConnectionError, 'No connection object for this entry'
        else:
            return self.__connection

    #### Subentry and Attribute Access Machinery ##########
    def __getitem__(self, key):
        """getitem is used to get sub-entries, not attributes"""
        if self.__subentries:
            se=self._subentries()
            if se.has_key(key):
                return se[key]
        key = '%s, %s' % (urllib.unquote(key), self.dn)
        conn= self._connection()
        if conn.hasEntry(key):
            return conn.getEntry(key, self)
        else:
            raise IndexError, key

    def __getattr__(self, attr):
        if self._data.has_key(attr):
            return AttrWrap(self._data[attr])
        else:
            raise AttributeError, attr

    #### Direct access for setting/getting/unsetting attributes
    def get(self, attr):
        if self._data.has_key(attr):
            return self._data[attr]
        else:
            raise AttributeError, attr

    def set(self, key, value):
        """ Sets individual items """
        self.setattrs({ key:value })

    def setattrs(self, kwdict={}, **kw):
        """ Sets one or more attributes on the entry object, taking in
        both a dictionary AND\OR keywork arguments """
        kwdict.update(kw)
        data = self._data
        for attr, value in kwdict.items():
            if type(value) is type(''):
                value = [value]
            data[attr] = value

        self._modify()

    def setAll(self, kwdict={}, **kw):
        """ The dictionary\keywords passed in become ALL of the new
        attributes for the Entry (old data is lost) """
        kwdict.update(kw)               # Merge passed in dict with keywords
        self._data = {}                 # Clear our Entry attributes
        self.setattrs(kwdict)           # And call self.setattrs to do the work

    def remove(self, attr):
        """ Remove the attribute\attribute list """
        if type(attr) is type(''):
            attr = (attr,)

        data = self._data
        mod_d = self._mod_delete
        for item in attr:
            if data.has_key(item):
                del data[attr]
                mod_d.append(attr)

        self._modify()                  # Send the changes to LDAP

    ### These methods actually change the object.  In the Generic Model,
    ### a .set calls this directly, while in the TransactionalModel this
    ### gets called by the Transaction system at commit time.
    def _modify(self):
        modlist = []

        for attribute, values in self._data.items():
            modlist.append((ldap.MOD_REPLACE, attribute, values))
        for attribute in self._mod_delete:
            modlist.append((ldap.MOD_DELETE, attribute, None))

        self._connection()._modifyEntry(self.dn, modlist)
        self._mod_delete=[]
        self.__subentries={}

    #### Get the ZLDAPConnection object.
    def _connection(self):
        if self.__connection is None:
            raise ConnectionError, 'Cannot Get Connection'
        else:
            return self.__connection

    def _setConnection(self, connection):
        self.__connection = connection

    ### Subentries
    def _subentries(self):
        if not self.__subentries:
            # self.__subentries is empty, look up our subentries
            # in the connection object and then set self.__subentries
            r = {}
            se = self._connection().getSubEntries(self.dn,self)
            for subentry in se:
                r[subentry.id] = subentry
            self.__subentries = r

        return self.__subentries

    def _clearSubentries(self):
        self.__subentries = {}

    def _setSubentry(self, entryid, entry):
        self.__subentries[entryid] = entry

    def _delSubentry(self, entryid):
        subs = self.__subentries
        if subs.has_key(entryid): del self.__subentries[entryid]

    ### Deleting Subentries
    def _beforeDelete(self, **ignored):
        """ Go through all the subentries and delete them too """
        conn = self._connection()
        for entry in self._subentries().values():
            entry._beforeDelete()
            conn._deleteEntry(entry.dn) # Delete from the server
            self._delSubentry(entry.id) # Delete our own reference

    def _delete(self, entry):
        conn = self._connection()

        entry._beforeDelete()
        conn._deleteEntry(entry.dn)
        entry._isDeleted = 1
        self._delSubentry(entry.id)

    def _delete_dn(self, rdn):
        """ Delete by relative dn, ( - entry._delete_dn('sn=Shell') - ) """
        entry = self[rdn]               # Get the subentry
        self._delete(entry)

    ### Adding subentries
    def addSubentry(self, rdn, attrs={}, **kw):
        """ Create a new subentry of myself """
        conn = self._connection()
        nkw = {}
        nkw.update(attrs); nkw.update(kw)
        attrs = nkw

        # Create the full new DN (Distinguished Name) for the new subentry
        # and verify that it doesn't already exist
        dn = "%s,%s" % (string.strip(rdn), self.dn)
        if conn.hasEntry(dn):           # Check the LDAP server directly
            raise KeyError, "DN '%s' already exists" % dn

        # Now split out the first attr based on the RDN (ie 'cn=bob') and
        # turn it into one of our attributes (ie attr[cn] = 'bob')
        key, value = map(string.strip, string.split(rdn,'='))
        attrs[key] = value

        # If the objectclass is not already set in the attrs, set it now
        if not attrs.has_key('objectclass'):
            attrs['objectclass'] = ['top']

        # Instantiate the instance based on the connections EntryFactory
        Entry = conn._EntryFactory()
        entry = Entry(dn, attrs, conn, isNew=1).__of__(self)
        conn._addEntry(dn, attrs.items()) # Physically add the new entry
        self._setSubentry(entry.id, entry)

        return entry

    ### Public API for deleting subentries
    def deleteSubentry(self, entry):
        """ Delete a subentry (may be specified either by an rdn (string)
        or an Entry object instance """
        if type(entry) is type(''):
            self._delete_dn(entry)      # Delete by the RDN ('cn=...')
        else:
            self._delete(entry)         # Delete by Entry object itself


class TransactionalEntry(GenericEntry): #Acquisition.Implicit
    """\
    The TransactionalEntry class holds all the LDAP-Entry specific information,
    registers itself with the transaction manager, etc.  It's faceless.
    All Zope UI/Management methods will be implemented in the Entry class.
    """
    __name__ = "TransactionalEntry"

    __ac_permissions__ = (
        ('Manage Entry information',
         ('undelete', 'setattrs','remove'),),
        ('Create New Entry Objects',
         ('addSubentry',),),
        )

    _registered=None            #denotes if we've registered with the
                                #transaction manager

    def __init__(self, dn, attrs=None, connection=None, isNew=0):
        self.id=ldap.explode_dn(dn)[0]  #split the DN into a list.
        self.dn=dn                      #Our actually unique ID in tree
        self._p_jar=None                #actually, the connection
        self._setConnection(None)

        if attrs is None and connection is not None:
            self._init(connection)
        elif attrs and connection is not None:
            self._data=attrs
            self._p_jar=connection
            self._setConnection(connection)
        else:
            self._data={}
        self._isNew=isNew
        if isNew:
            transaction.get().register(self)
            self._registered=1
        self._isDeleted=0               #deletion flag
        self._clearSubentries()
        self._mod_delete=[]

    # We override _set here because we will be physically updated by
    # the transaction manager (we don't call self._modify(), the transaction
    # machinery will)
    def setattrs(self, kwdict={}, **kw):
        """\
        Set attributes in self._data and register ourselves with the
        transaction machinery.  Data is not committed to LDAP when this
        is called.
        """
        if not self._registered:
            transaction.get().register(self)
            self._registered=1

        kwdict.update(kw)
        data = self._data
        for attr, value in kwdict.items():
            if type(value) is type(''):
                value = [value]
            data[attr] = value


    # We override _remove (previously '_unSet') here because we don't call
    # self._modify() (the transaction manager will)
    def remove(self, attr):
        """\
        Unset (delete) an attribute
        """
        if not self._registered:
            transaction.get().register(self)
            self._registered=1

        if type(attr) is type(''):
            attr = (attr,)

        data = self._data
        mod_d = self._mod_delete
        for item in attr:
            if data.has_key(item):
                del data[item]
                mod_d.append(item)


    ### Transaction Related methods
    def _reset(self):
        self._rollback()

    def _rollback(self):
        conn=self._connection()
        if not self._isNew:
            self._data=conn.getAttributes(self.dn)
            self._clear_subentries={}
        else:
            self._data={}

    ### Adding and Deleting sub-entries.
    def _beforeDelete(self, **ignored):
        c=self._connection()
        for entry in self._subentries().values():
            entry.manage_beforeDelete()
            c._registerDelete(entry.dn)
            entry._isDeleted=1
            del self._subentries()[entry.id]

    def _delete(self, o):
        c=self._connection()
        o._beforeDelete()
        c._registerDelete(o.dn)
        o._isDeleted=1
        if not o._registered:
            transaction.get().register(o)
            o._registered=1
        del self._subentries()[o.id]

    def _delete_dn(self, rdn):
        o=self[rdn]
        self._delete(o)

    def undelete(self):
        '''undelete myself'''
##        c=self._connection()
##        c._unregisterDelete(self.dn)
        self._isDeleted=0

    def addSubentry(self, rdn, attrs={}, **kw):
        ''' create a new subentry of myself '''
        c=self._connection()
        nkw = {}
        nkw.update(attrs); nkw.update(kw)
        attrs = nkw

        #create the new full DN for new subentry and check its existance
        dn='%s,%s' % (string.strip(rdn), self.dn)
        if c.hasEntry(dn):
            raise KeyError, "DN '%s' already exists" % dn

        # now split out the first attr based on the rdn (ie 'cn=bob', turns
        # into attr['cn'] = 'bob'
        key, value = map(string.strip,string.split(rdn,'='))
        attrs[key] = value

        #if objectclass is not set in the attrs, set it now
        if not attrs.has_key('objectclass'):
            attrs['objectclass']=['top']

        #instantiate the instance based on current instances class
        #and register it to be added at commit time
        Entry = c._EntryFactory()
        entry = Entry(dn,attrs,c,isNew=1).__of__(self)
        c._registerAdd(entry)           # Register new Entry (added by TM)
        self._setSubentry(entry.id, entry)

        return entry



class ZopeEntry(OFS.SimpleItem.Item):
    '''Entry Object'''

    #### Initialazation Routines ##############

    manage_options=(
        {'label':'Attributes','action':'manage_attributes'},
        )

    __ac_permissions__=(
        ('Access contents information', ('manage_attributes',),
         ('Manager','Anonymous',),),
        ('Manage Entry information', ('manage_changeAttributes',
                                      'manage_addAttribute',
                                      'manage_editAttributes',),
         ('Manager',),),
        ('Create New Entry Objects',
         ('manage_newEntry', 'manage_newEntryWithAttributes'),
         ('Manager',),),
        )

    manage_attributes=HTMLFile("attributes",globals())
    manage_main=manage_attributes
    isPrincipiaFolderish=1


    #### Entry & Attribute Access Machinery #####################

    def attributesMap(self):
        return self._data.items()

    def __bobo_traverse__(self, REQUEST, key):
        ' allow traversal to subentries '
        key=urllib.unquote(key)
        if key in self.objectIds(): return self[key]
        else: return getattr(self,key)

    ###### Tree Machinery ######

    def tpValues(self):
        return self._subentries().values()

    def tpId(self):
        return self.id

    def tpURL(self):
        """Return string to be used as URL relative to parent."""
        return urllib.quote(self.id)

    ### Object Manager-ish Machinery
    def objectValues(self):
        return self._subentries().values()

    def objectIds(self):
        return self._subentries().keys()

    def objectItems(self):
        return self._subentries().items()

    ### Zope management stuff

    def manage_deleteEntry(self, ids, REQUEST=None):
        '''Delete marked Entries and all their sub-entries.'''

        for rdn in ids:
            self._delete_dn(rdn)

        if REQUEST is not None:
            return self.manage_contents(self, REQUEST)


    def manage_newEntry(self, rdn, REQUEST=None):
        '''Add a new entry'''

        e = self.addSubentry(rdn)

        if REQUEST is not None:
            return self.manage_contents(self, REQUEST)
        else:
            return e

    def manage_newEntryWithAttributes(self, rdn, attributes={}, **kw):
        """ add a new entry with attributes """
        attributes.update(kw)           # merge the keyword args in
        e = self.addSubentry(rdn, attributes)
        return e                        # return the new entry

    def manage_addAttribute(self, id, values, REQUEST=None):
        '''Add an attribute to an LDAP entry'''

        self.set(id, values)

        if REQUEST is not None:
            return self.manage_attributes(self, REQUEST)


    def manage_editAttributes(self, REQUEST):
        """Edit entry's attributes via the web."""

        for attribute in self._data.keys():
            values = REQUEST.get(attribute, [])
            values = filter(isNotBlank, values)   #strip out blanks

            self.set(attribute, values)

        return MessageDialog(
               title  ='Success!',
               message='Your changes have been saved',
               action ='manage_attributes')

    def manage_changeAttributes(self, REQUEST=None,  **kw):
        """Change existing Entry's Attributes.

        Change entry's attributes by passing either a mapping object
        of name:value pairs {'foo':6} or passing name=value parameters
        """

        if REQUEST and not kw:
            kw=REQUEST

        datakeys = self._data.keys()

        if kw:
            for name, value in kw.items():
                if name in datakeys:
                    self.set(name, value)

        if REQUEST is not None:
            return MessageDialog(
                title  ='Success!',
                message='Your changes have been saved',
                action ='manage_propertiesForm')


import App.class_init
for klass in (GenericEntry, TransactionalEntry, ZopeEntry):
    App.class_init.default__class_init__(klass)

