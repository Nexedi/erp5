# -*- coding: utf-8 -*-
from logging import DEBUG

from persistent.list import PersistentList
from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from App.class_init import default__class_init__ as InitializeClass
from OFS.Folder import Folder
from Persistence import PersistentMapping
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import registerToolInterface, UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.common import MimeTypeException
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.chain import TransformsChain
from Products.PortalTransforms.chain import chain
from Products.PortalTransforms.interfaces import IDataStream
from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.interfaces import IEngine
from Products.PortalTransforms.interfaces import IPortalTransformsTool
from Products.PortalTransforms.libtransforms.utils import MissingBinary
from Products.PortalTransforms.Transform import Transform
from Products.PortalTransforms.transforms import initialize
from Products.PortalTransforms.utils import log
from Products.PortalTransforms.utils import TransformException
from Products.PortalTransforms.utils import _www
from Products.PortalTransforms.utils import parseContentType


from ZODB.POSException import ConflictError
from zLOG import WARNING

from time import time
from Acquisition import aq_base
_marker = object()
class Cache:

    def __init__(self, obj, context=None, _id='_v_transform_cache'):
        self.obj = obj
        if context is None:
            self.context = obj
        else:
            self.context = context
        self._id =_id

    def _genCacheKey(self, identifier, *args):
        key = identifier
        for arg in args:
            key = '%s_%s' % (key, arg)
        key = key.replace('/', '_')
        key = key.replace('+', '_')
        key = key.replace('-', '_')
        key = key.replace(' ', '_')
        if hasattr(aq_base(self.context), 'absolute_url'):
            return key, self.context.absolute_url()
        return key

    def setCache(self, key, value):
        """cache a value indexed by key"""
        if not value.isCacheable():
            return
        obj = self.obj
        key = self._genCacheKey(key)
        entry = getattr(aq_base(obj), self._id, None)
        if entry is None:
            entry = {}
            setattr(obj, self._id, entry)
        entry[key] = (time(), value)
        return key

    def getCache(self, key):
        """try to get a cached value for key

        return None if not present
        else return a tuple (time spent in cache, value)
        """
        obj = self.obj
        key = self._genCacheKey(key)
        dict = getattr(obj, self._id, None)
        if dict is None :
            return None
        try:
            orig_time, value = dict.get(key, None)
            return time() - orig_time, value
        except TypeError:
            return None

    def purgeCache(self, key=None):
        """Remove cache
        """
        obj = self.obj
        id = self._id
        if getattr(obj, id, _marker) is _marker:
            return
        if key is None:
            delattr(obj, id)
        else:
            cache = getattr(obj, id)
            key = self._genCacheKey(key)
            if cache.has_key(key):
                del cache[key]

