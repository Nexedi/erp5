import transaction

def abort_transaction():
    # FIXME: aborting a transaction means it could be commited later on. The
    # transaction should be doom()ed instead, but transaction.doom() is not
    # available on Zope 2.8. We should provide our own doom() implementation
    # which raises an exception on pre-commit-hook, which does exist
    # in Zope 2.8
    transaction.abort()
