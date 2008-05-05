for member in context.portal_membership.listMembers():
    context.my_mt(
        member=member,
        mto=member.getProperty('email')
        )
