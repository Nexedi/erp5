"""
Journal entries, for use with AccountingTransactionModule_viewJournal

changed by BG to make a simple list of purchases / sales
("rejestr zakupów" i "rejestr sprzedaży")

return a list of dictionnaries like that : 
  
{
  'date' : Date
  'description' : String
  'reference':String
  'lines' : {
     'debtor' : Bool, 
     'account_gap_id' : String
     'account_name' : String # with extra-description (ie. bank name if a bank, organisation name if an other party)
     'amount' : Float
     }
}
"""

from past.builtins import cmp
request = context.REQUEST
at_date = request['at_date']
transaction_section_category = request['transaction_section_category']
transaction_simulation_state = request['transaction_simulation_state']
transaction_portal_type = request['transaction_portal_type']
from_date = request.get('from_date', None)

params = {
  'sort_on' : 'delivery.stop_date',
  'at_date' : at_date,
  'simulation_state': transaction_simulation_state,
  'section_category' : transaction_section_category,
  'portal_type': transaction_portal_type,
}
if from_date:
  params['from_date'] = from_date

result=[]
for transaction in context\
      .AccountingTransactionModule_zGetAccountingTransactionList(
      selection_params = params, selection=None, **params):
  transaction = transaction.getObject()
  date = transaction.getStopDate() or transaction.getStartDate()
  transaction_dict={'date'       : str(date)[:10], #XXX dangerous for i18n
                    'description':"%s (source reference: %s)"%(
                                    transaction.getTitle() or '',
                                    transaction.getSourceReference() or ''),
                    'reference':transaction.getReference(),
                    }
  result.append(transaction_dict)
  transaction_lines = transaction.contentValues(
    filter = {'portal_type' : [ 'Accounting Transaction Line',
                                'Sale Invoice Transaction Line',
                                'Purchase Invoice Transaction Line',
                                'Pay Sheet Transaction Line',
                                'Balance Transaction Line']})

  transaction_lines.sort(lambda x,y: cmp(y.getObject().getSourceDebit(),
                                         x.getObject().getSourceDebit()))
  for line in transaction_lines :
    line = line.getObject()
    debtor = (line.getSourceDebit() > line.getSourceCredit())
    account = line.getSourceValue()
    # BG: for report, I want both sale and purchase invoices here
    if account is None: account=line.getDestinationValue()
    if account is None: continue
    if account.getAccountType() in ('asset/bank', 'asset/bank/cash') :
      account_description = "%s (%s)"%(
                                    line.getSourceTitle(),
                                    line.getSourcePaymentTitle())
    elif account.getAccountType() in (
                                  'asset/receivable',
                                  'liability/payable'):
      account_description = "%s (%s)"%(
                                    line.getSourceTitle(),
                                    line.getDestinationSectionTitle())
    else :
      account_description = line.getSourceTitle()
    if account.getAccountType() in ('income','expense'):
      transaction_dict['credit']=line.getSourceCredit()
      transaction_dict['credit_gap']=account.getGapId()
    if account.getAccountType() in ('liability/payable/collected_vat','asset/receivable/refundable_vat'):
      transaction_dict['vat']=line.getSourceCredit()+line.getDestinationCredit()


     # internal mouvements, ie when we are destination and source
     # BG: do we need this for PL "rejestr zakupow"?
    if line.getDestinationSection() == line.getSourceSection() :
      debtor = (line.getDestinationDebit() > line.getDestinationCredit())
      account = line.getDestinationValue()
      if account is None : continue
      if account.getAccountType() == 'asset/cash' :
        account_description = "%s (%s)"%(
                                    line.getDestinationTitle(),
                                    line.getDestinationPaymentTitle())
      elif account.getAccountType() in (
                                'asset/receivable',
                                'liability/payable'):
        account_description = "%s (%s)"%(
                                    line.getDestinationTitle(),
                                    line.getSourceSectionTitle())
      else :
        account_description = line.getDestinationTitle()
      lines.append({
          'debtor' : debtor,
          'credit_gap' : account.getGapId(),
          'account_name' : account_description,
          'amount' : debtor  and (line.getDestinationDebit() \
                                      - line.getDestinationCredit()) \
                              or (line.getDestinationCredit() \
                                      - line.getDestinationDebit())
          })
  # to avoid crash if transaction has no lines (can happen while debugging)
  transaction_dict['credit']=transaction_dict.get('credit','')
  transaction_dict['credit_gap']=transaction_dict.get('credit_gap','')
  transaction_dict['vat']=transaction_dict.get('vat','')

return result
# vim: syntax=python
# vim: filetype=python
# vim: shiftwidth=2
