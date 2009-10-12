# core of LDAP Filter Methods.


from Globals import HTMLFile, HTML
__version__ = "$Revision: 1.10 $"[11:-2]

try:
  import ldap
  from ldap import modlist
# see if it's on a regular path
except ImportError:
  from Products.ZLDAPConnection import ldap
  from Products.ZLDAPConnection.ldap import modlist
import string

from Shared.DC.ZRDB import Aqueduct
from Shared.DC.ZRDB.Aqueduct import parse, decodestring, default_input_form
from Shared.DC.ZRDB.Results import Results
import Acquisition, Globals, AccessControl.Role, OFS.SimpleItem
from Globals import HTMLFile, MessageDialog, Persistent
import DocumentTemplate
import ExtensionClass
import sys

from zLOG import LOG, INFO
from ldif import LDIFRecordList, is_dn, valid_changetype_dict, CHANGE_TYPES
import ldifvar
from AccessControl.DTML import RestrictedDTML
try:
    from AccessControl import getSecurityManager
except ImportError:
    getSecurityManager = None

MODIFY_MAPPING_DICT = {'add'      : ldap.MOD_ADD,
                       #'replace'  : ldap.MOD_REPLACE,
                       'delete'   : ldap.MOD_DELETE}

class ERP5LDIFRecordList(LDIFRecordList):

  def parse(self):
    """
    Continously read and parse LDIF records
    """
    self._line = self._input_file.readline()

    while self._line and \
          (not self._max_entries or self.records_read<self._max_entries):

      # Reset record
      version = None; dn = None; changetype = None; modop = None; entry = {};

      attr_type,attr_value = self._parseAttrTypeandValue()

      while attr_type!=None and attr_value!=None:
        if attr_type=='dn':
          # attr type and value pair was DN of LDIF record
          if dn!=None:
            raise ValueError, 'Two lines starting with dn: in one record.'
          if not is_dn(attr_value):
            raise ValueError, 'No valid string-representation of distinguished name %s.' % (repr(attr_value))
          dn = attr_value
        elif attr_type=='version' and dn is None:
          version = 1
        elif attr_type=='changetype':
          # attr type and value pair was DN of LDIF record
          if dn is None:
            raise ValueError, 'Read changetype: before getting valid dn: line.'
          if changetype!=None:
            raise ValueError, 'Two lines starting with changetype: in one record.'
          if not valid_changetype_dict.has_key(attr_value):
            raise ValueError, 'changetype value %s is invalid.' % (repr(attr_value))
          changetype = attr_value
          attr_type, attr_value = self._parseAttrTypeandValue()
          modify_list = []
          entry[changetype] = []
          while (attr_type and attr_value) is not None:
            mod_op = MODIFY_MAPPING_DICT[attr_type]
            mod_type = attr_value
            multivalued_list = []
            while attr_value is not None:
              attr_type, attr_value = self._parseAttrTypeandValue()
              if attr_value is not None:
                multivalued_list.append(attr_value)
            modify_list.append((mod_op, mod_type, multivalued_list))
            entry[changetype] = [modify_list]
            attr_type, attr_value = self._parseAttrTypeandValue()
          #don't add new entry for the same dn
          break
        elif attr_value not in (None, '') and \
             not self._ignored_attr_types.has_key(string.lower(attr_type)):
          # Add the attribute to the entry if not ignored attribute
          if entry.has_key(attr_type):
            entry[attr_type].append(attr_value)
          else:
            entry[attr_type]=[attr_value]

        # Read the next line within an entry
        attr_type, attr_value = self._parseAttrTypeandValue()

      if entry:
        # append entry to result list
        self.handle(dn, entry)
        self.records_read = self.records_read+1

    return # parse()

class Filter(DocumentTemplate.HTML):
    """
    Subclass of DocumentTemplate.HTML for Variable Interpolation.
    Special LDAP Specific tags would go here.  Since there aren't
    any (like ldapvar or ldaptest or whatever), we don't have to worry.
    It's just nice to have a nice name that reflects what this is. :)
    """
    pass

class nvLDIF(DocumentTemplate.HTML):
    # Non-validating Ldif Template for use by LDIFFiles.
    commands={}
    for k, v in DocumentTemplate.HTML.commands.items(): commands[k] = v
    commands['ldifvar' ] = ldifvar.LDIFVar
    commands['ldifline' ] = ldifvar.LDIFLine

    _proxy_roles=()

class Ldif(RestrictedDTML, ExtensionClass.Base, nvLDIF):
    pass

