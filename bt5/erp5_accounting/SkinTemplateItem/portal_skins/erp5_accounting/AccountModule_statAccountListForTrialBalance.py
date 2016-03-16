from Products.PythonScripts.standard import Object
request = container.REQUEST

initial_debit_balance = request['TrialBalance.total_initial_debit_balance']
initial_credit_balance = request['TrialBalance.total_initial_credit_balance']
debit = request['TrialBalance.debit']
credit = request['TrialBalance.credit']
final_balance_if_debit = request['TrialBalance.final_balance_if_debit']
final_balance_if_credit = request['TrialBalance.final_balance_if_credit']

return [ Object( initial_debit_balance=initial_debit_balance,
                 initial_credit_balance=initial_credit_balance,
                 initial_balance=initial_debit_balance-initial_credit_balance,
                 debit=debit,
                 credit=credit,
                 final_balance=(initial_debit_balance + debit) - (initial_credit_balance + credit),
                 final_debit_balance=initial_debit_balance + debit,
                 final_credit_balance=initial_credit_balance + credit,
                 final_balance_if_debit=final_balance_if_debit,
                 final_balance_if_credit=final_balance_if_credit ) ]
