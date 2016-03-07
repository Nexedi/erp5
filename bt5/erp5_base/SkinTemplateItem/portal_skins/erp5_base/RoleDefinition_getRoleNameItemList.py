from Products.ERP5Type.Message import translateString

return [(translateString(role), role)
        for role in context.valid_roles()
        if role not in ('Owner', 'Manager', 'Anonymous', 'Authenticated', 'Member', 'Reviewer',)]
