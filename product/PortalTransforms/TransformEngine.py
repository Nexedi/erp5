from AccessControl.Role import RoleManager
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Acquisition import aq_parent
from Acquisition import aq_base
from Globals import Persistent
from Globals import InitializeClass
from Globals import PersistentMapping
try:
    from ZODB.PersistentList import PersistentList
except ImportError:
    from persistent.list import PersistentList
from OFS.Folder import Folder
from OFS.SimpleItem import Item

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName

from Products.PortalTransforms.libtransforms.utils import MissingBinary
from Products.PortalTransforms import transforms
from Products.PortalTransforms.interfaces import iengine
from Products.PortalTransforms.interfaces import idatastream
from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.chain import TransformsChain
from Products.PortalTransforms.chain import chain
from Products.PortalTransforms.cache import Cache
from Products.PortalTransforms.Transform import Transform
from Products.PortalTransforms.utils import log
from Products.PortalTransforms.utils import TransformException
from Products.PortalTransforms.utils import BadRequest
from Products.PortalTransforms.utils import _www

__revision__ = '$Id: TransformEngine.py 6255 2006-04-11 15:29:29Z hannosch $'

from logging import DEBUG

class TransformTool(UniqueObject, ActionProviderBase, Folder):

    id        = 'portal_transforms'
    meta_type = id.title().replace('_', ' ')
    isPrincipiaFolderish = 1 # Show up in the ZMI

    __implements__ = iengine

    meta_types = all_meta_types = (
        { 'name'   : 'Transform',
          'action' : 'manage_addTransformForm'},
        { 'name'   : 'TransformsChain',
          'action' : 'manage_addTransformsChainForm'},
        )

    manage_addTransformForm = PageTemplateFile('addTransform', _www)
    manage_addTransformsChainForm = PageTemplateFile('addTransformsChain', _www)
    manage_cacheForm = PageTemplateFile('setCacheTime', _www)
    manage_editTransformationPolicyForm = PageTemplateFile('editTransformationPolicy', _www)
    manage_reloadAllTransforms = PageTemplateFile('reloadAllTransforms', _www)

    manage_options = ((Folder.manage_options[0],) + Folder.manage_options[2:] +
                      (
        { 'label'   : 'Caches',
          'action' : 'manage_cacheForm'},
        { 'label'   : 'Policy',
          'action' : 'manage_editTransformationPolicyForm'},
        { 'label'   : 'Reload transforms',
          'action' : 'manage_reloadAllTransforms'},
        )
                      )

    security = ClassSecurityInfo()

    def __init__(self, policies=None, max_sec_in_cache=3600):
        self._mtmap = PersistentMapping()
        self._policies = policies or PersistentMapping()
        self.max_sec_in_cache = max_sec_in_cache
        self._new_style_pt = 1

    # mimetype oriented conversions (iengine interface) ########################

    def unregisterTransform(self, name):
        """ unregister a transform
        name is the name of a registered transform
        """
        self._unmapTransform(getattr(self, name))
        if name in self.objectIds():
            self._delObject(name)


    def convertTo(self, target_mimetype, orig, data=None, object=None,
                  usedby=None, context=None, **kwargs):
        """Convert orig to a given mimetype

        * orig is an encoded string

        * data an optional idatastream object. If None a new datastream will be
        created and returned

        * optional object argument is the object on which is bound the data.
        If present that object will be used by the engine to bound cached data.

        * additional arguments (kwargs) will be passed to the transformations.
        Some usual arguments are : filename, mimetype, encoding

        return an object implementing idatastream or None if no path has been
        found.
        """
        target_mimetype = str(target_mimetype)

        if object is not None:
            cache = Cache(object)
            data = cache.getCache(target_mimetype)
            if data is not None:
                time, data = data
                if self.max_sec_in_cache == 0 or time < self.max_sec_in_cache:
                    return data

        if data is None:
            data = self._wrap(target_mimetype)

        registry = getToolByName(self, 'mimetypes_registry')

        if not getattr(aq_base(registry), 'classify', None):
            # avoid problems when importing a site with an old mimetype registry
            # XXX return None or orig?
            return None

        orig_mt = registry.classify(orig,
                                    mimetype=kwargs.get('mimetype'),
                                    filename=kwargs.get('filename'))
        orig_mt = str(orig_mt)
        if not orig_mt:
            log('Unable to guess input mime type (filename=%s, mimetype=%s)' %(
                kwargs.get('mimetype'), kwargs.get('filename')), severity=DEBUG)
            return None

        target_mt = registry.lookup(target_mimetype)
        if target_mt:
            target_mt = target_mt[0]
        else:
            log('Unable to match target mime type %s'% str(target_mimetype),
                severity=DEBUG)
            return None

        ## fastpath
        # If orig_mt and target_mt are the same, we only allow
        # a one-hop transform, a.k.a. filter.
        # XXX disabled filtering for now
        filter_only = False
        if orig_mt == str(target_mt):
            filter_only = True
            data.setData(orig)
            md = data.getMetadata()
            md['mimetype'] = str(orig_mt)
            if object is not None:
                cache.setCache(str(target_mimetype), data)
            return data

        ## get a path to output mime type
        requirements = self._policies.get(str(target_mt), [])
        path = self._findPath(orig_mt, target_mt, list(requirements))
        if not path and requirements:
            log('Unable to satisfy requirements %s' % ', '.join(requirements),
                severity=DEBUG)
            path = self._findPath(orig_mt, target_mt)

        if not path:
            log('NO PATH FROM %s TO %s : %s' % (orig_mt, target_mimetype, path),
                severity=DEBUG)
            return None #XXX raise TransformError

        if len(path) > 1:
            ## create a chain on the fly (sly)
            transform = chain()
            for t in path:
                transform.registerTransform(t)
        else:
            transform = path[0]

        result = transform.convert(orig, data, context=context, usedby=usedby, **kwargs)
        assert(idatastream.isImplementedBy(result),
               'result doesn\'t implemented idatastream')
        self._setMetaData(result, transform)

        # set cache if possible
        if object is not None and result.isCacheable():
            cache.setCache(str(target_mimetype), result)

        # return idatastream object
        return result

    security.declarePublic('convertToData')
    def convertToData(self, target_mimetype, orig, data=None, object=None,
                      usedby=None, context=None, **kwargs):
        """Convert to a given mimetype and return the raw data
        ignoring subobjects. see convertTo for more information
        """
        data =self.convertTo(target_mimetype, orig, data, object, usedby,
                       context, **kwargs)
        if data:
            return data.getData()
        return None

    security.declarePublic('convert')
    def convert(self, name, orig, data=None, context=None, **kwargs):
        """run a tranform of a given name on data

        * name is the name of a registered transform

        see convertTo docstring for more info
        """
        if not data:
            data = self._wrap(name)
        try:
            transform = getattr(self, name)
        except AttributeError:
            raise Exception('No such transform "%s"' % name)
        data = transform.convert(orig, data, context=context, **kwargs)
        self._setMetaData(data, transform)
        return data


    def __call__(self, name, orig, data=None, context=None, **kwargs):
        """run a transform by its name, returning the raw data product

        * name is the name of a registered transform.

        return an encoded string.
        see convert docstring for more info on additional arguments.
        """
        data = self.convert(name, orig, data, context, **kwargs)
        return data.getData()


    # utilities ###############################################################

    def _setMetaData(self, datastream, transform):
        """set metadata on datastream according to the given transform
        (mime type and optionaly encoding)
        """
        md = datastream.getMetadata()
        if hasattr(transform, 'output_encoding'):
            md['encoding'] = transform.output_encoding
        md['mimetype'] = transform.output

    def _wrap(self, name):
        """wrap a data object in an icache"""
        return datastream(name)

    def _unwrap(self, data):
        """unwrap data from an icache"""
        if idatastream.isImplementedBy(data):
            data = data.getData()
        return data

    def _mapTransform(self, transform):
        """map transform to internal structures"""
        registry = getToolByName(self, 'mimetypes_registry')
        inputs = getattr(transform, 'inputs', None)
        if not inputs:
            raise TransformException('Bad transform %s : no input MIME type' %
                                     (transform))
        for i in inputs:
            mts = registry.lookup(i)
            if not mts:
                msg = 'Input MIME type %r for transform %s is not registered '\
                      'in the MIME types registry' % (i, transform.name())
                raise TransformException(msg)
            for mti in mts:
                for mt in mti.mimetypes:
                    mt_in = self._mtmap.setdefault(mt, PersistentMapping())
                    output = getattr(transform, 'output', None)
                    if not output:
                        msg = 'Bad transform %s : no output MIME type'
                        raise TransformException(msg % transform.name())
                    mto = registry.lookup(output)
                    if not mto:
                        msg = 'Output MIME type %r for transform %s is not '\
                              'registered in the MIME types registry' % \
                              (output, transform.name())
                        raise TransformException(msg)
                    if len(mto) > 1:
                        msg = 'Wildcarding not allowed in transform\'s output '\
                              'MIME type'
                        raise TransformException(msg)

                    for mt2 in mto[0].mimetypes:
                        try:
                            if not transform in mt_in[mt2]:
                                mt_in[mt2].append(transform)
                        except KeyError:
                            mt_in[mt2] = PersistentList([transform])

    def _unmapTransform(self, transform):
        """unmap transform from internal structures"""
        registry = getToolByName(self, 'mimetypes_registry')
        for i in transform.inputs:
            for mti in registry.lookup(i):
                for mt in mti.mimetypes:
                    mt_in = self._mtmap.get(mt, {})
                    output = transform.output
                    mto = registry.lookup(output)
                    for mt2 in mto[0].mimetypes:
                        l = mt_in[mt2]
                        for i in range(len(l)):
                            if transform.name() == l[i].name():
                                l.pop(i)
                                break
                        else:
                            log('Can\'t find transform %s from %s to %s' % (
                                transform.name(), mti, mt),
                                severity=DEBUG)

    def _findPath(self, orig, target, required_transforms=()):
        """return the shortest path for transformation from orig mimetype to
        target mimetype
        """
        path = []

        if not self._mtmap:
            return None

        # naive algorithm :
        #  find all possible paths with required transforms
        #  take the shortest
        #
        # it should be enough since we should not have so much possible paths
        shortest, winner = 9999, None
        for path in self._getPaths(str(orig), str(target), required_transforms):
            if len(path) < shortest:
                winner = path
                shortest = len(path)

        return winner

    def _getPaths(self, orig, target, requirements, path=None, result=None, searched_orig_list=None):
        """return a all path for transformation from orig mimetype to
        target mimetype
        """
        # don't search the same orig again, otherwise infinite loop occurs.
        if searched_orig_list is None:
            searched_orig_list = []
        if orig in searched_orig_list:
            return result
        else:
            searched_orig_list.append(orig)

        if path is None:
            result = []
            path = []
            requirements = list(requirements)
        outputs = self._mtmap.get(orig)
        if outputs is None:
            return result
        path.append(None)
        for o_mt, transforms in outputs.items():
            for transform in transforms:
                required = 0
                name = transform.name()
                if name in requirements:
                    requirements.remove(name)
                    required = 1
                if transform in path:
                    # avoid infinite loop...
                    continue
                path[-1] = transform
                if o_mt == target:
                    if not requirements:
                        result.append(path[:])
                else:
                    self._getPaths(o_mt, target, requirements, path, result, searched_orig_list)
                if required:
                    requirements.append(name)
        path.pop()

        return result

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """ overload manage_afterAdd to finish initialization when the
        transform tool is added
        """
        Folder.manage_afterAdd(self, item, container)
        transforms.initialize(self)
        # XXX required?
        #try:
        #    # first initialization
        #    transforms.initialize(self)
        #except:
        #    # may fail on copy
        #    pass

    security.declareProtected(ManagePortal, 'manage_addTransform')
    def manage_addTransform(self, id, module, REQUEST=None):
        """ add a new transform to the tool """
        transform = Transform(id, module)
        self._setObject(id, transform)
        self._mapTransform(transform)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    security.declareProtected(ManagePortal, 'manage_addTransform')
    def manage_addTransformsChain(self, id, description, REQUEST=None):
        """ add a new transform to the tool """
        transform = TransformsChain(id, description)
        self._setObject(id, transform)
        self._mapTransform(transform)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    security.declareProtected(ManagePortal, 'manage_addTransform')
    def manage_setCacheValidityTime(self, seconds, REQUEST=None):
        """set  the lifetime of cached data in seconds"""
        self.max_sec_in_cache = int(seconds)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    security.declareProtected(ManagePortal, 'reloadTransforms')
    def reloadTransforms(self, ids=()):
        """ reload transforms with the given ids
        if no ids, reload all registered transforms

        return a list of (transform_id, transform_module) describing reloaded
        transforms
        """
        if not ids:
            ids = self.objectIds()
        reloaded = []
        for id in ids:
            o = getattr(self, id)
            o.reload()
            reloaded.append((id, o.module))
        return reloaded

    # Policy handling methods #################################################

    def manage_addPolicy(self, output_mimetype, required_transforms, REQUEST=None):
        """ add a policy for a given output mime types"""
        registry = getToolByName(self, 'mimetypes_registry')
        if not registry.lookup(output_mimetype):
            raise TransformException('Unknown MIME type')
        if self._policies.has_key(output_mimetype):
            msg = 'A policy for output %s is yet defined' % output_mimetype
            raise TransformException(msg)

        required_transforms = tuple(required_transforms)
        self._policies[output_mimetype] = required_transforms
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_editTransformationPolicyForm')

    def manage_delPolicies(self, outputs, REQUEST=None):
        """ remove policies for given output mime types"""
        for mimetype in outputs:
            del self._policies[mimetype]
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_editTransformationPolicyForm')

    def listPolicies(self):
        """ return the list of defined policies

        a policy is a 2-uple (output_mime_type, [list of required transforms])
        """
        # XXXFIXME: backward compat, should be removed latter
        if not hasattr(self, '_policies'):
            self._policies = PersistentMapping()
        return self._policies.items()

    # mimetype oriented conversions (iengine interface) ########################

    def registerTransform(self, transform):
        """register a new transform

        transform isn't a Zope Transform (the wrapper) but the wrapped transform
        the persistence wrapper will be created here
        """
        # needed when call from transform.transforms.initialize which
        # register non zope transform
        module = str(transform.__module__)
        transform = Transform(transform.name(), module, transform)
        if not itransform.isImplementedBy(transform):
            raise TransformException('%s does not implement itransform' % transform)
        name = transform.name()
        __traceback_info__ = (name, transform)
        if name not in self.objectIds():
            self._setObject(name, transform)
            self._mapTransform(transform)

    security.declareProtected(ManagePortal, 'ZopeFind')
    def ZopeFind(self, *args, **kwargs):
        """Don't break ZopeFind feature when a transform can't be loaded
        """
        try:
            return Folder.ZopeFind(self, *args, **kwargs)
        except MissingBinary:
            log('ZopeFind: catched MissingBinary exception')

    security.declareProtected(View, 'objectItems')
    def objectItems(self, *args, **kwargs):
        """Don't break ZopeFind feature when a transform can't be loaded
        """
        try:
            return Folder.objectItems(self, *args, **kwargs)
        except MissingBinary:
            log('objectItems: catched MissingBinary exception')
            return []

InitializeClass(TransformTool)