def LDAPConnectionIDs(self):
    """find LDAP connections in the current folder and parents
    Returns list of ids.
    """
    ids={}
    StringType = type('')
    have_key = ids.has_key
    while self is not None:
        if hasattr(self, 'objectValues'):
            for o in self.objectValues():
                if (hasattr(o,'_isAnLDAPConnection')
                    and o._isAnLDAPConnection() and hasattr(o,'id')):
                    id=o.id
                    if type(id) is not StringType: id=id()
                    if not ids.has_key(id):
                        if hasattr(o,'title_and_id'): o=o.title_and_id()
                        else: o=id
                        ids[id]=id
        if hasattr(self, 'aq_parent'): self=self.aq_parent
        else: self=None
    ids=map(lambda item: (item[1], item[0]), ids.items())
    ids.sort()
    return ids

manage_addZLDAPMethodForm = HTMLFile('add', globals())

def manage_addZLDAPMethod(self, id, title, connection_id, scope, basedn, 
                          filters, arguments, getfromconnection=0,
                          REQUEST=None, submit=None):
    """Add an LDAP Method """
    l=LDAPMethod(id, title, connection_id, scope, basedn,
                 arguments, filters)
    self._setObject(id, l)
    if getfromconnection:
        getattr(self,id).recomputeBaseDN()

    if REQUEST is not None:
        u=REQUEST['URL1']
        if submit==" Add and Edit ":
            u="%s/%s/manage_main" % (u,id)
        elif submit==" Add and Test ":
            u="%s/%s/manage_testForm" % (u,id)
        else:
            u=u+'/manage_main'

        REQUEST.RESPONSE.redirect(u)
    return ''




_ldapScopes = { "ONELEVEL": ldap.SCOPE_ONELEVEL,
                "SUBTREE": ldap.SCOPE_SUBTREE,
                "BASE": ldap.SCOPE_BASE }

