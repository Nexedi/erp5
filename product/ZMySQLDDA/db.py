##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# Copyright (c) Nexedi SARL 2004.  All rights reserved.
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

from Products.ZMySQLDA.db import *

class DeferredDB(DB):
    """
        An experimental MySQL DA which implements deferred execution
        of SQL code in order to reduce locks and provide better behaviour
        with MyISAM non transactional tables
    """
    
    def __init__(self,connection):
        DB.__init__(self, connection)
        self.sql_string_list = []
                
    def query(self,query_string, max_rows=1000):
        self._use_TM and self._register()
        desc=None
        result=()
        db=self.db
        try:
            self._lock.acquire()
            for qs in filter(None, map(strip,split(query_string, '\0'))):
                qtype = upper(split(qs, None, 1)[0])
                if qtype == "SELECT":
                      raise NotSupportedError, "can not SELECT in deferred connections"
                #LOG('ZMySQLDDA', 0, "insert string %s" % qs )
                self.sql_string_list.append(qs)
        finally:
            self._lock.release()

        return (),()

    def _begin(self, *ignored):
        from thread import get_ident
        self._tlock.acquire()
        self._tthread = get_ident()
        
    def _finish(self, *ignored):
        from thread import get_ident
        if not self._tlock.locked() or self._tthread != get_ident():
            LOG('ZMySQLDA', INFO, "ignoring _finish")
            return
        # BEGIN commit
        LOG('ZMySQLDDA', INFO, "BEGIN commit")
        try:
            if self._transactions:
                self.db.query("BEGIN")
                self.db.store_result()
            if self._mysql_lock:
                self.db.query("SELECT GET_LOCK('%s',0)" % self._mysql_lock)
                self.db.store_result()
        except:
            LOG('ZMySQLDDA', ERROR, "exception during _begin",
                error=sys.exc_info())
            self._tlock.release()
            raise
        # Execute SQL            
        db = self.db
        for qs in self.sql_string_list:
            try:
                db.query(qs)
                c=db.store_result()                       
            except OperationalError, m:
                if m[0] not in hosed_connection: raise
                # Hm. maybe the db is hosed.  Let's restart it.
                db=self.db=apply(self.Database_Connection, (), self.kwargs)
                try:
                    db.query(qs)
                    c=db.store_result()
                except OperationalError, m:
                    raise            
            LOG('ZMySQLDDA', INFO, "Execute %s" % qs)
        # Finish commit             
        LOG('ZMySQLDDA', INFO, "FINISH commit")
        try:
            try:
                if self._mysql_lock:
                    self.db.query("SELECT RELEASE_LOCK('%s')" % self._mysql_lock)
                    self.db.store_result()
                if self._transactions:
                    self.db.query("COMMIT")
                self.db.store_result()
            except:
                LOG('ZMySQLDDA', ERROR, "exception during _finish",
                    error=sys.exc_info())
                raise
        finally:
            self._tlock.release()

    def _abort(self, *ignored):
        from thread import get_ident
        if not self._tlock.locked() or self._tthread != get_ident():
            LOG('ZMySQLDDA', INFO, "ignoring _abort")
            return
        self._tlock.release()          