class TransformTool(UniqueObject, ActionProviderBase, Folder):

    id = 'portal_transforms'
    meta_type = id.title().replace('_', ' ')
    isPrincipiaFolderish = 1 # Show up in the ZMI

    implements(IPortalTransformsTool, IEngine)

    meta_types = all_meta_types = (
        {'name': 'Transform', 'action': 'manage_addTransformForm'},
        {'name': 'TransformsChain', 'action': 'manage_addTransformsChainForm'},
        )

    manage_addTransformForm = PageTemplateFile('addTransform', _www)
    manage_addTransformsChainForm = PageTemplateFile(
        'addTransformsChain', _www)
    manage_cacheForm = PageTemplateFile('setCacheTime', _www)
    manage_editTransformationPolicyForm = PageTemplateFile(
        'editTransformationPolicy', _www)
    manage_reloadAllTransforms = PageTemplateFile('reloadAllTransforms', _www)

    manage_options = (
        (Folder.manage_options[0], ) + Folder.manage_options[2:] +
        ({'label': 'Caches', 'action': 'manage_cacheForm'},
         {'label': 'Policy', 'action': 'manage_editTransformationPolicyForm'},
         {'label': 'Reload transforms',
          'action': 'manage_reloadAllTransforms'},
        ))

    security = ClassSecurityInfo()

    def __init__(self, policies=None, max_sec_in_cache=3600):
        self._mtmap = PersistentMapping()
        self._policies = policies or PersistentMapping()
        self.max_sec_in_cache = max_sec_in_cache
        self._new_style_pt = 1

    # mimetype oriented conversions (iengine interface)

    security.declarePrivate('unregisterTransform')
    def unregisterTransform(self, name):
        """ unregister a transform
        name is the name of a registered transform
        """
        self._unmapTransform(getattr(self, name))
        if name in self.objectIds():
            self._delObject(name)


    security.declarePrivate('convertTo')
    def convertTo(self, target_mimetype, orig, data=None, object=None,
                  usedby=None, context=None, **kwargs):
        """Convert orig to a given mimetype

        * orig is an encoded string

        * data an optional IDataStream object. If None a new datastream will be
        created and returned

        * optional object argument is the object on which is bound the data.
        If present that object will be used by the engine to bound cached data.

        * additional arguments (kwargs) will be passed to the transformations.
        Some usual arguments are : filename, mimetype, encoding

        return an object implementing IDataStream or None if no path has been
        found.
        """
        target_mimetype = str(target_mimetype)

        if object is not None:
            cache = Cache(object, context=context)
            data = cache.getCache(target_mimetype)
            if data is not None:
                time, data = data
                if self.max_sec_in_cache == 0 or time < self.max_sec_in_cache:
                    return data

        if data is None:
            data = self._wrap(target_mimetype)

        registry = getToolByName(self, 'mimetypes_registry')

        if not getattr(aq_base(registry), 'classify', None):
            # avoid problems when importing a site with an old mimetype
            # registry
            return None

        orig_mt = registry.classify(orig,
                                    mimetype=kwargs.get('mimetype'),
                                    filename=kwargs.get('filename'))
        orig_mt = str(orig_mt)
        if not orig_mt:
            log('Unable to guess input mime type (filename=%s, mimetype=%s)' %
                (kwargs.get('mimetype'), kwargs.get('filename')),
                severity=WARNING)
            return None

        target_mt = registry.lookup(target_mimetype)
        if target_mt:
            target_mt = target_mt[0]
        else:
            log('Unable to match target mime type %s'% str(target_mimetype),
                severity=WARNING)
            return None

        ## fastpath
        # If orig_mt and target_mt are the same, we only allow
        # a one-hop transform, a.k.a. filter.
        # XXX disabled filtering for now
        if orig_mt == str(target_mt):
            data.setData(orig)
            md = data.getMetadata()
            md['mimetype'] = str(orig_mt)
            if object is not None:
                cache.setCache(str(target_mimetype), data)
            return data

        ## get a path to output mime type
        requirements = self.getRequirementListByMimetype(str(orig_mt),
                                                         str(target_mt))
        path = self._findPath(orig_mt, target_mt, list(requirements))
        if not path and requirements:
            log('Unable to satisfy requirements %s' % ', '.join(requirements),
                severity=WARNING)
            path = self._findPath(orig_mt, target_mt)

        if not path:
            log('NO PATH FROM %s TO %s : %s' %
                (orig_mt, target_mimetype, path), severity=WARNING)
            return None

        if len(path) > 1:
            ## create a chain on the fly (sly)
            transform = chain()
            for t in path:
                transform.registerTransform(t)
        else:
            transform = path[0]

        result = transform.convert(orig, data, context=context,
                                   usedby=usedby, **kwargs)
        self._setMetaData(result, transform)

        # set cache if possible
        if object is not None and result.isCacheable():
            cache.setCache(str(target_mimetype), result)

        # return IDataStream object
        return result

    security.declarePrivate('getRequirementListByMimetype')
    def getRequirementListByMimetype(self, origin_mimetype, target_mimetype):
      """Return requirements only if origin_mimetype
      and target_mimetype are matching transform policy

      As an example pdf => text conversion force a transformation
      to intermediate HTML format, because w3m_dump is a requirement
      to output plain/text.
      But we want using pdf_to_text directly.

      So requirements are returned only if
      origin_mimetype and target_mimetype sastify
      the requirement: ie html_to_text is returned
      only if origin_mimetype  == 'text/html' and
      target_mimetype == 'text/plain'
      """
      result_list = []
      candidate_requirement_list = self._policies.get(target_mimetype, [])
      for candidate_requirement in candidate_requirement_list:
        transform = getattr(self, candidate_requirement)
        if origin_mimetype in transform.inputs:
          result_list.append(candidate_requirement)
      return result_list

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
        if IDataStream.providedBy(data):
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
                        msg = ("Wildcarding not allowed in transform's output "
                               "MIME type")
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
                    try:
                        mt_in = self._mtmap[mt]
                    except KeyError:
                        continue
                    output = transform.output
                    mto = registry.lookup(output)
                    for mt2 in mto[0].mimetypes:
                        try:
                            l = mt_in[mt2]
                        except KeyError:
                            continue
                        for i in range(len(l)):
                            if transform.name() == l[i].name():
                                l.pop(i)
                                break
                        else:
                            log('Can\'t find transform %s from %s to %s' % (
                                transform.name(), mti, mt),
                                severity=WARNING)

    def _findPath(self, orig, target, required_transforms=()):
        """return the shortest path for transformation from orig mimetype to
        target mimetype
        """
        if not self._mtmap:
            return None

        orig = str(orig)
        target = str(target)
        # First, let's deal with required transforms.
        if required_transforms:
            # Let's decompose paths, then.
            required_transform = required_transforms.pop(0)
            # The first path must lead to one of the inputs supported
            # by this first required transform.
            # Which input types are supported by this transform ?
            supportedInputs = {}
            for input, outputs in self._mtmap.items():
                for output, transforms in outputs.items():
                    for transform in transforms:
                        if transform.name() == required_transform:
                            supportedInputs[input] = 'ok'
                            # BTW, let's remember the output type
                            transformOutput = output
                            # and remember the transform, it is
                            # useful later
                            requiredTransform = transform
            # Which of these inputs will be reachable with the
            # shortest path ?
            shortest = 9999 # big enough, I guess
            shortestFirstPath = None
            for supportedInput in supportedInputs.keys():
                # We start from orig
                firstOrig = orig
                # And want to reach supportedInput
                firstTarget = supportedInput
                # What's the shortest path ?
                firstPath = self._findPath(firstOrig, firstTarget)
                if firstPath is not None:
                    if len(firstPath) < shortest:
                        # Here is a path which is shorter than others
                        # which also reach the required transform.
                        shortest = len(firstPath)
                        shortestFirstPath = firstPath
            if shortestFirstPath == None:
                return None # there is no path leading to this transform
            # Then we have to take this transform.
            secondPath = [requiredTransform]
            # From the output of this transform, we then have to
            # reach our target, possible through other required
            # transforms.
            thirdOrig = transformOutput
            thirdTarget = target
            thirdPath = self._findPath(thirdOrig, thirdTarget,
                                       required_transforms)
            if thirdPath is None:
                return None # no path
            # Final result is the concatenation of these 3 parts
            return shortestFirstPath + secondPath + thirdPath

        if orig == target:
            return []

        # Now let's efficiently find the shortest path from orig
        # to target (without required transforms).
        # The overall idea is that we build all possible paths
        # starting from orig and of given length. And we increment
        # this length until one of these paths reaches our target or
        # until all reachable types have been reached.
        currentPathLength = 0
        pathToType = {orig: []} # all paths we know, by end of path.
        def typesWithPathOfLength(length):
            '''Returns the lists of known paths of a given length'''
            result = []
            for type_, path in pathToType.items():
                if len(path) == length:
                    result.append(type_)
            return result
        # We will start exploring paths which start from types
        # reachable in zero steps. That is paths which start from
        # orig.
        typesToStartFrom = typesWithPathOfLength(currentPathLength)
        # Explore paths while there are new paths to be explored
        while len(typesToStartFrom) > 0:
            for startingType in typesToStartFrom:
                # Where can we go in one step starting from here ?
                outputs = self._mtmap.get(startingType)
                if outputs:
                    for reachedType, transforms in outputs.items():
                        # Does this lead to a type we never reached before ?
                        if reachedType not in pathToType.keys() and transforms:
                            # Yes, we did not know any path reaching this type
                            # Let's remember the path to here
                            pathToType[reachedType] = (
                                pathToType[startingType] + [transforms[0]])
                            if reachedType == target:
                                # This is the first time we reach our target.
                                # We have our shortest path to target.
                                return pathToType[target]
            # We explored all possible paths of length currentPathLength
            # Let's increment that length.
            currentPathLength += 1
            # What are the next types to start from ?
            typesToStartFrom = typesWithPathOfLength(currentPathLength)
        # We are done exploring paths starting from orig
        # and this exploration did not reach our target.
        # Hence there is no path from orig to target.
        return None

    def _getPaths(self, orig, target, requirements, path=None, result=None):
        """return some of the paths for transformation from orig mimetype to
        target mimetype with the guarantee that the shortest path is included.
        If target is the same as orig, then returns an empty path.
        """

        shortest = 9999
        if result:
            for okPath in result:
                shortest = min(shortest, len(okPath))

        if orig == target:
            return [[]]
        if path is None:
            result = []
            path = []
            requirements = list(requirements)
        outputs = self._mtmap.get(orig)
        if outputs is None:
            return result

        registry = getToolByName(self, 'mimetypes_registry')
        mto = registry.lookup(target)
        # target mimetype aliases
        target_aliases = mto[0].mimetypes

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
                if o_mt in target_aliases:
                    if not requirements:
                        result.append(path[:])
                        if len(path[:]) < shortest:
                            # here is a shorter one !
                            shortest = len(path)
                else:
                    if len(path) < shortest:
                        # keep exploring this path, it is still short enough
                        self._getPaths(o_mt, target, requirements,
                                       path, result)
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
        try:
            initialize(self)
        except TransformException:
            # may fail on copy or zexp import
            pass

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
            try:
                self._unmapTransform(o)
            except MimeTypeException:
                pass
            try:
                self._mapTransform(o)
            except MimeTypeException:
                pass
        return reloaded

    # Policy handling methods

    def manage_addPolicy(self, output_mimetype, required_transforms,
                         REQUEST=None):
        """ add a policy for a given output mime types"""
        registry = getToolByName(self, 'mimetypes_registry')
        if not registry.lookup(output_mimetype):
            raise TransformException('Unknown MIME type')
        if output_mimetype in self._policies:
            msg = 'A policy for output %s is yet defined' % output_mimetype
            raise TransformException(msg)

        required_transforms = tuple(required_transforms)
        self._policies[output_mimetype] = required_transforms
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url() +
                '/manage_editTransformationPolicyForm')

    def manage_delPolicies(self, outputs, REQUEST=None):
        """ remove policies for given output mime types"""
        for mimetype in outputs:
            del self._policies[mimetype]
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url() +
                '/manage_editTransformationPolicyForm')

    security.declareProtected(View, 'listPolicies')
    def listPolicies(self):
        """ return the list of defined policies

        a policy is a 2-uple (output_mime_type, [list of required transforms])
        """
        # XXXFIXME: backward compat, should be removed latter
        if not hasattr(self, '_policies'):
            self._policies = PersistentMapping()
        return self._policies.items()

    # mimetype oriented conversions (iengine interface)

    security.declarePrivate('registerTransform')
    def registerTransform(self, transform):
        """register a new transform

        transform isn't a Zope Transform (the wrapper) but the wrapped
        transform the persistence wrapper will be created here
        """
        # needed when call from transform.transforms.initialize which
        # register non zope transform
        module = str(transform.__module__)
        transform = Transform(transform.name(), module, transform)
        if not ITransform.providedBy(transform):
            raise TransformException('%s does not implement ITransform' %
                                     transform)
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

    # available mimetypes ####################################################
    security.declarePrivate('listAvailableTextInputs')
    def listAvailableTextInputs(self):
        """Returns a list of mimetypes that can be used as input for textfields
        by building a list of the inputs beginning with "text/" of all
        transforms.
        """
        available_types = []
        candidate_transforms = [object[1] for object in self.objectItems()]
        for candidate in candidate_transforms:
            for input in candidate.inputs:
                if input.startswith("text/") and input not in available_types:
                    available_types.append(input)
        return available_types

    security.declarePublic('getAvailableTargetMimetypeList')
    def getAvailableTargetMimetypeList(self, source_mimetype):
        """
          Returns a list of mimetypes that can be used as target for
          `source_mimetype` conversion.
        """

        # clean up mimetype from its useless characters
        source_mimetype = parseContentType(source_mimetype)
        source_mimetype = ";".join([source_mimetype.gettype()] + source_mimetype.getplist())

        # fill dict that will contain all possible conversion for each mimetype
        input_output_dict = {} # {"application/pdf": set(["text/html", "application/msword", ...])}
        for obj in self.objectValues():
            for input_ in obj.inputs:
                if input_ in input_output_dict:
                    input_output_dict[input_].add(obj.output)
                else:
                    input_output_dict[input_] = set([obj.output])

        # browse mimetypes to fill result_set of available target mimetypes
        result_set = set([source_mimetype])
        browsing_list = [source_mimetype]
        input_output_items = input_output_dict.items()
        while len(browsing_list):
            browsing_mimetype = browsing_list.pop()
            for mimetype, output_mimetype_set in input_output_items:
                if (browsing_mimetype == mimetype or
                    (mimetype.endswith("/*") and
                     browsing_mimetype[:len(mimetype[:-1])] == mimetype[:-1])
                        ):
                    for output_mimetype in output_mimetype_set:
                        if output_mimetype not in result_set:
                            result_set.add(output_mimetype)
                            browsing_list.append(output_mimetype)

        result_set.remove(source_mimetype)
        return list(result_set)

InitializeClass(TransformTool)
registerToolInterface('portal_transforms', IPortalTransformsTool)
