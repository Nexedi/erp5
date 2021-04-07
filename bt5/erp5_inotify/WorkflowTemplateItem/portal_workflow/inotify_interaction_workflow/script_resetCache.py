ob = state_change['object']
if ob.getPortalType() == 'Inotify':
  ob = ob.getParentValue()
if ob.getRelativeUrl() == 'portal_inotify':
  ob.resetCache()
