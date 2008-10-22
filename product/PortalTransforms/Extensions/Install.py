import os
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.DirectoryView import createDirectoryView
from Products.CMFCore.DirectoryView import manage_listAvailableDirectories
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import minimalpath
from Globals import package_home
from Acquisition import aq_base
from OFS.ObjectManager import BadRequestException

from Products.PortalTransforms import GLOBALS
from Products.PortalTransforms import skins_dir

from StringIO import StringIO

def install(self):
    out = StringIO()
    qi=getToolByName(self, 'portal_quickinstaller')
    qi.installProduct('MimetypesRegistry',)
    id = 'portal_transforms'
    if hasattr(aq_base(self), id):
        pt = getattr(self, id)
        if not getattr(aq_base(pt), '_new_style_pt', None) == 1:
            print >>out, 'Removing old portal transforms tool'
            self.manage_delObjects([id,])

    if not hasattr(aq_base(self), id):
        addTool = self.manage_addProduct['PortalTransforms'].manage_addTool
        addTool('Portal Transforms')
        print >>out, 'Installing portal transforms tool'

    updateSafeHtml(self, out)

    correctMapping(self, out)
    # not required right now
    # installSkin(self)
    
    return out.getvalue()

def correctMapping(self, out):

    pt = getToolByName(self, 'portal_transforms')
    pt_ids = pt.objectIds()

    for m_in, m_out_dict in pt._mtmap.items():
        for m_out, transforms in m_out_dict.items():
            for transform in transforms:
                if transform.id not in pt_ids:
                    #error, mapped transform is no object in portal_transforms. correct it!
                    print >>out, "have to unmap transform (%s) cause its not in portal_transforms ..." % transform.id
                    try:
                        pt._unmapTransform(transform)
                    except:
                        raise
                    else:
                        print >>out, "...ok"

def updateSafeHtml(self, out):
    print >>out, 'Update safe_html...'
    safe_html_id = 'safe_html'
    safe_html_module = "Products.PortalTransforms.transforms.safe_html"
    pt = getToolByName(self, 'portal_transforms')
    for id in pt.objectIds():
        transform = getattr(pt, id)
        if transform.id == safe_html_id and transform.module == safe_html_module:
            
            try:
                disable_transform = transform.get_parameter_value('disable_transform')
            except KeyError:
                print >>out, '  replace safe_html (%s, %s) ...' % (transform.name(), transform.module)
                try:
                    pt.unregisterTransform(id)
                    pt.manage_addTransform(id, safe_html_module)
                except:
                    raise
                else:
                    print >>out, '  ...done'
    
    print >>out, '...done'

def installSkin(self):
    skinstool=getToolByName(self, 'portal_skins')

    fullProductSkinsPath = os.path.join(package_home(GLOBALS), skins_dir)
    productSkinsPath = minimalpath(fullProductSkinsPath)
    registered_directories = manage_listAvailableDirectories()
    if productSkinsPath not in registered_directories:
        registerDirectory(skins_dir, GLOBALS)
    try:
        addDirectoryViews(skinstool, skins_dir, GLOBALS)
    except BadRequestException, e:
        pass  # directory view has already been added

    files = os.listdir(fullProductSkinsPath)
    for productSkinName in files:
        if os.path.isdir(os.path.join(fullProductSkinsPath, productSkinName)) \
               and productSkinName != 'CVS':
            for skinName in skinstool.getSkinSelections():
                path = skinstool.getSkinPath(skinName)
                path = [i.strip() for i in  path.split(',')]
                try:
                    if productSkinName not in path:
                        path.insert(path.index('custom') +1, productSkinName)
                except ValueError:
                    if productSkinName not in path:
                        path.append(productSkinName)
                path = ','.join(path)
                skinstool.addSkinSelection(skinName, path)
