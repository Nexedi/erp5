"""
 Old forum backward compatibility script, wraps new DiscussionForum_createNewDiscussionThread
"""

forum = context.WebSection_getRelatedForum()
web_section = context.getRelativeUrl()
return forum.DiscussionForum_createNewDiscussionThread(title, text_content, form_id, predecessor, description, subject_list, classification, group_list, site_list, send_notification_text, reference, file, web_section, **kw)
