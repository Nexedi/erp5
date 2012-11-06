try:
    from zope.traversing import namespace
except ImportError:
    from zope.app.traversing import namespace
try:
    from zope.traversing.interfaces import TraversalError
except ImportError:
    from zope.exceptions import NotFoundError as TraversalError

old_traverse = namespace.view.traverse
def traverse(self, name, ignored):
	if not name:
		raise TraversalError(self.context, name)
	return old_traverse(self, name, ignored)
namespace.view.traverse = traverse
