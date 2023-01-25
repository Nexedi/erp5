"""Redirect user to the path
Parameters:
redirect_path -- Specify where redirect user, use 'paypal.payment.accepted' as default"""

context.REQUEST.RESPONSE.redirect("%s/%s" % (context.Base_getWebSiteSecureUrl(),
                                             redirect_path))
