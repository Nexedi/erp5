# This is the default method for a redirection after being added.
redirect_url = '%s/%s' %(context.absolute_url(), 'view')
return dict(redirect_url=redirect_url, selection_index=None, selection_name=None)
