active_process = context.newActiveProcess().getRelativeUrl()
context.activate(tag=tag).Base_checkSiteDailyModification(active_process=active_process)
context.activate(after_tag=tag).getId()
