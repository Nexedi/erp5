from Products.ERP5Type.Accessor.Accessor import Accessor as Method
from Products.ERP5Type.Base import _aq_reset
import Acquisition
from Acquisition import aq_parent
"""
  Current implementation uses callable objects.
  Using decorator would be more modern and consistent with
  recent evolution of python. But we have 2.3 ERP5 users
  so we should, at least, provide both implementations.

  Code structure should be changed so that Interactors
  because a new "type" of ERP5 class such Document
  with a modular plugin structure.

  TODO: multiple instances of interactors could
  use different parameters. This way, interactions
  can be defined on "instances" or can be
  made generic.
"""


class InteractorMethodCall:

  def __init__(self, method, instance, *args, **kw):
    self.instance = instance
    self.args = args
    self.kw = kw
    self.method = method

  def __call__(self):
    # We use self.__dict__['instance'] to prevent inserting the
    # InteractorMethodCall instance in the acquisition chain
    # which has some side effects
    return self.method(self.__dict__['instance'], *self.args, **self.kw)

class InteractorMethod(Method):

  def __init__(self, method):
    self.after_action_list = []
    self.before_action_list = []
    self.method = method
    self.func_code = method.func_code
    self.func_defaults = method.func_defaults

  def registerBeforeAction(self, action, args, kw):
    self.after_action_list.append((action, args, kw))
  
  def registerAfterAction(self, action, args, kw):
    self.after_action_list.append((action, args, kw))

  def __call__(self, instance, *args, **kw):
    method_call_object = InteractorMethodCall(self.method, instance, *args, **kw)
    for action, args, kw in self.before_action_list:
      action(method_call_object, *args, **kw)
    result = method_call_object()
    for action, args, kw in self.after_action_list:
      action(method_call_object, *args, **kw)
    return result

class InteractorSource:

  def __init__(self, method):
    """
      Register method
    """
    self.method = method

  def doAfter(self, action, *args, **kw):
    """
    """
    im_class = self.method.im_class
    if not isinstance(self.method, InteractorMethod):
      # Turn this into an InteractorMethod
      interactor_method = InteractorMethod(self.method)
      setattr(im_class, self.method.__name__, interactor_method)
      self.method = interactor_method
    # Register the action
    self.method.registerAfterAction(action, args, kw)

class Interactor:
  def install(self):
    raise NotImplementedError
  
  def uninstall(self):
    raise NotImplementedError
  
  # Interaction implementation
  def on(self, method):
    """
      Parameters may hold predicates ?
      no need - use InteractorMethodCall and decide on action
    """
    return InteractorSource(method)


## #
## # Experimental part
## #
## class AqDynamicInteractor(Interactor):

##   def install(self):
##     """
##       Installs interactions
##     """
##     from Products.ERP5.Interaction import InteractionDefinition
##     self.on(InteractionDefinition.setProperties).doAfter(self.resetAqDynamic, 1, 2, toto="foo")
##     self.on(InteractionDefinition.addVariable).doAfter(self.resetAqDynamic, 1, 2, toto="foo")

##   def uninstall(self):
##     """
##       Uninstall interactions
##     """

##   # Interaction example
##   def resetAqDynamic(self, method_call_object, a, b, toto=None):
##     """
##       Reset _aq_dynamic
##     """
##     _aq_reset()


## class TypeInteractorExample(Interactor):
##   def __init__(self, portal_type):
##     self.portal_type = portal_type

##   def install(self):
##     from Products.CMFCore.TypesTool import TypesTool
##     self.on(TypesTool.manage_edit).doAfter(self.doSomething)

##   def doSomething(self, method_call_object):
##     if self.portal_type == method_call_object.instance.portal_type:
##       pass
##       # do whatever


## class InteractorOfInteractor(Interactor):

##   def __init__(self, interactor):
##     self.interactor = interactor

##   def install(self):
##     self.on(interactor.doSomething).doAfter(self.doSomething)

##   def doSomething(self, method_call_object):
##     pass

## test = AqDynamicInteractor()
## test.install()


class FieldValueInteractor(Interactor):

  def install(self):
    """
      Installs interactions
    """
    from Products.Formulator.Field import ZMIField
    from Products.ERP5Form.ProxyField import ProxyField
    from Products.Formulator.Form import ZMIForm
    self.on(ZMIField.manage_edit).doAfter(self.purgeFieldValueCache)
    self.on(ZMIField.manage_edit_xmlrpc).doAfter(self.purgeFieldValueCache)
    self.on(ZMIField.manage_tales).doAfter(self.purgeFieldValueCache)
    self.on(ZMIField.manage_tales_xmlrpc).doAfter(self.purgeFieldValueCache)
    self.on(ProxyField.manage_edit).doAfter(self.purgeFieldValueCache)
    self.on(ProxyField.manage_edit_target).doAfter(self.purgeFieldValueCache)
    self.on(ProxyField.manage_tales).doAfter(self.purgeFieldValueCache)
    self.on(ZMIForm.manage_renameObject).doAfter(self.purgeFieldValueCache)

  def uninstall(self):
    """
      Uninstall interactions
    """

  def purgeFieldValueCache(self, method_call_object):
    """
    """
    from Products.ERP5Form import Form, ProxyField
    Form.purgeFieldValueCache()
    ProxyField.purgeFieldValueCache()

class TypeInteractorExample(Interactor):
  def __init__(self, portal_type):
    self.portal_type = portal_type

  def install(self):
    from Products.CMFCore.TypesTool import TypesTool
    self.on(TypesTool.manage_edit).doAfter(self.doSomething)

  def doSomething(self, method_call_object):
    if self.portal_type == method_call_object.instance.portal_type:
      pass
      # do whatever

class InteractorOfInteractor(Interactor):

  def __init__(self, interactor):
    self.interactor = interactor

  def install(self):
    self.on(interactor.doSomething).doAfter(self.doSomething)

  def doSomething(self, method_call_object):
    pass


#test = AqDynamicInteractor()
#test.install()


#interactor_of_interactor = InteractorOfInteractor(test)
#interactor_of_interactor.install()
# This is used in ERP5Form and install method is called in ERP5Form
fielf_value_interactor = FieldValueInteractor()
fielf_value_interactor.install()
