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
from Acquisition import aq_base
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5.mixin.property_recordable import PropertyRecordableMixin
from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.Accessor import Base as BaseAccessor
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
from zExceptions import Forbidden

from zLOG import LOG, INFO

from ExtensionClass import ExtensionClass
from Products.ERP5Type.Utils import convertToUpperCase, checkPythonSourceCode

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

    def getterWrapper(accessor_name, property_name, property_getter):
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

        return property_getter(self)

      getter.__name__ = accessor_name
      return getter

    for (property_name,
         property_getter) in dictionary['_recorded_property_name_getter_dict'].iteritems():
      setter_name = '_set' + convertToUpperCase(property_name)
      dictionary[setter_name] = setterWrapper(setter_name, property_name)

      getter_name = 'get' + convertToUpperCase(property_name)
      dictionary[getter_name] = getterWrapper(getter_name, property_name,
                                              property_getter)

    # docstring required for publishing any object
    dictionary['__doc__'] = metacls.__doc__

    # ExtensionClass required to avoid metaclasses conflicts when
    # ghosting/unghosting Portal Types
    return ExtensionClass.__new__(ExtensionClass, name, bases, dictionary)

class ComponentMixin(PropertyRecordableMixin, Base):
  """
  Mixin used for all ZODB Components. Most of the code is generic, thus actual
  ZODB Components should have almost nothing to defined...

  From a security point of view, only Developer Role defined on Component Tool
  can manage Components (as exec is used and anything potentially damaging
  could be done on the filesystem), while only Manager or Developer Roles can
  reset Component Packages (see ERP5Type.Permissions). All the permissions are
  defined on Component Tool itself and newly created Components just inherits
  permissions defined on the former.

  The Developer Role is not a typical Role as only users defined in Zope
  configuration can be added to this Role (which is displayed in the list of
  available Roles in ZMI). This is achieved by two monkey patches
  (ERP5Type.patches.{User,PropertiedUser}) and modifications in
  ERP5Security.ERP5UserFactory.

  Component source code is checked upon modification of text_content property
  whatever its Workflow state (checkSourceCode). On validated and modified
  state, checkConsistency() is called to check id, reference, version and
  errors/warnings messages (set when the Component is modified).
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
                     'TextDocument',
                     'Component')

  _recorded_property_name_getter_dict = {
    'reference': BaseAccessor.Getter('getReference',
                                     'reference',
                                     'string',
                                     storage_id='default_reference'),
    'version': BaseAccessor.Getter('getVersion',
                                   'version',
                                   'string',
                                   default=''),
    'text_content': BaseAccessor.Getter('getTextContent',
                                        'text_content',
                                        'string'),
    'description': BaseAccessor.Getter('getDescription',
                                       'description',
                                       'string',
                                       default='')
    }

  _message_invalid_id = "ID is invalid, should be '${id_prefix}.VERSION.REFERENCE'"

  _message_reference_not_set = "Reference must be set"
  _message_invalid_reference = "Reference cannot end with '_version' or "\
      "start with '_' or be equal to find_module, load_module or reset"

  _message_version_not_set = "Version must be set"
  _message_invalid_version = "Version cannot start with '_'"

  _message_text_content_not_set = "No source code"
  _message_text_content_error = "Error in Source Code: ${error_message}"

  def _hookAfterLoad(self, module_obj):
    pass

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getValidationState')
  def getValidationState(self):
    """
    Needed for bootstrap when the WorkflowState Accessor is not defined yet
    """
    try:
      return aq_base(self).workflow_history[
        'component_validation_workflow'][-1]['validation_state']
    except (AttributeError, KeyError, IndexError):
      return 'draft'

  security.declareProtected(Permissions.ModifyPortalContent, 'checkConsistency')
  def checkConsistency(self, *args, **kw):
    """
    Check the consistency of the Component upon validate or when being
    modified after being validated.

    Some keywords are forbidden for reference and version. As Version package
    always ends with '_version', reference is checked more carefully to avoid
    clashing with existing method names (such as the ones required for PEP
    302).

    XXX-arnau: separate Constraint class?
    """
    error_list = super(ComponentMixin, self).checkConsistency(*args, **kw)
    object_relative_url = self.getRelativeUrl()

    is_id_invalid = False
    try:
      prefix, version, reference = self.getId().split('.')
    except ValueError:
      is_id_invalid = True
    else:
      if (prefix != self.getIdPrefix() or
          version != self.getVersion() or
          reference != self.getReference()):
        is_id_invalid = True

    if is_id_invalid:
      error_list.append(
        ConsistencyMessage(self,
                           object_relative_url,
                           message=self._message_invalid_id,
                           mapping={'id_prefix': self.getIdPrefix()}))

    reference = self.getReference()
    if not reference:
      error_list.append(
        ConsistencyMessage(self,
                           object_relative_url,
                           message=self._message_reference_not_set,
                           mapping={}))

    elif (reference.endswith('_version') or
          reference[0] == '_' or
          reference in ('find_module', 'load_module', 'reset')):
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
      for error_message in self.getTextContentErrorMessageList():
        error_list.append(ConsistencyMessage(self,
                                             object_relative_url=object_relative_url,
                                             message=self._message_text_content_error,
                                             mapping=dict(error_message=error_message)))

    return error_list

  security.declareProtected(Permissions.ModifyPortalContent,
                            'checkConsistencyAndValidate')
  def checkConsistencyAndValidate(self):
    """
    When a Component is in validated or modified validation state and it is
    modified, modified state is set then this checks whether the Component can
    be validated again if checkConsistency returns no error. Otherwise, it
    stays in modified state and previously validated values are used for
    reference, version and text_content
    """
    if not self.checkConsistency():
      for property_name in self._recorded_property_name_getter_dict:
        self.clearRecordedProperty(property_name)

      self.validate()

  security.declareProtected(Permissions.ModifyPortalContent, 'checkSourceCode')
  def checkSourceCode(self):
    """
    Check Component source code through Pylint or compile() builtin if not
    available
    """
    return checkPythonSourceCode(self.getTextContent(), self.getPortalType())

  security.declareProtected(Permissions.ModifyPortalContent, 'PUT')
  def PUT(self, REQUEST, RESPONSE):
    """
    Handle HTTP PUT requests for FTP/Webdav upload, which is object
    dependent. For now only set the text content...
    """
    self.dav__init(REQUEST, RESPONSE)
    self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
    if REQUEST.environ['REQUEST_METHOD'] != 'PUT':
      raise Forbidden, 'REQUEST_METHOD should be PUT.'

    text_content = REQUEST.get('BODY')
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

    XXX-arnau: encoding issue?
    """
    return self.getTextContent()


  # Whether ZODB Components is going to be validated or not should depend on
  # its types because it is fine to validate '{Test,Extension} Component' as
  # it not going to break anything but not for {Document,Interface,Mixin,Tool}
  # Components...
  do_validate_on_import_from_filesystem = False

  security.declareProtected(Permissions.ModifyPortalContent,
                            'importFromFilesystem')
  @classmethod
  def importFromFilesystem(cls,
                           context,
                           reference,
                           version,
                           source_reference=None,
                           filesystem_zodb_module_mapping_set=None):
    """
    Import a Component from the filesystem into ZODB and validate it so it can
    be loaded straightaway provided validate() does not raise any error of
    course
    """
    import os.path
    if source_reference is None or not source_reference.startswith('Products'):
      path = os.path.join(cls._getFilesystemPath(), reference + '.py')
    else:
      import inspect
      module_obj = __import__(source_reference, globals(), {},
                              level=0, fromlist=[source_reference])
      path = inspect.getsourcefile(module_obj)

    with open(path) as f:
      if filesystem_zodb_module_mapping_set is None:
        source_code = f.read()
      else:
        source_code_line_list = []
        for line in f:
          for (filesystem_module,
               zodb_module) in filesystem_zodb_module_mapping_set:
            if line.startswith("from " + filesystem_module):
              line = line.replace(filesystem_module, zodb_module, 1)
              break

          source_code_line_list.append(line)

        source_code = ''.join(source_code_line_list)

    # Checking that the source code is syntactically correct is not
    # needed when importing from filesystem, moreover errors may occur
    # if in the same transaction a Component is created and another
    # one depending upon the former...
    object_id = '%s.%s.%s' % (cls.getIdPrefix(), version, reference)
    new_component = context.newContent(id=object_id,
                                       reference=reference,
                                       source_reference=source_reference,
                                       version=version,
                                       text_content=source_code,
                                       portal_type=cls.portal_type)

    # XXX-ARNAU: checkConsistency() is also called before commit in
    # Component_checkSourceCodeAndValidateAfterModified. Also, everything
    # should be done in checkConsistency()...
    error_message_list = [ m for m in new_component.checkSourceCode()
                           if m['type'] in ('F', 'E') ]
    if error_message_list:
      raise SyntaxError(error_message_list)

    consistency_message_list = new_component.checkConsistency()
    if consistency_message_list:
      from Products.DCWorkflow.DCWorkflow import ValidationFailed
      raise ValidationFailed(consistency_message_list)

    if cls.do_validate_on_import_from_filesystem:
      new_component.validate()

    return new_component

InitializeClass(ComponentMixin)
