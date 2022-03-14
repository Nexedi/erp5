"""Physically delete the document.

In categories and web sections that are managed by developer or "power users",
there are cases where we want to delete the document. The "logical deletion" is
covered by expired state.

The example use cases of this physical deletion could be to cleanup old categories
that were never used, or to remove a web section so that it causes a 404 error when
clients access (and not a 401 as when it's expired).
"""
document = state_change['object']
document.getParentValue().manage_delObjects(ids=[document.getId()])

raise state_change.ObjectDeleted
