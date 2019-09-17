##############################################################################
#
# Copyright (c) 2002 Nexedi SARL. All Rights Reserved.
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import Acquisition
import traceback
from ZODB.POSException import ConflictError
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityInfo import allow_class
from zLOG import LOG, WARNING
try:
  from Products.CMFActivity.ActiveObject import DEFAULT_ACTIVITY
except ImportError:
  DEFAULT_ACTIVITY = None
_MARKER = []

class ZSQLBrain(Acquisition.Implicit):
  security = ClassSecurityInfo()
  security.declareObjectPublic()

  def _aq_dynamic(self, name):
    """Acquire an attribute from a real object.
    """
    if name.startswith('__') :
      return None
    return getattr(self.getObject(), name, None)

  def getURL(self):
    return self.path

  def getUrl(self):
    return self.path

  def getPath(self):
    return self.path

  def getUid(self):
    return self.uid

  getRID = getUid

  def getObject(self, REQUEST=None):
    """Try to return the object for this record"""
    if 'path' not in dir(self) and 'PATH' not in dir(self):
      raise ValueError, "Unable to getObject from ZSQLBrain if ZSQL Method "\
                  "does not retrieves the `path` column from catalog table."
    obj = self.aq_parent.unrestrictedTraverse(self.getPath())
    if obj is None:
      if REQUEST is None:
        REQUEST = self.REQUEST
      obj = self.aq_parent.portal_catalog.resolve_url(
                                self.getPath(), REQUEST)
    return obj

  def getProperty(self, name, d=_MARKER, **kw):
    value = None
    if hasattr(self, name):
      value = getattr(self, name)
    else:
      if d is not _MARKER:
        kw['d'] = d
      document = self.getObject()
      if document is None:
        raise AttributeError(name)
      value = document.getProperty(name, **kw)
    return value

  def absolute_url(self, relative=0):
    """
      Default method used to return the path stored in the Catalog.
      However, if virtual hosting is implemented, we must return
      a value which is compatible with the standard absolute_url
      behaviour

      And if absolute_url is invoked within a Web Site,
      additional Web Site behaviour is required

      Implementation of absolute_url therefore consists in using
      physicalPathToURL defined in the REQUEST so that absolute_url
      is consistent with HTTPRequest implementation.
    """
    return self.REQUEST.physicalPathToURL(self.path, relative=relative)

  def resolve_url(self, path, REQUEST):
    """
      Taken from ZCatalog

      Attempt to resolve a url into an object in the Zope
      namespace. The url may be absolute or a catalog path
      style url. If no object is found, None is returned.
      No exceptions are raised.
    """
    script = REQUEST.script
    if not path.startswith(script):
      path='%s/%s' % (script, path)
    try:
      return REQUEST.resolve_url(path)
    except ConflictError:
      raise
    except:
      pass

  # If CMFActivity is available, we add ZSQLBrain.activate() that does
  # not call getObject() for better performance and less memory usage.
  if DEFAULT_ACTIVITY is not None:
    def activate(self, activity=DEFAULT_ACTIVITY, active_process=None,
                 activate_kw=None, **kw):
      """
      This method returns an ActiveWrapper without calling getObject().

      See CMFActivity.ActiveObject.activate() for the detail of API.
      """
      try:
        activity_tool = self.aq_parent.getPortalObject().portal_activities
      except AttributeError:
        return self # Do nothing if no portal_activities
      # here we cannot have local default_activate_parameter because
      # we don't want to access the object. if we really need local
      # one, we can just call like brain.getObject().activate()
      # instead.
      new_kw = activity_tool.getDefaultActivateParameterDict(inherit_placeless=False)
      if activate_kw:
        new_kw.update(activate_kw)
      new_kw.update(kw)

      # activate returns an ActiveWrapper
      # a queue can be provided as well as extra parameters
      # which can be used for example to define deferred tasks
      return activity_tool.activateObject(
        self.getPath(), activity, active_process, uid=self.getUid(), **new_kw)

allow_class(ZSQLBrain)

class ZSQLBrainNoObject(ZSQLBrain):
  security = ClassSecurityInfo()
  security.declareObjectPublic()

  def getObject(self):
    stack = ''.join(traceback.format_stack())
    LOG('Products.ZSQLCatalog.Extentions.zsqlbrain.ZSQLBrainNoObject', WARNING,
        "Attempted direct access to object %r:\n%s" % (self.getPath(), stack))
    return None

  def getProperty(self, name, d=_MARKER, **kw):
    value = None
    if hasattr(self, name):
      value = getattr(self, name)
    else:
      stack = ''.join(traceback.format_stack())
      LOG('Products.ZSQLCatalog.Extentions.zsqlbrain.ZSQLBrainNoObject',
          WARNING,
          "Non-existing property %r on record for %r:\n%s" % (name,
                                                              self.getPath(),
                                                              stack))
      return None
    return value

  def _aq_dynamic(self, name):
    """Do not acquire an attribute from a real object.
    """
    stack = ''.join(traceback.format_stack(limit=5))
    LOG('Products.ZSQLCatalog.Extentions.zsqlbrain.ZSQLBrainNoObject', WARNING,
        "Non-existing attribute %r on record for %r:\n%s" % (name,
                                                             self.getPath(),
                                                             stack))
allow_class(ZSQLBrainNoObject)

