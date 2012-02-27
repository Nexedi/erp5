# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#                    Jean-Paul Smets <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

# There is absolutely no reason to use relative imports when loading a Component
from __future__ import absolute_import

from AccessControl import ClassSecurityInfo
from Products.ERP5.mixin.property_recordable import PropertyRecordableMixin
from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage

from zLOG import LOG, INFO

from ExtensionClass import ExtensionClass
from Products.ERP5Type.Utils import convertToUpperCase

class RecordablePropertyMetaClass(ExtensionClass):
  """
  Meta-class for extension classes with registered setters and getters wrapped
  to respectively record and get property through PropertyRecordableMixin
  """
  def __new__(metacls, name, bases, dictionary):
    def setterWrapper(accessor_name, property_name):
      dictionary['security'].declareProtected(Permissions.ModifyPortalContent,
                                              accessor_name)

      def setter(self, property_value):
        """
        Everytime either 'reference', 'version' or 'text_content' are modified
        when a Component is in modified or validated state, the Component is
        set to modified state by dynamic class generation interaction
        workflow, then in this method, the current property value is recorded
        in order to handle any error returned when checking consistency before
        the new value is set. At the end, through dynamic class generation
        interaction workflow, the Component is validated only if
        checkConsistency returns no error

        The recorded property will be used upon loading the Component whereas
        the new value set is displayed in Component view.
        """
        if (self.getValidationState() == 'modified' and
            not self.isPropertyRecorded(property_name)):
          self.recordProperty(property_name)

        return getattr(super(ComponentMixin, self), accessor_name)(property_value)

      setter.__name__ = accessor_name
      return setter

    def getterWrapper(accessor_name, property_name):
      dictionary['security'].declareProtected(Permissions.AccessContentsInformation,
                                              accessor_name)

      def getter(self, validated_only=False):
        """
        When validated_only is True, then returns the property recorded if
        the Component has been modified but there was an error upon
        consistency checking
        """
        if validated_only:
          try:
            return self.getRecordedProperty(property_name)
          # AttributeError when this property has never been recorded before
          # (_recorded_property_dict) and KeyError if the property has been
          # recorded before but is not anymore
          except (AttributeError, KeyError):
            pass

        return getattr(super(ComponentMixin, self), accessor_name)()

      getter.__name__ = accessor_name
      return getter

    for property_name in dictionary['_recorded_property_name_tuple']:
      setter_name = '_set' + convertToUpperCase(property_name)
      dictionary[setter_name] = setterWrapper(setter_name, property_name)

      getter_name = 'get' + convertToUpperCase(property_name)
      dictionary[getter_name] = getterWrapper(getter_name, property_name)

    # docstring required for publishing any object
    dictionary['__doc__'] = metacls.__doc__

    # ExtensionClass required to avoid metaclasses conflicts when
    # ghosting/unghosting Portal Types
    new_class = ExtensionClass.__new__(ExtensionClass,
                                       name,
                                       bases,
                                       dictionary)

    return new_class

