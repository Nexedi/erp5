##############################################################################
#
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
#
# Copyright (c) Digital Creations.  All rights reserved.
#
# This license has been certified as Open Source(tm).
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
#
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
#
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
#
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
#
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
#
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
#
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
#
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
#
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
#
#
# Disclaimer
#
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
#
#
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
#
##############################################################################
database_type='MySQL'
__doc__='''%s Database Connection

$Id: DA.py,v 1.4 2001/08/09 20:16:36 adustman Exp $''' % database_type
__version__='$Revision: 1.4 $'[11:-2]

import os
from collections import defaultdict
from weakref import WeakKeyDictionary
import transaction
import Shared.DC.ZRDB
from App.Dialogs import MessageDialog
from App.special_dtml import HTMLFile
from App.ImageFile import ImageFile
from DateTime import DateTime
from . import DABase
from .db import DB, DeferredDB
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import IS_ZOPE2

SHARED_DC_ZRDB_LOCATION = os.path.dirname(Shared.DC.ZRDB.__file__)

manage_addZMySQLConnectionForm=HTMLFile('connectionAdd',globals())

def manage_addZMySQLConnection(self, id, title, connection_string,
                               check=None, deferred=False, REQUEST=None):
    """Add a MySQL connection to a folder.

    Arguments:
        REQUEST -- The current request
        title -- The title of the ZMySQLDA Connection (string)
        id -- The id of the ZMySQLDA Connection (string)
        connection_string -- see connectionAdd.dtml
    """
    cls = DeferredConnection if deferred else Connection
    connection = cls(id, title, connection_string)
    self._setObject(id, connection)
    if check:
        connection.connect(connection_string)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

# Connection Pool for connections to MySQL.
database_connection_pool = defaultdict(WeakKeyDictionary)

class Connection(DABase.Connection):
    """MySQL Connection Object
    """
    database_type=database_type
    id='%s_database_connection' % database_type
    meta_type=title='Z %s Database Connection' % database_type
    icon='misc_/Z%sDA/conn' % database_type
    security = ClassSecurityInfo()

    manage_properties=HTMLFile('connectionEdit', globals())

    connect_on_load = False

    if not IS_ZOPE2:
      zmi_icon = 'fas fa-database'

    def factory(self): return DB

    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        database_connection_pool.get(self._p_oid, {}).pop(self._p_jar, None)

    def connect(self, s):
        self._v_connected = ''
        if not self._p_oid:
            transaction.savepoint(optimistic=True)
        pool = database_connection_pool[self._p_oid]
        connection = pool.get(self._p_jar)
        DB = self.factory()
        if connection.__class__ is not DB or connection._connection != s:
            connection = pool[self._p_jar] = DB(s)
        self._v_database_connection = connection
        # XXX If date is used as such, it can be wrong because an existing
        # connection may be reused. But this is suposedly only used as a
        # marker to know if connection was successfull.
        self._v_connected = DateTime()
        return self

    def sql_quote__(self, v, escapes={}):
        try:
            connection = self._v_database_connection
        except AttributeError:
            # The volatile attribute sometimes disappears.
            # In this case, re-assign it by calling the connect method.
            # Note that we don't call sql_quote__ recursively by intention,
            # because if connect fails to assign the volatile attribute for
            # any reason, that would generate an infinite loop.
            self.connect(self.connection_string)
            connection = self._v_database_connection
        return connection.string_literal(v)


class DeferredConnection(Connection):
    """
        Experimental MySQL DA which implements
        deferred SQL code execution to reduce locking issues
    """
    meta_type=title='Z %s Deferred Database Connection' % database_type

    def factory(self): return DeferredDB


# BBB: Allow loading of deferred connections that were created
#      before the merge of ZMySQLDDA into ZMySQLDA.
import sys, imp
m = 'Products.ZMySQLDDA'
assert m not in sys.modules, "please remove obsolete ZMySQLDDA product"
sys.modules[m] = imp.new_module(m)
m += '.DA'
sys.modules[m] = m = imp.new_module(m)
m.DeferredConnection = DeferredConnection
del m


__ac_permissions__=(
    ('Add Z MySQL Database Connections',
     ('manage_addZMySQLConnectionForm',
      'manage_addZMySQLConnection')),
    )

misc_={'conn': ImageFile(
    os.path.join(SHARED_DC_ZRDB_LOCATION,'www','DBAdapterFolder_icon.gif'))}

for icon in ('table', 'view', 'stable', 'what',
             'field', 'text','bin','int','float',
             'date','time','datetime'):
    misc_[icon]=ImageFile(os.path.join('icons','%s.gif') % icon, globals())