class LDAPMethod(Aqueduct.BaseQuery,
    Acquisition.Implicit,
    Globals.Persistent,
    AccessControl.Role.RoleManager,
    OFS.SimpleItem.Item,
    ):
    'LDAP Method'

    meta_type = 'LDAP Method'

    manage_main = HTMLFile('edit', globals())
    manage_options = (
        {'label':'Edit', 'action':'manage_main'},
        {'label':'Test', 'action':'manage_testForm'},
        {'label':'Security', 'action':'manage_access'},
        )

    __ac_permissions__=(
        ('View management screens', ('manage_tabs','manage_main',),),
        ('Change LDAP Methods', ('manage_edit',
                                 'manage_testForm','manage_test')),
        ('Use LDAP Methods',    ('__call__',''), ('Anonymous','Manager')),
        )


    #manage_testForm = HTMLFile("testForm", globals())

    def manage_testForm(self, REQUEST):
        " "
        input_src=default_input_form(self.title_or_id(),
                                     self._arg, 'manage_test',
                                     '<!--#var manage_tabs-->')
        return DocumentTemplate.HTML(input_src)(self,REQUEST,HTTP_REFERER='')

    def __init__(self, id, title, connection_id, scope, basedn,
                 arguments, filters):
        """ init method """
        self.id = id
        self.title = title
        self.connection_id = connection_id
        self._scope = _ldapScopes[scope]
        self.scope = scope
        self.basedn = basedn
        self.arguments_src=self.arguments=arguments
        self._arg=parse(arguments)
        self.filters = filters

    def recomputeBaseDN(self):
        ' recompute base DN based on connection '
        cdn=self._connection().dn
        if self.basedn:
            self.basedn='%s, %s' % (self.basedn, cdn)
        else:
            self.basedn=cdn
        return self.basedn

    def manage_edit(self, title, connection_id, scope, basedn,
                    arguments, filters, REQUEST=None):
        """ commit changes """
        self.title = title
        self.connection_id = connection_id
        self._scope = _ldapScopes[scope]
        self.scope = scope
        self.basedn = basedn
        self.arguments_src=self.arguments=arguments
        self._arg=parse(arguments)
        self.filters = filters
        if REQUEST is not None:
            return MessageDialog(
                title='Edited',
                message='<strong>%s</strong> has been changed.' % self.id,
                action ='./manage_main', )

    def cleanse(self,s):
        import string
        # kill line breaks &c.
        s = string.join(string.split(s))
        return s

    def _connection(self):
        ' return actual ZLDAP Connection Object '
        return getattr(self, self.connection_id, None)

    def _getConn(self):
        return self._connection().GetConnection()

    # Hacky, Hacky
    GetConnection=_getConn

    def manage_test(self, REQUEST):
        """ do the test query """
        src="Could not render the filter template!"
        res=()
        t=v=tb=None
        try:
            try:
                src=self(REQUEST, src__=1)
                res=self(REQUEST, tst__=1)
                r=self.prettyResults(res)
            except:
                t, v, tb = sys.exc_info()
                r='<strong>Error, <em>%s</em>:</strong> %s' % (t,v)

            report=DocumentTemplate.HTML(
                '<html><body bgcolor="#ffffff">\n'
                '<!--#var manage_tabs-->\n<hr>%s\n\n'
                '<hr><strong>Filter used:</strong><br>\n<pre>\n%s\n</pre>\n<hr>\n'
                '</body></html>' % (r, src)
                )
            report=apply(report,(self,REQUEST),{self.id:res})

            if tb is not None:
                self.raise_standardErrorMessage(
                    None, REQUEST, t, v, tb, None, report)

            return report

        finally: tb=None

    def prettyResults(self, res):
        s = ""
        if not res or not len(res):
            s = "no results"
        else:
            for dn,attrs in res:
                s = s + ('<ul><li><b>DN: %s</b></li>\n<ul>' % dn)
                s = s + str(pretty_results(attrs=attrs.items()))
                s = s + '</ul></ul>'
        return s

    def __call__(self, REQUEST=None, src__=0, tst__=0, **kw):
        """ call the object """
        if REQUEST is None:
            if kw: REQUEST = kw
            else:
                if getattr(self, 'REQUEST', None) is not None: REQUEST=self.REQUEST
                else: REQUEST={}
        c = self._getConn()
        if not c:
            raise "LDAPError", "LDAP Connection not open"

        if getattr(self, 'aq_parent', None) is not None:
            p = self.aq_parent
        else: p = None

        argdata = self._argdata(REQUEST)  #use our BaseQuery's magic.  :)

        # Also need the authenticated user.
        auth_user = REQUEST.get('AUTHENTICATED_USER', None)
        if auth_user is None:
            auth_user = getattr(self, 'REQUEST', None)
            if auth_user is not None:
                try: auth_user = auth_user.get('AUTHENTICATED_USER', None)
                except: auth_user = None

        if auth_user is not None:
            if getSecurityManager is None:
                # working in a pre-Zope 2.2.x instance
                from AccessControl.User import verify_watermark
                verify_watermark(auth_user)
                argdata['AUTHENTICATED_USER'] = auth_user

        f = Filter(self.filters)        # make a FilterTemplate
        f.cook()
        if getSecurityManager is None:
            # working in a pre-Zope 2.2 instance
            f = apply(f, (p,argdata))       #apply the template
        else:
            # Working with the new security manager (Zope 2.2.x ++)
            security = getSecurityManager()
            security.addContext(self)
            try:     f = apply(f, (p,), argdata)  # apply the template
            finally: security.removeContext(self)

        f = str(f)                      #ensure it's a string
        if src__: return f              #return the rendered source
        f = self.cleanse(f)
        ### run the search
        res = c.search_s(self.basedn, self._scope, f)
        if tst__: return res            #return test-friendly data

        ### instantiate Entry objects based on results
        l = []                          #list of entries to return
        conn=self._connection()         #ZLDAPConnection
        Entry = conn._EntryFactory()
        for dn, attrdict in res:
            e = Entry(dn, attrdict, conn).__of__(self)
            l.append(e)

        return l



manage_addZLDIFMethodForm = HTMLFile('addLdif', globals())

def manage_addZLDIFMethod(self, id, title, connection_id, basedn, arguments, ldif, getfromconnection=0, REQUEST=None, submit=None):
  """Add an LDIF Method """
  l=LDIFMethod(id, title, connection_id, basedn, arguments, ldif)
  self._setObject(id, l)
  if getfromconnection:
    getattr(self,id).recomputeBaseDN()

  if REQUEST is not None:
    u=REQUEST['URL1']
    if submit == " Add and Edit ":
        u = "%s/%s/manage_main" % (u, id)
    elif submit == " Add and Test ":
        u = "%s/%s/manage_testForm" % (u, id)
    else:
        u = u + '/manage_main'

    REQUEST.RESPONSE.redirect(u)
  return ''


