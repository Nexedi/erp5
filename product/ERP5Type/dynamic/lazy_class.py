# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002-2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#               2014 Wenjie.Zheng <wenjie.zheng@tiolive.com>
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
import sys

from Products.ERP5Type import Permissions
from Products.ERP5Type.Accessor.Constant import Getter as ConstantGetter
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Base import Base as ERP5Base
from . import aq_method_lock
from Products.ERP5Type.Base import PropertyHolder, initializePortalTypeWorkflowMethods
from Products.ERP5Type.Utils import UpperCase
from Products.ERP5Type.Core.CategoryProperty import CategoryProperty
from ExtensionClass import ExtensionClass, pmc_init_of

from zope.interface import classImplements
from ZODB.broken import Broken, PersistentBroken
from AccessControl import ClassSecurityInfo
from zLOG import LOG, WARNING, BLATHER

from portal_type_class import generatePortalTypeClass
from accessor_holder import AccessorHolderType
import persistent_migration

class ERP5BaseBroken(Broken, ERP5Base):
  # PersistentBroken can't be reused directly
  # because its « layout differs from 'GhostPortalType' »

  def __metaclass__(name, base, d):
    d = dict(PersistentBroken.__dict__, **d)
    for x in '__dict__', '__metaclass__', '__weakref__':
      del d[x]
    def get(x):
      def get(self):
        d = self.__dict__
        try:
          return d.get('__Broken_state__', d)[x]
        except KeyError:
          return getattr(self.__class__, x)
      return property(get)
    for x in 'id', 'title':
      d[x] = get(x)
    return type(name, base, d)

  def __getattr__(self, name):
    try:
      return self.__dict__['__Broken_state__'][name]
    # TypeError: SynchronizationTool => SynchronisationTool
    except (KeyError, TypeError):
      raise AttributeError("state of broken %r object has no %r key"
                           % (self.__class__.__name__, name))

# the meta class of a derived class must be a subclass of all of its bases:
# since a portal type derives from both Zope Extension classes and
# from Accessor Holders, both metaclasses are required, even if
# only ExtensionClass is needed to run the house
class GhostBaseMetaClass(ExtensionClass, AccessorHolderType):
  """
  Generate classes that will be used as bases of portal types to
  mark portal types as non-loaded and to force loading it.
  """

  ghost_doc = """\
  Ghost state for a portal type class that is not loaded.

  When an instance of this portal type class is loaded (a new object is
  created, or an attribute of an existing object is accessed) this class will
  force loading the portal type real inheritance and properties from the ZODB.

  The portal type class will then update its __bases__ so that it points to
  the correct Document+Mixin+interfaces+AccessorHolder classes: after the first
  load, a portal type class does not use GhostPortalType in its __bases__
  anymore.
  """
  def __init__(cls, name, bases, dictionary):
    super(GhostBaseMetaClass, cls).__init__(name, bases, dictionary)

    def __init__(self, *args, **kw):
      self.__class__.loadClass()
      getattr(self, '__init__')(*args, **kw)

    def __getattribute__(self, attr):
      """
      This is only called once to load the class.
      Because __bases__ is changed, the behavior of this object
      will change after the first call.
      """
      # very special case used to bootstrap an instance:
      # calling _setObject() requires accessing the meta_type of the
      # object we're setting, but when creating portal_types it's way
      # too early to load erp5.portal_type.Types Tool
      if attr == "meta_type" and self.__class__.__name__ == "Types Tool":
          return "ERP5 Types Tool"

      # Class must be loaded if '__of__' is requested because otherwise,
      # next call to __getattribute__ would lose any acquisition wrapper.
      if attr in ('__class__',
                  '__getnewargs__',
                  '__getstate__',
                  '__dict__',
                  '__module__',
                  '__name__',
                  '__repr__',
                  '__str__') or attr[:3] in ('_p_', '_v_'):
        return super(cls, self).__getattribute__(attr)
      #LOG("ERP5Type.Dynamic", BLATHER,
      #    "loading attribute %s.%s..." % (name, attr))
      self.__class__.loadClass()
      return getattr(self, attr)

    cls.__getattribute__ = __getattribute__
    cls.__init__ = __init__
    cls.__doc__ = GhostBaseMetaClass.ghost_doc
    # This prevents serialize (ZODB) from reloading the class during commit
    # (which would even trigger migration, resulting in a ConflictError).
    cls.__getnewargs__ = None

