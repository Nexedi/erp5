context.log("----------------------------------------------------------DEBUG----------------------------------------------------------------------")
context.log("context relative url:" + context.getRelativeUrl())
context.log("context absolute url:" + context.absolute_url())
portal_status_message = "Post a message"
form_id = 'DiscussionForum_viewProjectForum'
redirect_url = '%s/%s' % (context.absolute_url(), form_id)

return context.Base_redirect(form_id="DiscussionForum_viewNewThreadDialog",
                             redirect_url=redirect_url,
                             predecessor=context.getRelativeUrl(),
                             keep_items = dict(predecessor=context.getRelativeUrl(),
                                               redirect_url=redirect_url,
                                               portal_status_message=context.Base_translateString(portal_status_message)))

#return context.DiscussionForum_viewNewThreadDialog(**kw)

#redirect_url = context.getAbsoluteUrl()
#return context.Base_redirect(redirect_url=redirect_url

#redirect_url = '%s?%s' % ( context.absolute_url()+'/'+form_id, make_query(kw) )
#redirect_url = '%s/%s?%s' % (context.absolute_url(), form_id, url_params)


#return context.Base_redirect(redirect_url=context.DiscussionForum_viewNewThreadDialog(**kw),
#                             keep_items = dict(portal_status_message=context.Base_translateString(portal_status_message)))
