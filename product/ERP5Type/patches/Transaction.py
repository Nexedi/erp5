##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import sys

# Adding commit_prepare to the zodb transaction
try:
    from ZODB import Transaction, POSException
    from zLOG import LOG, ERROR
    
    hosed = Transaction.hosed
    hosed_msg = Transaction.hosed_msg
    free_transaction = Transaction.free_transaction
    jar_cmp = Transaction.jar_cmp
    
    def commit(self, subtransaction=None):
        """Finalize the transaction."""
        objects = self._objects
        
        subjars = []
        if subtransaction:
            if self._sub is None:
                # Must store state across multiple subtransactions
                # so that the final commit can commit all subjars.
                self._sub = {}
        else:
            if self._sub is not None:
                # This commit is for a top-level transaction that
                # has previously committed subtransactions.  Do
                # one last subtransaction commit to clear out the
                # current objects, then commit all the subjars.
                if objects:
                    self.commit(1)
                    objects = []
                subjars = self._sub.values()
                subjars.sort(jar_cmp)
                self._sub = None
                
                # If there were any non-subtransaction-aware jars
                # involved in earlier subtransaction commits, we need
                # to add them to the list of jars to commit.
                if self._non_st_objects is not None:
                    objects.extend(self._non_st_objects)
                    self._non_st_objects = None

        if (objects or subjars) and hosed:
            # Something really bad happened and we don't
            # trust the system state.
            raise POSException.TransactionError, hosed_msg

        # It's important that:
        #
        # - Every object in self._objects is either committed or
        #   aborted.
        #
        # - For each object that is committed we call tpc_begin on
        #   it's jar at least once
        #
        # - For every jar for which we've called tpc_begin on, we
        #   either call tpc_abort or tpc_finish. It is OK to call
        #   these multiple times, as the storage is required to ignore
        #   these calls if tpc_begin has not been called.
        #
        # - That we call tpc_begin() in a globally consistent order,
        #   so that concurrent transactions involving multiple storages
        #   do not deadlock.
        try:
            ncommitted = 0
            # Do prepare until number of jars is stable - this could
            # create infinite loop
            jars_len = -1
            jars = self._get_jars(objects, subtransaction)
            objects_len = len(self._objects)
            while len(jars) != jars_len:
                jars_len = len(jars)
                self._commit_prepare(jars, subjars, subtransaction)
                if len(self._objects) != objects_len:
                  objects.extend(self._objects[objects_len:])
                  objects_len = len(self._objects)
                jars = self._get_jars(objects, subtransaction)
            try:
                # If not subtransaction, then jars will be modified.
                self._commit_begin(jars, subjars, subtransaction)
                ncommitted += self._commit_objects(objects)
                if not subtransaction:
                    # Unless this is a really old jar that doesn't
                    # implement tpc_vote(), it must raise an exception
                    # if it can't commit the transaction.
                    for jar in jars:
                        try:
                            vote = jar.tpc_vote
                        except AttributeError:
                            pass
                        else:
                            vote(self)

                # Handle multiple jars separately.  If there are
                # multiple jars and one fails during the finish, we
                # mark this transaction manager as hosed.
                if len(jars) == 1:
                    self._finish_one(jars[0])
                else:
                    self._finish_many(jars)
            except:
                # Ugh, we got an got an error during commit, so we
                # have to clean up.  First save the original exception
                # in case the cleanup process causes another
                # exception.
                error = sys.exc_info()
                try:
                    self._commit_error(objects, ncommitted, jars, subjars)
                except:
                    LOG('ZODB', ERROR,
                        "A storage error occured during transaction "
                        "abort.  This shouldn't happen.",
                        error=error)
                raise error[0], error[1], error[2]
        finally:
            del objects[:] # clear registered
            if not subtransaction and self._id is not None:
                free_transaction()

    def _commit_prepare(self, jars, subjars, subtransaction):
        if subtransaction:
            assert not subjars
            for jar in jars:
                try:
                    jar.tpc_prepare(self, subtransaction)
                except TypeError:
                    # Assume that TypeError means that tpc_begin() only
                    # takes one argument, and that the jar doesn't
                    # support subtransactions.
                    jar.tpc_prepare(self)
                except AttributeError:
                    # Assume that KeyError means that tpc_prepare
                    # not available
                    pass
        else:
            # Merge in all the jars used by one of the subtransactions.
            
            # When the top-level subtransaction commits, the tm must
            # call commit_sub() for each jar involved in one of the
            # subtransactions.  The commit_sub() method should call
            # tpc_begin() on the storage object.
            
            # It must also call tpc_begin() on jars that were used in
            # a subtransaction but don't support subtransactions.
            
            # These operations must be performed on the jars in order.
            
            # Modify jars inplace to include the subjars, too.
            jars += subjars
            jars.sort(jar_cmp)
            # assume that subjars is small, so that it's cheaper to test
            # whether jar in subjars than to make a dict and do has_key.
            for jar in jars:
                #if jar in subjars:
                #  pass
                #else:
                try:
                    jar.tpc_prepare(self)
                except AttributeError:
                    # Assume that KeyError means that tpc_prepare
                    # not available
                    pass

    Transaction.Transaction.commit = commit
    Transaction.Transaction._commit_prepare = _commit_prepare
except ImportError:
    # On Zope 2.8, do not patch Transaction. Instead, we use a before commit hook.
    pass
