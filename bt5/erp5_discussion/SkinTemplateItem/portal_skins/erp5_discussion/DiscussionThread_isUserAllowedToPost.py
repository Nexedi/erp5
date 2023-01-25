"""
  Evaluate if user is allowed to create new Discussion Post in context.

"""
return context.portal_membership.checkPermission('Add portal content', context) or \
         (context.getValidationState() in ('published', 'published_alive', \
                                          'shared', 'shared_alive', \
                                          'released', 'released_alive',))
