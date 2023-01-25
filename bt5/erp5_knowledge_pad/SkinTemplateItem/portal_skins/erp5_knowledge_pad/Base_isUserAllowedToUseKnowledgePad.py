portal = context.getPortalObject()
portal_membership = portal.portal_membership
knowledge_pad_module = portal.restrictedTraverse('knowledge_pad_module',
                                                 default = None)
return knowledge_pad_module is not None and \
       portal_membership.checkPermission('Add portal content',
                                         knowledge_pad_module)
