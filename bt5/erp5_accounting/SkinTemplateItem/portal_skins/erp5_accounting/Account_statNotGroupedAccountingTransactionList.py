from Products.PythonScripts.standard import Object
request = container.REQUEST

return [Object(
          debit_price=request.get(
                 'Account_statNotGroupedAccountingTransactionList.total_debit_price'),
          credit_price=request.get(
                 'Account_statNotGroupedAccountingTransactionList.total_credit_price'),
          debit=request.get(
                 'Account_statNotGroupedAccountingTransactionList.total_debit'),
          credit=request.get(
                 'Account_statNotGroupedAccountingTransactionList.total_credit'),)]