InitGhostBase = GhostBaseMetaClass('InitGhostBase', (ERP5Base,), {})

class PortalTypeMetaClass(GhostBaseMetaClass, PropertyHolder):
  """
  Meta class that is used by portal type classes

  - Tracks subclasses of portal type classes
  - Takes care of ghosting/unghosting

  Instances of this metaclass have __isghost__ class attributes.
  - If True, this attribute marks classes awaiting a load from the
    ZODB. An instance of GhostBaseMetaClass should be in the mro()
    and will be removed after loading.
  - If False, the class is fully-loaded and functional.
  """

  # register which classes subclass portal type classes
  subclass_register = {} # XXX ideal defaultdict(list) wannabe

  def __init__(cls, name, bases, dictionary):
    """
    This method is called when a portal type class is
    created, or when a class inheriting a portal type
    class is created
    """
    for parent in bases:
      if issubclass(type(parent), PortalTypeMetaClass):
        PortalTypeMetaClass.subclass_register.setdefault(parent, []).append(cls)

    cls.workflow_method_registry = {}

    cls.__isghost__ = True
    super(GhostBaseMetaClass, cls).__init__(name, bases, dictionary)

    # InitializeClass is evil and removes the security info. Set it up AFTER
    # superclass initialization
    cls.security = ClassSecurityInfo()

  @classmethod
  def getSubclassList(meta_class, cls):
    """
    Returns classes deriving from cls
    """
    return meta_class.subclass_register.get(cls, [])

  def getAccessorHolderPropertyList(cls, content=False):
    """
    Get unique properties, by its id, as defined in the accessor holders,
    meaningful for _propertyMap for example

    Properties whose type is 'content' should not be visible in ZMI
    so they are not returned by default. This would also slow down
    MovementCollectionDiff._getPropertyList (ERP5 product). However,
    ERP5TypeInformation.getInstancePropertyAndBaseCategorySet needs them.

    @see Products.ERP5Type.Base.Base._propertyMap
    """
    cls.loadClass()
    property_dict = {}

    for klass in cls.mro():
      if klass.__module__.startswith('erp5.accessor_holder'):
        for property in klass._properties:
          if content or property['type'] != 'content':
            property_dict.setdefault(property['id'], property)

    return property_dict.itervalues()

  def resetAcquisition(cls):
    # First, fill the __get__ slot of the class
    # that has been null'ed after resetting its __bases__
    # This descriptor is the magic allowing __of__ and our
    # _aq_dynamic trick
    pmc_init_of(cls)

    # And we need to do the same thing on subclasses
    for subclass in PortalTypeMetaClass.getSubclassList(cls):
      pmc_init_of(subclass)

  def setupSecurity(cls):
    apply_security_function = getattr(cls, '_applyAllStaticSecurity', None)
    if apply_security_function:
      apply_security_function()

    # note that after this call the 'security' attribute will be gone.
    InitializeClass(cls)
    for subclass in PortalTypeMetaClass.getSubclassList(cls):
      apply_security_function = getattr(cls, '_applyAllStaticSecurity', None)
      if apply_security_function:
        apply_security_function()

      InitializeClass(subclass)

  def restoreGhostState(cls):
    """
    Insert in the __bases__ hierarchy an instance of GhostBaseMetaClass
    that will force reloading the class.
    - mro before reset:
       erp5.portal_type.XXX, *TAIL
    - after reset:
       erp5.portal_type.XXX, GhostBaseMetaClass instance, *TAIL
    """
    if not cls.__isghost__:
      for attr in cls.__dict__.keys():
        if attr not in ('__module__',
                        '__doc__',
                        '__setstate__',
                        'workflow_method_registry',
                        '__isghost__',
                        'portal_type'):
          delattr(cls, attr)
      # generate a ghostbase that derives from all previous bases
      ghostbase = GhostBaseMetaClass('GhostBase', cls.__bases__, {})
      cls.workflow_method_registry.clear()
      cls.__bases__ = (ghostbase,)
      cls.__isghost__ = True
      cls.resetAcquisition()
      cls.security = ClassSecurityInfo()

  def __getattr__(cls, name):
    """
    Load the class before trying to access a class attribute (for
    example, Standard Property document defines a class method to
    import a filesystem property)
    """
    # Perform the loadClass only on erp5.portal_type classes
    if cls.__module__ != 'erp5.portal_type':
      return getattr(cls.__bases__[0], name)

    if not name.startswith('__') and cls.__isghost__:
      cls.loadClass()
      return getattr(cls, name)

    raise AttributeError("'%r' has no attribute '%s'" % (cls, name))

  def generatePortalTypeAccessors(cls, site, portal_type_category_list):
    category_tool = getattr(site, 'portal_categories', None)
    for category_id in portal_type_category_list:
      # we need to generate only categories defined on portal type
      CategoryProperty.applyDefinitionOnAccessorHolder(cls,
                                                       category_id,
                                                       category_tool)

    portal_workflow = getattr(site, 'portal_workflow', None)
    if portal_workflow is None:
      if not getattr(site, '_v_bootstrapping', False):
        LOG("ERP5Type.Dynamic", WARNING,
            "Could not generate workflow methods for %s"
            % cls.__name__)
    else:
      initializePortalTypeWorkflowMethods(cls, portal_workflow)

    # portal type group methods, isNodeType, isResourceType...
    from Products.ERP5Type.ERP5Type import ERP5TypeInformation
    # XXX possible optimization:
    # generate all methods on Base accessor holder, with all methods
    # returning False, and redefine on portal types only those returning True,
    # aka only those for the group they belong to
    for group in ERP5TypeInformation.defined_group_list:
      value = cls.__name__ in site._getPortalGroupedTypeSet(group)
      accessor_name = 'is' + UpperCase(group) + 'Type'
      method = ConstantGetter(accessor_name, group, value)
      cls.registerAccessor(method, Permissions.AccessContentsInformation)

    from Products.ERP5Type.Cache import initializePortalCachingProperties
    initializePortalCachingProperties(site)

  # TODO in reality much optimization can be done for all
  # PropertyHolder methods:
  # - workflow methods are only on the MetaType erp5.portal_type method
  # Iterating over the complete MRO is nonsense and inefficient
  def _getPropertyHolderItemList(cls):
    cls.loadClass()
    result = PropertyHolder._getPropertyHolderItemList(cls)
    for parent in cls.mro():
      if parent.__module__.startswith('erp5.accessor_holder'):
        for x in parent.__dict__.items():
          if x[0] not in PropertyHolder.RESERVED_PROPERTY_SET:
            result.append(x)
    return result

  def loadClass(cls):
    """
    - mro before load:
      erp5.portal_type.XXX, GhostBaseMetaClass instance, *TAIL
    - mro after:
      erp5.portal_type.XXX, *new_bases_fetched_from_ZODB
    """
    __traceback_info__ = cls.__name__
    # Do not load the class again if it has already been loaded
    if not cls.__isghost__:
      return

    # cls might be a subclass of a portal type class
    # we need to find the right class to change
    for klass in cls.__mro__:
      # XXX hardcoded, this doesnt look too good
      if klass.__module__ == "erp5.portal_type":
        break
    else:
      raise AttributeError("Could not find a portal type class in"
                           " class hierarchy")

    portal_type = klass.__name__
    from Products.ERP5.ERP5Site import getSite
    site = getSite()
    with aq_method_lock:
      try:
        class_definition = generatePortalTypeClass(site, portal_type)
      except AttributeError:
        LOG("ERP5Type.Dynamic", WARNING,
            "Could not access Portal Type Object for type %r"
            % portal_type, error=sys.exc_info())
        base_tuple = (ERP5BaseBroken, )
        portal_type_category_list = []
        attribute_dict = dict(_categories=[], constraints=[])
        interface_list = []
      else:
        base_tuple, portal_type_category_list, \
          interface_list, attribute_dict = class_definition

      klass.__isghost__ = False
      klass.__bases__ = base_tuple

      klass.resetAcquisition()

      for key, value in attribute_dict.iteritems():
        setattr(klass, key, value)

      if getattr(klass.__setstate__, 'im_func', None) is \
         persistent_migration.__setstate__:
        # optimization to reduce overhead of compatibility code
        klass.__setstate__ = persistent_migration.Base__setstate__

      for interface in interface_list:
        classImplements(klass, interface)

      # skip this during the early Base Type / Types Tool generation
      # because they dont have accessors, and will mess up
      # workflow methods. We KNOW that we will re-load this type anyway
      if len(base_tuple) > 1:
        klass.generatePortalTypeAccessors(site, portal_type_category_list)
        # need to set %s__roles__ for generated methods
        cls.setupSecurity()

def generateLazyPortalTypeClass(portal_type_name):
  return PortalTypeMetaClass(portal_type_name,
                             (InitGhostBase,),
                             dict(portal_type=portal_type_name))
