"""LDAP Server Connection Package """

import ZLDAP, Entry
__version__ = ZLDAP.__version__


# use the propert product registration
def initialize(context):
    context.registerClass(
        ZLDAP.ZLDAPConnection,
        constructors = (ZLDAP.manage_addZLDAPConnectionForm,
                        ZLDAP.manage_addZLDAPConnection),
        icon = 'LDAP_conn_icon.gif',
        permissions = ('Manage Entry information',
                       'Create New Entry Objects',
                       ),
        )

