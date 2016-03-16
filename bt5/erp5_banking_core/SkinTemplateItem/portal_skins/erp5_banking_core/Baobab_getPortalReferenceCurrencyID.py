# in this script you must return the default value of the currency for the site
# this must correspond to the id of the currency in the currency_module
return context.getPortalObject().getProperty('reference_currency_id')
