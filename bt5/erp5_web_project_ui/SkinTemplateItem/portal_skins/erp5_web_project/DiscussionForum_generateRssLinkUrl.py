"""Return the personal RSS feed URL of this forum in a dialog, so it can be copied."""
context.REQUEST.form["your_rss_url"] = context.DiscussionForum_getRssAccessUrl()
return context.Base_renderForm("DiscussionForum_viewGenerateRssLinkDialog",
                               message="RSS feed URL generated")
