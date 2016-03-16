# It is easier to stay in the transaction as the user can edit lines at the transaction.
return dict(redirect_url=transaction.absolute_url() + '/' + form_id)
