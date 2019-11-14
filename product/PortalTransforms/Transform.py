# -*- coding: utf-8 -*-
from zLOG import ERROR
from UserDict import UserDict

from zope.interface import implements

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from App.class_init import default__class_init__ as InitializeClass
from Persistence import PersistentMapping
from persistent.list import PersistentList
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName

from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.utils import TransformException, log, _www
from Products.PortalTransforms.transforms.broken import BrokenTransform


def import_from_name(module_name):
    """ import and return a module by its name """
    return __import__(module_name, {}, {}, module_name)

def make_config_persistent(kwargs):
    """ iterates on the given dictionnary and replace list by persistent list,
    dictionary by persistent mapping.
    """
    for key, value in kwargs.items():
        if type(value) == type({}):
            p_value = PersistentMapping(value)
            kwargs[key] = p_value
        elif type(value) in (type(()), type([])):
            p_value = PersistentList(value)
            kwargs[key] = p_value

def make_config_nonpersistent(kwargs):
    """ iterates on the given dictionary and replace ListClass by python List,
        and DictClass by python Dict
    """
    for key, value in kwargs.items():
        if isinstance(value, PersistentMapping):
            p_value = dict(value)
            kwargs[key] = p_value
        elif isinstance(value, PersistentList):
            p_value = list(value)
            kwargs[key] = p_value

VALIDATORS = {
    'int' : int,
    'string' : str,
    'list' : PersistentList,
    'dict' : PersistentMapping,
    }

