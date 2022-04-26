"""
PortalTransforms setup handlers.
"""
from __future__ import print_function

from io import StringIO
from Products.CMFCore.utils import getToolByName


def correctMapping(out, portal):
    pt = getToolByName(portal, 'portal_transforms')
    pt_ids = pt.objectIds()

    for m_in, m_out_dict in list(pt._mtmap.items()):
        for m_out, transforms in list(m_out_dict.items()):
            for transform in transforms:
                if transform.id not in pt_ids:
                    #error, mapped transform is no object in portal_transforms. correct it!
                    print("have to unmap transform (%s) cause its not in portal_transforms ..." % transform.id, file=out)
                    try:
                        pt._unmapTransform(transform)
                    except:
                        raise
                    else:
                        print("...ok", file=out)

def updateSafeHtml(out, portal):
    print('Update safe_html...', file=out)
    safe_html_id = 'safe_html'
    safe_html_module = "Products.PortalTransforms.transforms.safe_html"
    pt = getToolByName(portal, 'portal_transforms')
    for id in pt.objectIds():
        transform = getattr(pt, id)
        if transform.id == safe_html_id and transform.module == safe_html_module:
            try:
                disable_transform = transform.get_parameter_value('disable_transform')
            except KeyError:
                print('  replace safe_html (%s, %s) ...' % (transform.name(), transform.module), file=out)
                try:
                    pt.unregisterTransform(id)
                    pt.manage_addTransform(id, safe_html_module)
                except:
                    raise
                else:
                    print('  ...done', file=out)

    print('...done', file=out)


def installPortalTransforms(portal):
    out = StringIO()

    updateSafeHtml(out, portal)

    correctMapping(out, portal)

def setupPortalTransforms(context):
    """
    Setup PortalTransforms step.
    """
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('portal-transforms-various.txt') is None:
        return
    out = []
    site = context.getSite()
    installPortalTransforms(site)

