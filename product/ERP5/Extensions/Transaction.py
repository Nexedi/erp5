# def this_transaction():
#     return get_transaction()
# 
# def commit_transaction():
#     get_transaction().commit()

def abort_transaction():
    get_transaction().abort()

# def abort_subtransaction():
#     get_transaction().abort(1)
# 
# def commit_subtransaction():
#     get_transaction().commit(1)
