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
from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage

from zLOG import LOG, INFO

class Component(Base):
  # CMF Type Definition
  meta_type = 'ERP5 Component'
  portal_type = 'Component'

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
  def checkConsistency(self, text_content=None, *args, **kw):
    """
    XXX-arnau: should probably be in a separate Constraint class?
    """
    if text_content is None:
      text_content = self.getTextContent()

    if not text_content:
      return [ConsistencyMessage(self,
                                 object_relative_url=self.getRelativeUrl(),
                                 message="No source code",
                                 mapping={})]

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
      mapping = dict(message=str(e))
      message = "Source code: ${error_message}"

    if message:
      return [ConsistencyMessage(self,
                                 object_relative_url=self.getRelativeUrl(),
                                 message=message,
                                 mapping=mapping)]

    return []

  security.declareProtected(Permissions.ModifyPortalContent, 'addToRegistry')
  def addToRegistry(self):
    """
    Add the Component to its appropriate module registry
    """
    namespace_fullname = self._getDynamicModuleNamespace()
    namespace_module = __import__(namespace_fullname, {}, {},
                                  fromlist=[namespace_fullname])

    reference = self.getReference()
    namespace_module._registry_dict.setdefault(
      reference, {})[self.getVersion()] = self

  security.declareProtected(Permissions.ModifyPortalContent,
                            'deleteFromRegistry')
  def deleteFromRegistry(self):
    """
    Delete the Component from its appropriate module registry
    """
    namespace_fullname = self._getDynamicModuleNamespace()
    namespace_module = __import__(namespace_fullname, {}, {},
                                  fromlist=[namespace_fullname])

    del namespace_module._registry_dict[self.getReference()]

  def _setTextContent(self, text_content):
    """
    When the validation state is already 'validated', set the new value to
    'text_content_non_validated' property instead of 'text_content' for the
    following reasons:

    1/ It allows to validate the source code through Component validation
       workflow rather than after each edition;

    2/ It avoids dirty hacks to call checkConsistency upon edit and deal with
       error messages, instead use workflow as it makes more sense.

    Then, when the user revalidates the Component through a workflow action,
    'text_content_non_validated' property is copied back to 'text_content'.

    XXX-arnau: the workflow history bit is really ugly and should be moved to
               an interaction workflow instead
    """
    validation_state = self.getValidationState()
    if validation_state in ('validated', 'modified'):
      error_message_list = self.checkConsistency(text_content=text_content)
      if error_message_list:
        self.modified()

        validation_workflow = self.workflow_history['component_validation_workflow']

        last_validation_workflow = validation_workflow[-1]
        last_validation_workflow['error_message'] = error_message_list[0]
        last_validation_workflow['text_content'] = text_content

        previous_validation_workflow = validation_workflow[-2]
        previous_validation_workflow['error_message'] = ''
        previous_validation_workflow['text_content'] = ''
      else:
        super(Component, self)._setTextContent(text_content)
        self.validate()

        if validation_state == 'modified':
          # XXX-arnau: copy/paste
          validation_workflow = self.workflow_history['component_validation_workflow']
          previous_validation_workflow = validation_workflow[-2]
          previous_validation_workflow['error_message'] = ''
          previous_validation_workflow['text_content'] = ''
    else:
      return super(Component, self)._setTextContent(text_content)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTextContent')
  def getTextContent(self, validated_only=False):
    """
    Return the source code of the validated source code (if validated_only is
    True), meaningful when generating the Component, or the non-validated
    source code (when a Component is modified when it has already been
    validated), meaningful when editing a Component or checking consistency
    """
    if not validated_only:
      text_content_non_validated = \
          self.workflow_history['component_validation_workflow'][-1].get('text_content',
                                                                         None)

      if text_content_non_validated:
        return text_content_non_validated

    return super(Component, self).getTextContent()

  def _getErrorMessage(self):
    current_workflow = self.workflow_history['component_validation_workflow'][-1]
    return current_workflow['error_message']

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTranslatedValidationStateTitleWithErrorMessage')
  def getTranslatedValidationStateTitleWithErrorMessage(self):
    validation_state_title = self.getTranslatedValidationStateTitle()
    error_message = self._getErrorMessage()
    if error_message:
      return "%s (%s)" % (validation_state_title,
                          str(error_message.getTranslatedMessage()))

    return validation_state_title

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

    # Try to load it first
    namespace_dict = {}
    exec source_code in namespace_dict

    new_component = context.newContent(id=object_id,
                                       reference=reference,
                                       version=version,
                                       text_content=source_code,
                                       portal_type=cls.portal_type)

    new_component.validate()

    # XXX-arnau: is it really safe?
    os.remove(path)

    return new_component