class ComponentMixin(PropertyRecordableMixin, Base):
  """
  XXX-arnau: add tests to ERP5 itself to make sure all securities are defined
  properly everywhere (see naming convention test)
  """
  __metaclass__ = RecordablePropertyMetaClass

  isPortalContent = 1
  isRADContent = 1
  isDelivery = ConstantGetter('isDelivery', value=True)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ('Base',
                     'XMLObject',
                     'CategoryCore',
                     'DublinCore',
                     'Version',
                     'Reference',
                     'TextDocument')

  _recorded_property_name_tuple = (
    'reference',
    'version',
    'text_content')

  _message_reference_not_set = "Reference must be set"
  _message_invalid_reference = "Reference cannot end with '_version' or "\
      "start with '_' or be equal to find_module or load_module"

  _message_version_not_set = "Version must be set"
  _message_invalid_version = "Version cannot start with '_'"
  _message_text_content_not_set = "No source code"
  _message_invalid_text_content = "Source code: ${error_message}"
  _message_text_content_syntax_error = "Syntax error in source code: "\
      "${error_message} (line: ${line_number}, column: ${column_number})"

  security.declareProtected(Permissions.ModifyPortalContent, 'checkConsistency')
  def checkConsistency(self, *args, **kw):
    """
    XXX-arnau: should probably be in a separate Constraint class?
    """
    error_list = super(ComponentMixin, self).checkConsistency(*args, **kw)
    object_relative_url = self.getRelativeUrl()

    reference = self.getReference()
    if not reference:
      error_list.append(
        ConsistencyMessage(self,
                           object_relative_url,
                           message=self._message_reference_not_set,
                           mapping={}))

    elif (reference.endswith('_version') or
          reference[0] == '_' or
          reference in ('find_module', 'load_module')):
      error_list.append(
        ConsistencyMessage(self,
                           object_relative_url,
                           message=self._message_invalid_reference,
                           mapping={}))

    version = self.getVersion()
    if not version:
      error_list.append(ConsistencyMessage(self,
                                           object_relative_url,
                                           message=self._message_version_not_set,
                                           mapping={}))
    elif version[0] == '_':
      error_list.append(ConsistencyMessage(self,
                                           object_relative_url,
                                           message=self._message_invalid_version,
                                           mapping={}))

    text_content = self.getTextContent()
    if not text_content:
      error_list.append(
          ConsistencyMessage(self,
                             object_relative_url=object_relative_url,
                             message=self._message_text_content_not_set,
                             mapping={}))
    else:
      message = None
      try:
        self.load(text_content=text_content)
      except SyntaxError, e:
        mapping = dict(error_message=str(e),
                       line_number=e.lineno,
                       column_number=e.offset)

        message = self._message_text_content_syntax_error

      except Exception, e:
        mapping = dict(error_message=str(e))
        message = self._message_invalid_text_content

      if message:
        error_list.append(
          ConsistencyMessage(self,
                             object_relative_url=self.getRelativeUrl(),
                             message=message,
                             mapping=mapping))

    return error_list

  security.declareProtected(Permissions.ModifyPortalContent,
                            'checkConsistencyAndValidate')
  def checkConsistencyAndValidate(self):
    """
    When a Component is in validated or modified validation state and
    it is modified, modified state is set then this checks whether the
    Component can be validated again if checkConsistency returns no
    error
    """
    error_list = self.checkConsistency()
    if error_list:
      workflow = self.workflow_history['component_validation_workflow'][-1]
      workflow['error_list'] = error_list
    else:
      for property_name in self._recorded_property_name_tuple:
        self.clearRecordedProperty(property_name)

      self.validate()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getErrorMessageList')
  def getErrorMessageList(self):
    """
    Return the checkConsistency errors which may have occurred when
    the Component has been modified after being validated once
    """
    current_workflow = self.workflow_history['component_validation_workflow'][-1]
    return [str(error.getTranslatedMessage())
            for error in current_workflow.get('error_list', [])]

  security.declareProtected(Permissions.ModifyPortalContent, 'load')
  def load(self, namespace_dict={}, validated_only=False, text_content=None):
    """
    Load the source code into the given dict. Using exec() rather than
    imp.load_source() as the latter would required creating an intermediary
    file. Also, for traceback readability sake, the destination module
    __dict__ is given rather than creating an empty dict and returning
    it. By default namespace_dict is an empty dict to allow checking the
    source code before validate.
    """
    if text_content is None:
      text_content = self.getTextContent(validated_only=validated_only)

    exec text_content in namespace_dict

  security.declareProtected(Permissions.ModifyPortalContent, 'PUT')
  def PUT(self, REQUEST, RESPONSE):
    """
    Handle HTTP PUT requests for FTP/Webdav upload, which is object
    dependent. For now only set the text content...
    """
    self.dav__init(REQUEST, RESPONSE)
    self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)

    text_content = REQUEST.get('BODY', None)
    if text_content is None:
      RESPONSE.setStatus(304)
    else:
      self.setTextContent(text_content)
      RESPONSE.setStatus(204)

    return RESPONSE

  security.declareProtected(Permissions.ModifyPortalContent, 'manage_FTPput')
  manage_FTPput = PUT

  security.declareProtected(Permissions.AccessContentsInformation,
                            'manage_FTPget')
  def manage_FTPget(self):
    """
    Get source for FTP/Webdav. The default implementation of GET for Webdav,
    available in webdav.Resource, calls manage_FTPget

    XXX-arnau: encoding?
    """
    return self.getTextContent()

  security.declareProtected(Permissions.ModifyPortalContent,
                            'importFromFilesystem')
  @classmethod
  def importFromFilesystem(cls, context, reference, version,
                           erase_existing=False):
    """
    Import a Component from the filesystem into ZODB after checking that the
    source code is valid
    """
    object_id = '%s.%s.%s' % (cls._getDynamicModuleNamespace(), version,
                              reference)

    obj = context._getOb(object_id, None)
    if obj is not None:
      if not erase_existing:
        obj.validate()
        return obj

      context.deleteContent(object_id)

    import os.path
    path = os.path.join(cls._getFilesystemPath(), reference + '.py')
    with open(path) as f:
      source_code = f.read()

    # Checking that the source code is syntactically correct is not
    # needed when importing from filesystem, moreover errors may occur
    # if in the same transaction a Component is created and another
    # one depending upon the former...
    new_component = context.newContent(id=object_id,
                                       reference=reference,
                                       version=version,
                                       text_content=source_code,
                                       portal_type=cls.portal_type)

    # Validate the Component once it is imported so it can be used
    # straightaway as there should be no error
    new_component.validate()

    # XXX-arnau: is it really safe?
    os.remove(path)

    return new_component
