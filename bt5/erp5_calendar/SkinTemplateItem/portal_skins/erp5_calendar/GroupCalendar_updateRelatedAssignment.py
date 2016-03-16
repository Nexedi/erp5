"""
Reindex all related group calendar assignments in case there is
any change. This is needed because group calendar properties affect the
values reindexed in stock by group calendar assignments

We could have possibly millions of assignments linked to the same group
calendar, therefore make sure to use method that would well scale
"""
group_calendar = context
portal = group_calendar.getPortalObject()
portal.portal_catalog.searchAndActivate(method_id="reindexObject",
        activate_kw={'priority': 3},
        specialise_uid=group_calendar.getUid(),
        portal_type="Group Calendar Assignment")
