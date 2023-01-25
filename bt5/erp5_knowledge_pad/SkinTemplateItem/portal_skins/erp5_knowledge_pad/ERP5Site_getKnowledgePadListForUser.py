portal = context.getPortalObject()

# in Web Mode we can have a temporary object created based on current language, document by reference
real_context_url = context.Base_getRealContext().getRelativeUrl()
if mode == 'web_front':
  # Web Site must at least one Pad referenced by context
  filter_pad = lambda x: real_context_url in x.getPublicationSectionList() and x.getGroup() is None
elif mode == 'web_section':
  # Web Sections, Web Pages can "reuse" tabs
  filter_pad = lambda x: real_context_url in x.getPublicationSectionList() or x.getGroup() == default_pad_group
elif mode == 'erp5_front':
  # leave only those not having a publication_section as
  # this means belonging to root
  filter_pad = lambda x: x.getPublicationSection() is None and x.getGroup() is None
else:
  filter_pad = lambda x: 1

results = []
def search(container, *states, **kw):
  # call getObject() explicitly so that further getter methods do not
  # invoke getObject().
  for pad in container.searchFolder(validation_state=states,
                                    portal_type="Knowledge Pad",
                                    sort_on=(("creation_date", "ascending"),),
                                    limit=50, **kw):
    try:
      pad = pad.getObject()
      if filter_pad(pad) and pad.getValidationState() in states:
        results.append(pad)
    except Exception:
      pass

# first for context
search(portal.knowledge_pad_module, 'visible', 'invisible', local_roles='Owner')
if not results:
  request = portal.REQUEST
  if request.get('is_anonymous_knowledge_pad_used', 1):
    # try to get default pads for anonymous users if allowed on site
    search(portal.knowledge_pad_module, 'public')
  if not portal.portal_membership.isAnonymousUser():
    # try getting default knowledge pads for user from global site preference
    user_pref = context.Base_getActiveGlobalKnowledgePadPreference()
    if user_pref is not None:
      # use template from user's preferences
      search(user_pref, 'public')
    if results:
      # set a REQUEST variable (this can be used in HTML views)
      request.set('is_knowledge_pad_template_used', 1)

return results
