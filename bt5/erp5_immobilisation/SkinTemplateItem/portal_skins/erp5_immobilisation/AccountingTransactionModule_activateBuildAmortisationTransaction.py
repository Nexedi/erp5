from ZTUtils import make_query
form_id='AccountingTransactionModule_viewAccountingTransactionList'
message='Building of Amortisation Transactions in progress...'

context.accounting_module.activate(
           after_tag='expand_amortisation'
         ).AccountingTransactionModule_buildAmortisationTransaction(item_uid_list=item_uid_list,at_date=at_date)


url_params = make_query(form_id=form_id,
                        portal_status_message=message)
redirect_url = '%s/%s?%s' % (context.absolute_url(), form_id, url_params)
context.REQUEST[ 'RESPONSE' ].redirect(redirect_url)
