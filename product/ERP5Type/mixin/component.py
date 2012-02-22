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

class ComponentMixin(PropertyRecordableMixin, Base):
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

  security.declareProtected(Permissions.ModifyPortalContent, 'checkConsistency')
  def checkConsistency(self, *args, **kw):
    """
    XXX-arnau: should probably be in a separate Constraint class?
    """
    error_list = []
    object_relative_url = self.getRelativeUrl()

    reference = self.getReference()
    if not reference:
      error_list.append(
        ConsistencyMessage(self,
                           object_relative_url,
                           message="Reference must be set",
                           mapping={}))

    elif (reference.endswith('_version') or
          reference[0] == '_' or
          reference in ('find_module', 'load_module')):
      error_list.append(
        ConsistencyMessage(self,
                           object_relative_url,
                           message="Reference cannot end with '_version' or "\
                             "start with '_' or be equal to find_module or "\
                             "load_module",
                           mapping={}))

    version = self.getVersion()
    if not version:
      error_list.append(ConsistencyMessage(self,
                                           object_relative_url,
                                           message="Version must be set",
                                           mapping={}))
    elif version[0] == '_':
      error_list.append(ConsistencyMessage(self,
                                           object_relative_url,
                                           message="Version cannot start with '_'",
                                           mapping={}))

    text_content = self.getTextContent()
    if not text_content:
      error_list.append(
          ConsistencyMessage(self,
                             object_relative_url=object_relative_url,
                             message="No source code",
                             mapping={}))
    else:
      message = None
      try:
        self.load(text_content=text_content)
      except SyntaxError, e:
        mapping = dict(error_message=str(e),
                       line_number=e.lineno,
                       column_number=e.offset)

        message = "Syntax error in source code: ${error_message} " \
            "(line: ${line_number}, column: ${column_number})"

      except Exception, e:
        mapping = dict(error_message=str(e))
        message = "Source code: ${error_message}"

      if message:
        error_list.append(
          ConsistencyMessage(self,
                             object_relative_url=self.getRelativeUrl(),
                             message=message,
                             mapping=mapping))

    return error_list

  def _recordPropertyDecorator(accessor_name, property_name):
    def inner(self, property_value):
      """
      Everytime either 'reference', 'version' or 'text_content' are
      modified when a Component is in modified or validated state, the
      Component is set to modified state by component interaction
      workflow, then in this method, the current property value is
      recorded in order to handle any error returned when checking
      consistency before the new value is set. At the end, through
      component interaction workflow, the Component is validated only
      if checkConsistency returns no error

      The recorded property will be used upon loading the Component
      whereas the new value set is displayed in Component view.
      """
      if self.getValidationState() in ('modified', 'validated'):
        self.recordProperty(property_name)

      return getattr(super(ComponentMixin, self), accessor_name)(property_value)

    return inner

  security.declareProtected(Permissions.ModifyPortalContent, '_setReference')
  _setReference = _recordPropertyDecorator('_setReference', 'reference')

  security.declareProtected(Permissions.ModifyPortalContent, '_setVersion')
  _setVersion = _recordPropertyDecorator('_setVersion', 'version')

  security.declareProtected(Permissions.ModifyPortalContent, '_setTextContent')
  _setTextContent = _recordPropertyDecorator('_setTextContent', 'text_content')

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
      self.clearRecordedProperty('reference')
      self.clearRecordedProperty('version')
      self.clearRecordedProperty('text_content')
      self.validate()

  def _getRecordedPropertyDecorator(accessor_name, property_name):
    def inner(self, validated_only=False):
      """
      When validated_only is True, then returns the property recorded if the
      Component has been modified but there was an error upon consistency
      checking
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

    return inner

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getReference')
  getReference = _getRecordedPropertyDecorator('getReference', 'reference')

  security.declareProtected(Permissions.AccessContentsInformation, 'getVersion')
  getVersion = _getRecordedPropertyDecorator('getVersion', 'version')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTextContent')
  getTextContent = _getRecordedPropertyDecorator('getTextContent',
                                                 'text_content')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getErrorMessageList')
  def getErrorMessageList(self):
    """
    Return the checkConsistency errors which may have occurred when
    the Component has been modified after being validated once
    """
    current_workflow = self.workflow_history['component_validation_workflow'][-1]
    return [str(error.getTranslatedMessage())
            for error in current_workflow['error_list']]

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

  @staticmethod
  def _getFilesystemPath():
    raise NotImplementedError

  @staticmethod
  def _getDynamicModuleNamespace():
    raise NotImplementedError

  security.declareProtected(Permissions.ModifyPortalContent,
                            'importFromFilesystem')
  @classmethod
  def importFromFilesystem(cls, context, reference, version,
                           erase_existing=False):
    """
    Import a Component from the given path into ZODB after checking that the
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
