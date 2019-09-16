active_process = context.getPortalObject().restrictedTraverse(active_process_url)
assert len(active_process.getResultList())