class LDIFMethod(LDAPMethod):
  'LDIF Method'

  meta_type = 'LDIF Method'

  manage_main = HTMLFile('editLdif', globals())
  manage_options = (
      {'label':'Edit', 'action':'manage_main'},
      {'label':'Test', 'action':'manage_testForm'},
      {'label':'Security', 'action':'manage_access'},
      )

  __ac_permissions__=(
      ('View management screens', ('manage_tabs', 'manage_main',),),
      ('Change LDAP Methods', ('manage_edit',
                                'manage_testForm', 'manage_test')),
      ('Use LDAP Methods',    ('__call__', ''), ('Anonymous', 'Manager')),
      )

  #manage_testForm = HTMLFile("testLdifForm", globals())



  def __init__(self, id, title, connection_id, basedn, arguments, ldif, **kw):
    """ init method """
    self.id = id
    self.title = title
    self.connection_id = connection_id
    self.basedn = basedn
    self.arguments_src=self.arguments=arguments
    self._arg=parse(arguments)
    self.ldif = str(ldif)


  def manage_edit(self, title, connection_id, basedn, arguments, ldif, REQUEST=None, **kw):
    """ commit changes """
    self.title = title
    self.connection_id = connection_id
    self.basedn = basedn
    self.arguments_src = self.arguments = arguments
    self._arg = parse(arguments)
    self.ldif = str(ldif)
    if REQUEST is not None:
      return MessageDialog(
        title = 'Edited',
        message = '<strong>%s</strong> has been changed.' % self.id,
        action = './manage_main', )

  def __call__(self, REQUEST=None, src__=0, tst__=0, **kw):
    """ call the object """
    if REQUEST is None:
      if kw: REQUEST = kw
      else:
        if hasattr(self, 'REQUEST'): REQUEST = self.REQUEST
        else: REQUEST={}
    c = self._connection().GetConnection()
    if not c:
      raise "LDAPError", "LDAP Connection not open"

    if hasattr(self, 'aq_parent'):
      p = self.aq_parent
    else: p = None

    argdata = self._argdata(REQUEST)  #use our BaseQuery's magic.  :)
    argdata['basedn'] = self.basedn
    # Also need the authenticated user.
    auth_user = REQUEST.get('AUTHENTICATED_USER', None)
    if auth_user is None:
      auth_user = getattr(self, 'REQUEST', None)
      if auth_user is not None:
        try: auth_user = auth_user.get('AUTHENTICATED_USER', None)
        except: auth_user = None

    if auth_user is not None:
      if getSecurityManager is None:
        # working in a pre-Zope 2.2.x instance
        from AccessControl.User import verify_watermark
        verify_watermark(auth_user)
        argdata['AUTHENTICATED_USER'] = auth_user

    ldif = Ldif(self.ldif)        # make a FilterTemplate
    ldif.cook()
    if getSecurityManager is None:
      # working in a pre-Zope 2.2 instance
      ldif = apply(ldif, (p, argdata))       #apply the template
    else:
      # Working with the new security manager (Zope 2.2.x ++)
      security = getSecurityManager()
      security.addContext(self)
      try:     ldif = apply(ldif, (p,), argdata)  # apply the template
      finally: security.removeContext(self)

    ldif = str(ldif)                      #ensure it's a string
    #LOG('ldif', 0, ldif)
    if src__: return ldif              #return the rendered source
    ### Apply Query
    from cStringIO import StringIO
    file = StringIO(ldif)
    l = ERP5LDIFRecordList(file)
    l.parse()
    res = l.all_records

    def delete(c, dn):
      try:
        c.delete_s(dn)
      except ldap.NO_SUCH_OBJECT:
        pass
      except:
        LOG('ldif', INFO, ldif)
        raise

    def add(c, dn, mod_list):
      try:
        c.add_s(dn, mod_list)
      except ldap.ALREADY_EXISTS:
        pass
      except:
        LOG('ldif', INFO, ldif)
        raise

    for record in res:
      dn = record[0]
      entry = record[1]
      if type(entry) == type({}):
        authorized_modify_key = [key for key in entry.keys() if key in CHANGE_TYPES]
        if len(authorized_modify_key):
          for key in authorized_modify_key:
            tuple_list = entry[key]
            if key == 'delete':
              try:
                delete(c, dn)
              except ldap.SERVER_DOWN:
                c = self._connection().getForcedConnection()
                delete(c, dn)
            else:
              for mod_tuple in tuple_list:
                c.modify_s(dn, mod_tuple)
        else:
          mod_list = modlist.addModlist(entry)
          try:
            add(c, dn, mod_list)
          except ldap.SERVER_DOWN:
            c = self._connection().getForcedConnection()
            add(c, dn, mod_list)
      else:
        LOG('LDIFMethod Type unknow', INFO, '')
    return res


class LDAP(LDAPMethod):
    "backwards compatibility.  blech. XXX Delete Me!"

pretty_results=DocumentTemplate.HTML("""\
  <table border="1" cellpadding="2" cellspacing="0" rules="rows" frame="void">
   <dtml-in attrs>
    <tr valign="top">
     <th align="left">&dtml-sequence-key;</th>
     <td><dtml-in name="sequence-item">&dtml-sequence-item;<br /></dtml-in></td>
    </tr>
   </dtml-in>
  </table>""")


import App.class_init
App.class_init.default__class_init__(LDAPMethod)
App.class_init.default__class_init__(LDIFMethod)