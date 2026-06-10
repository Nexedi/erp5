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
__doc__='''Generic Database Adapter Package Registration

$Id: __init__.py,v 1.4 2001/08/17 02:17:38 adustman Exp $'''
__version__='$Revision: 1.4 $'[11:-2]

from . import DA
import sys
import types
from . import MySQL as MySQLDA
from . import SQLite as SQLiteDA

# Zope auto-publishes Products.ZSQLDA.misc_ as misc_/ZSQLDA/<key>; both
# backends share the same icon set built from ZSQLDA/icons/.
misc_ = DA.build_misc_()

def initialize(context):
    import Products
    for backend in (MySQLDA, SQLiteDA):
        bt = backend.database_type
        context.registerClass(
            backend.Connection,
            permission="Add Z %s Database Connections" % bt,
            constructors=(getattr(backend, 'manage_addZ%sConnectionForm' % bt),
                          getattr(backend, 'manage_addZ%sConnection' % bt)),
        )
        Products.meta_types += dict(Products.meta_types[-1],
            name=backend.DeferredConnection.meta_type,
            action=None),


# BBB: Allow loading of deferred connections that were created
#      before the merge of ZMySQLDDA into ZMySQLDA.
assert 'Products.ZMySQLDDA' not in sys.modules, \
    "please remove obsolete ZMySQLDDA product"
for m in 'Products.ZMySQLDDA', 'Products.ZMySQLDDA.DA':
    sys.modules[m] = m = types.ModuleType(m)
m.DeferredConnection = MySQLDA.DeferredConnection

# Products.ZMySQLDA was merged into Products.ZSQLDA.MySQL. Objects load as BBB
# subclasses of the real classes and get re-classed in place at site bootstrap
# (see Products.ERP5Type.dynamic.portal_type_class.synchronizeDynamicModules).
for m in 'Products.ZMySQLDA', 'Products.ZMySQLDA.DA':
    sys.modules[m] = m = types.ModuleType(m)
for k in 'Connection', 'DeferredConnection':
    setattr(m, k, type(k, (getattr(MySQLDA, k),), {'__module__': m.__name__}))
del m, k
