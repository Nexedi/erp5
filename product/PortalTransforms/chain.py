from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Persistence import Persistent
from App.class_init import default__class_init__ as InitializeClass
from Acquisition import Implicit
from OFS.SimpleItem import Item
from AccessControl.Role import RoleManager
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import ManagePortal, ManageProperties
from Products.CMFCore.utils import getToolByName

from Products.PortalTransforms.utils import TransformException, _www
from  Products.PortalTransforms.interfaces import ichain
from  Products.PortalTransforms.interfaces import itransform
from zope.interface import implements

from UserList import UserList

class chain(UserList):
    """A chain of transforms used to transform data"""

    implements(ichain, itransform)

    def __init__(self, name='',*args):
        UserList.__init__(self, *args)
        self.__name__ = name
        if args:
            self._update()

    def name(self):
        return self.__name__

    def registerTransform(self, transform):
        self.append(transform)

    def unregisterTransform(self, name):
        for i in range(len(self)):
            tr = self[i]
            if tr.name() == name:
                self.pop(i)
                break
        else:
            raise Exception('No transform named %s registered' % name)

    def convert(self, orig, data, **kwargs):
        for transform in self:
            data = transform.convert(orig, data, **kwargs)
            orig = data.getData()
        md = data.getMetadata()
        md['mimetype'] = self.output
        return data

    def __setitem__(self, key, value):
        UserList.__setitem__(self, key, value)
        self._update()

    def append(self, value):
        UserList.append(self, value)
        self._update()

    def insert(self, *args):
        UserList.insert(*args)
        self._update()

    def remove(self, *args):
        UserList.remove(*args)
        self._update()

    def pop(self, *args):
        UserList.pop(*args)
        self._update()

    def _update(self):
        self.inputs = self[0].inputs
        self.output = self[-1].output
        for i in range(len(self)):
            if hasattr(self[-i-1], 'output_encoding'):
                self.output_encoding = self[-i-1].output_encoding
                break
        else:
            try:
                del self.output_encoding
            except:
                pass

class TransformsChain(Implicit, Item, RoleManager, Persistent):
    """ a transforms chain is suite of transforms to apply in order.
    It follows the transform API so that a chain is itself a transform.
    """

    meta_type = 'TransformsChain'

    meta_types = all_meta_types = ()

    manage_options = (
                      ({'label':'Configure',
                       'action':'manage_main'},
                       {'label':'Reload',
                       'action':'manage_reloadTransform'},) +
                      Item.manage_options
                      )

    manage_main = PageTemplateFile('editTransformsChain', _www)
    manage_reloadTransform = PageTemplateFile('reloadTransform', _www)

    security = ClassSecurityInfo()

    def __init__(self, id, description, ids=()):
        self.id = id
        self.description = description
        self._object_ids = list(ids)
        self.inputs = ('application/octet-stream',)
        self.output = 'application/octet-stream'
        self._chain = None

    def __setstate__(self, state):
        """ __setstate__ is called whenever the instance is loaded
            from the ZODB, like when Zope is restarted.

            We should rebuild the chain at this time
        """
        TransformsChain.inheritedAttribute('__setstate__')(self, state)
        self._chain = None

    def _chain_init(self):
        """ build the transforms chain """
        tr_tool = getToolByName(self, 'portal_transforms')
        self._chain = c = chain()
        for id in self._object_ids:
            object = getattr(tr_tool, id)
            c.registerTransform(object)
        self.inputs = c.inputs or ('application/octet-stream',)
        self.output = c.output or 'application/octet-stream'

    security.declarePublic('convert')
    def convert(self, *args, **kwargs):
        """ return apply the transform and return the result """
        if self._chain is None:
            self._chain_init()
        return self._chain.convert(*args, **kwargs)

    security.declarePublic('name')
    def name(self):
        """return the name of the transform instance"""
        return self.id

    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        Item.manage_beforeDelete(self, item, container)
        if self is item:
            # unregister self from catalog on deletion
            tr_tool = getToolByName(self, 'portal_transforms')
            tr_tool.unregisterTransform(self.id)

    security.declareProtected(ManagePortal, 'manage_addObject')
    def manage_addObject(self, id, REQUEST=None):
        """ add a new transform or chain to the chain """
        assert id not in self._object_ids
        self._object_ids.append(id)
        self._chain_init()
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    security.declareProtected(ManagePortal, 'manage_delObjects')
    def manage_delObjects(self, ids, REQUEST=None):
        """ delete the selected mime types """
        for id in ids:
            self._object_ids.remove(id)
        self._chain_init()
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


    # transforms order handling #

    security.declareProtected(ManagePortal, 'move_object_to_position')
    def move_object_to_position(self, id, newpos):
        """ overriden from OrderedFolder to store id instead of objects
        """
        oldpos = self._object_ids.index(id)
        if (newpos < 0 or newpos == oldpos or newpos >= len(self._object_ids)):
            return 0
        self._object_ids.pop(oldpos)
        self._object_ids.insert(newpos, id)
        self._chain_init()
        return 1

    security.declareProtected(ManageProperties, 'move_object_up')
    def move_object_up(self, id, REQUEST=None):
        """  move object with the given id up in the list """
        newpos = self._object_ids.index(id) - 1
        self.move_object_to_position(id, newpos)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    security.declareProtected(ManageProperties, 'move_object_down')
    def move_object_down(self, id, REQUEST=None):
        """  move object with the given id down in the list """
        newpos = self._object_ids.index(id) + 1
        self.move_object_to_position(id, newpos)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


    # Z transform interface #

    security.declareProtected(ManagePortal, 'reload')
    def reload(self):
        """ reload the module where the transformation class is defined """
        for tr in self.objectValues():
            tr.reload()


    # utilities #

    security.declareProtected(ManagePortal, 'listAddableObjectIds')
    def listAddableObjectIds(self):
        """ return a list of addable transform """
        tr_tool = getToolByName(self, 'portal_transforms')
        return [id for id in tr_tool.objectIds() if not (id == self.id or id in self._object_ids)]

    security.declareProtected(ManagePortal, 'objectIds')
    def objectIds(self):
        """ return a list of addable transform """
        return tuple(self._object_ids)

    security.declareProtected(ManagePortal, 'objectValues')
    def objectValues(self):
        """ return a list of addable transform """
        tr_tool = getToolByName(self, 'portal_transforms')
        return [getattr(tr_tool, id) for id in self.objectIds()]

InitializeClass(TransformsChain)
