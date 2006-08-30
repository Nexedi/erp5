from Products.CMFCore.utils import *
from Products.CMFCore import utils

security.declarePrivate('_getViewFor')
def _getViewFor(obj, view='view'):
    warn('__call__() and view() methods using _getViewFor() as well as '
         '_getViewFor() itself are deprecated and will be removed in CMF 1.6. '
         'Bypass these methods by defining \'(Default)\' and \'view\' Method '
         'Aliases.',
         DeprecationWarning)
    ti = obj.getTypeInfo()

    if ti is not None:

        context = getActionContext( obj )
        actions = ti.listActions()

        for action in actions:
            if action.getId() == view or action.getCategory().endswith('_%s' % view):
                if _verifyActionPermissions( obj, action ):
                    target = action.action(context).strip()
                    if target.startswith('/'):
                        target = target[1:]
                    __traceback_info__ = ( ti.getId(), target )
                    return obj.restrictedTraverse( target )

        # "view" action is not present or not allowed.
        # Find something that's allowed.
        for action in actions:
            if _verifyActionPermissions(obj, action):
                target = action.action(context).strip()
                if target.startswith('/'):
                    target = target[1:]
                __traceback_info__ = ( ti.getId(), target )
                return obj.restrictedTraverse( target )

        raise AccessControl_Unauthorized( 'No accessible views available for '
                                    '%s' % '/'.join( obj.getPhysicalPath() ) )
    else:
        raise NotFound('Cannot find default view for "%s"' %
                            '/'.join(obj.getPhysicalPath()))


utils._getViewFor = _getViewFor