class Transform(SimpleItem):
    """A transform is an external method with
    additional configuration information
    """

    implements(ITransform)

    meta_type = 'Transform'
    meta_types = all_meta_types = ()

    manage_options = (
                      ({'label':'Configure',
                       'action':'manage_main'},
                       {'label':'Reload',
                       'action':'manage_reloadTransform'},) +
                      SimpleItem.manage_options
                      )

    manage_main = PageTemplateFile('configureTransform', _www)
    manage_reloadTransform = PageTemplateFile('reloadTransform', _www)
    tr_widgets = PageTemplateFile('tr_widgets', _www)

    security = ClassSecurityInfo()
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, id, module, transform=None):
        self.id = id
        self.module = module
        # DM 2004-09-09: 'Transform' instances are stored as
        #  part of a module level configuration structure
        #  Therefore, they must not contain persistent objects
        self._config = UserDict()
        self._config.__allow_access_to_unprotected_subobjects__ = 1
        self._config_metadata = UserDict()
        self._tr_init(1, transform)

    def __setstate__(self, state):
        """ __setstate__ is called whenever the instance is loaded
            from the ZODB, like when Zope is restarted.

            We should reload the wrapped transform at this time
        """
        Transform.inheritedAttribute('__setstate__')(self, state)
        self._tr_init()

    def _tr_init(self, set_conf=0, transform=None):
        """ initialize the zope transform by loading the wrapped transform """
        __traceback_info__ = (self.module, )
        if transform is None:
            transform = self._load_transform()
        else:
            self._v_transform = transform
        # check this is a valid transform
        if not hasattr(transform, '__class__'):
            raise TransformException('Invalid transform : transform is not a class')
        if not ITransform.providedBy(transform):
            raise TransformException('Invalid transform : ITransform is not implemented by %s' % transform.__class__)
        if not hasattr(transform, 'inputs'):
            raise TransformException('Invalid transform : missing required "inputs" attribute')
        if not hasattr(transform, 'output'):
            raise TransformException('Invalid transform : missing required "output" attribute')
        # manage configuration
        if set_conf and hasattr(transform, 'config'):
            conf = dict(transform.config)
            self._config.update(conf)
            make_config_persistent(self._config)
            if hasattr(transform, 'config_metadata'):
                conf = dict(transform.config_metadata)
                self._config_metadata.update(conf)
                make_config_persistent(self._config_metadata)
        transform.config = dict(self._config)
        make_config_nonpersistent(transform.config)
        transform.config_metadata = dict(self._config_metadata)
        make_config_nonpersistent(transform.config_metadata)

        self.inputs = transform.inputs
        self.output = transform.output
        self.output_encoding = getattr(transform, 'output_encoding', None)
        return transform

    def _load_transform(self):
        try:
            return self._v_transform
        except AttributeError:
            pass
        try:
            m = import_from_name(self.module)
        except ImportError, err:
            transform = BrokenTransform(self.id, self.module, err)
            msg = "Cannot register transform %s (ImportError), using BrokenTransform: Error\n %s" % (self.id, err)
            self.title = 'BROKEN'
            log(msg, severity=ERROR)
            return transform
        if not hasattr(m, 'register'):
            msg = 'Invalid transform module %s: no register function defined' % self.module
            raise TransformException(msg)
        try:
            transform = m.register()
        except Exception, err:
            transform = BrokenTransform(self.id, self.module, err)
            msg = "Cannot register transform %s, using BrokenTransform: Error\n %s" % (self.id, err)
            self.title = 'BROKEN'
            log(msg, severity=ERROR)
        else:
            self.title = ''
        self._v_transform = transform
        return transform

    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        SimpleItem.manage_beforeDelete(self, item, container)
        if self is item:
            # unregister self from catalog on deletion
            # While building business template, transform tool will be
            # copied and this transform will be removed from copied one
            # so that this must not use getToolByName to retrive the tool.
            tr_tool = self.aq_parent
            tr_tool._unmapTransform(self)

    security.declarePublic('get_documentation')
    def get_documentation(self):
        """ return transform documentation """
        return self._load_transform().__doc__

    security.declarePrivate('convert')
    def convert(self, *args, **kwargs):
        """ return apply the transform and return the result """
        return self._load_transform().convert(*args, **kwargs)

    security.declarePublic('name')
    def name(self):
        """return the name of the transform instance"""
        return self.id

    security.declareProtected(ManagePortal, 'get_parameters')
    def get_parameters(self):
        """ get transform's parameters names """
        return sorted(self._load_transform().config.keys())

    security.declareProtected(ManagePortal, 'get_parameter_value')
    def get_parameter_value(self, key):
        """ get value of a transform's parameter """
        value = self._config[key]
        type = self.get_parameter_infos(key)[0]
        if type == 'dict':
            result = {}
            for key, val in value.items():
                result[key] = val
        elif type == 'list':
            result = list(value)
        else:
            result = value
        return result

    security.declareProtected(ManagePortal, 'get_parameter_infos')
    def get_parameter_infos(self, key):
        """ get informations about a parameter

        return a tuple (type, label, description [, type specific data])
        where type in (string, int, list, dict)
              label and description are two string describing the field
        there may be some additional elements specific to the type :
             (key label, value label) for the dict type
        """
        try:
            return tuple(self._config_metadata[key])
        except KeyError:
            return 'string', '', ''

    security.declareProtected(ManagePortal, 'set_parameters')
    def set_parameters(self, REQUEST=None, **kwargs):
        """ set transform's parameters """
        if not kwargs:
            kwargs = REQUEST.form
        self.preprocess_param(kwargs)
        for param, value in kwargs.items():
            try:
                self.get_parameter_value(param)
            except KeyError:
                log('Warning: ignored parameter %r' % param)
                continue
            meta = self.get_parameter_infos(param)
            self._config[param] = VALIDATORS[meta[0]](value)

        tr_tool = getToolByName(self, 'portal_transforms')
        # need to remap transform if necessary (i.e. configurable inputs / output)
        if kwargs.has_key('inputs') or kwargs.has_key('output'):
            tr_tool._unmapTransform(self)
            transform = self._load_transform()
            self.inputs = kwargs.get('inputs', transform.inputs)
            self.output = kwargs.get('output', transform.output)
            tr_tool._mapTransform(self)
        # track output encoding
        if kwargs.has_key('output_encoding'):
            self.output_encoding = kwargs['output_encoding']
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(tr_tool.absolute_url()+'/manage_main')


    security.declareProtected(ManagePortal, 'reload')
    def reload(self):
        """ reload the module where the transformation class is defined """
        log('Reloading transform %s' % self.module)
        if not self.module.startswith('erp5.'):
            reload(import_from_name(self.module))
        self._tr_init()

    security.declarePrivate('preprocess_param')
    def preprocess_param(self, kwargs):
        """ preprocess param fetched from an http post to handle optional dictionary
        """
        for param in self.get_parameters():
            if self.get_parameter_infos(param)[0] == 'dict':
                try:
                    keys = kwargs[param + '_key']
                    del kwargs[param + '_key']
                except:
                    keys = ()
                try:
                    values = kwargs[param + '_value']
                    del kwargs[param + '_value']
                except:
                    values = ()
                kwargs[param] = dict = {}
                for key, value in zip(keys, values):
                    key = key.strip()
                    if key:
                        value = value.strip()
                        if value:
                            dict[key] = value

InitializeClass(Transform)

