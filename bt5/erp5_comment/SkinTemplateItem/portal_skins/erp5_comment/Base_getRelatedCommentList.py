portal = context.getPortalObject()
objectValues = portal.comment_module.objectValues

date = DateTime().strftime('%Y%m%d')
today_set = {x for x in objectValues(base_id=date, checked_permission="View") if x.getFollowUp() == context.getRelativeUrl()}
related_set= {x.getObject() for x in context.getFollowUpRelatedValueList(portal_type="Comment")}
result_list = list(today_set.union(related_set))
result_list.sort(key=lambda x: x.getCreationDate())
return result_list
