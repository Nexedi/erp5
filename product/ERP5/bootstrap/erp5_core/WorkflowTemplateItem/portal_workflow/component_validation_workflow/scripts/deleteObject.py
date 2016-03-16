document = state_change['object']
container = document.getParentValue()
container.manage_delObjects(ids=[document.getId()])
