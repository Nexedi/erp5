##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SARL and Contributors. All Rights Reserved.
#                         Sebastien Robin <seb@nexedi.com>
#                         Jean-Paul Smets <jp@nexedi.com>
#                         Courteaud Romain <romain@nexedi.com>
#                         Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.interfaces import IConstraint
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
from zope.interface import implements
from Products.ERP5Type.Core.Predicate import Predicate
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Utils import UpperCase, createExpressionContext
from Products.CMFCore.Expression import Expression
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin

class ConstraintMixin(IdAsReferenceMixin('_constraint'), Predicate):
  """
  Mixin Constraint implementation (only relevant for ZODB Property
  sheets, use Products.ERP5Type.Constraint instead for filesystem
  Property Sheets) relying on Predicate

  @todo: Add code to import constraints requiring a new TALES
         Expression field in predicate to be able to import
         'condition' properly
  """
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # IDs of error messages defined in each Constraint, only used when
  # importing or exporting from/to filesystem Constraint
  _message_id_tuple = ()

  __allow_access_to_unprotected_subobjects__ = 1
  implements( IConstraint, )

  property_sheets = (PropertySheet.SimpleItem,
                     PropertySheet.Reference,
                     PropertySheet.Predicate)

  def _getMessage(self, message_id):
    """
    Get the message corresponding to this message_id.
    """
    return getattr(self, 'get' + UpperCase(message_id))()

  def _generateError(self, obj, error_message, mapping={}):
    """
    Generic method used to generate error in checkConsistency.
    """
    if error_message is not None:
      msg = ConsistencyMessage(self,
                               object_relative_url=obj.getRelativeUrl(),
                               message=error_message,
                               mapping=mapping)
      return msg

  security.declareProtected(Permissions.AccessContentsInformation,
                            'checkConsistency')
  def checkConsistency(self, obj, fixit=0, **kw):
    """
    Check the pre-condition before checking the consistency.
    _checkConsistency() must be define in the child class.
    """
    if not self.test(obj):
      return []

    return self._checkConsistency(obj, fixit, **kw)

  def _checkConsistency(self, obj, fixit=0, **kw):
    """Implementation of constraint logic.
    """
    raise NotImplementedError()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'fixConsistency')
  def fixConsistency(self, obj, **kw):
    """
    Default method is to call checkConsistency with fixit set to 1
    """
    return self.checkConsistency(obj, fixit=1, **kw)

  def _getExpressionValue(self, obj, expression_string):
    """
    Get the Python value from an Expression string, but check before
    whether it is None as a getter may returns the default value which
    could be None
    """
    if expression_string is None:
      return None

    return Expression(expression_string)(createExpressionContext(obj))

  @staticmethod
  def _preConvertBaseFromFilesystemDefinition(filesystem_definition_dict):
    """
    Call before actually converting the attributes common to all
    constraints
    """
    return {}

  @staticmethod
  def _convertFromFilesystemDefinition(*args, **kw):
    """
    Convert a filesystem property dict to a ZODB Property dict which
    will be given to newContent().

    Only attributes specific to this constraint will be given as
    parameters, e.g. not the ones common to all constraints such as
    'id', 'description', 'type' and 'condition' and error messages
    defined in '_message_id_tuple' class attribute.

    @see importFromFilesystemDefinition
    """
    yield {}

  security.declareProtected(Permissions.AccessContentsInformation,
                            'importFromFilesystemDefinition')
  @classmethod
  def importFromFilesystemDefinition(cls, context, filesystem_definition_dict):
    """
    Import the filesystem definition to a ZODB Constraint, without its
    condition as it is now a Predicate and has to be converted
    manually.

    Several ZODB Constraints may be created to handle Constraints such
    as Attribute Equality which defines an attribute name and its
    expected value, thus ending up creating one ZODB Constraint per
    attribute/expected value
    """
    # Copy the dictionnary as it is going to be modified to remove all
    # the common properties in order to have a dictionnary containing
    # only properties specific to the current constraint
    filesystem_definition_copy_dict = filesystem_definition_dict.copy()

    # This dict only contains definition attributes common to *all*
    # ZODB Constraints
    base_constraint_definition_dict = \
        cls._preConvertBaseFromFilesystemDefinition(filesystem_definition_copy_dict)

    base_constraint_definition_dict['portal_type'] = cls.portal_type

    base_constraint_definition_dict['id'] = \
        filesystem_definition_copy_dict.pop('id') + \
          cls.getIdAsReferenceSuffix()

    base_constraint_definition_dict['description'] = \
        filesystem_definition_copy_dict.pop('description', '')

    if 'condition' in filesystem_definition_copy_dict:
      base_constraint_definition_dict['test_tales_expression'] = \
          filesystem_definition_copy_dict.pop('condition')

    # The type is meaningless for ZODB Constraints as it is the portal
    # type itself
    filesystem_definition_copy_dict.pop('type')

    # Add specific error messages defined on the constraint document
    for message_name in cls._message_id_tuple:
      if message_name in filesystem_definition_copy_dict:
        base_constraint_definition_dict[message_name] = \
            filesystem_definition_copy_dict.pop(message_name)

    # Call the method defined in the Constraint document which returns
    # N dictionnaries containing only attributes specific to the
    # Constraint
    constraint_definition_generator = \
        cls._convertFromFilesystemDefinition(**filesystem_definition_copy_dict)

    # Create all the constraint in the current ZODB Property Sheet
    for constraint_definition_dict in constraint_definition_generator:
      constraint_definition_dict.update(base_constraint_definition_dict)
      context.newContent(**constraint_definition_dict)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'applyOnAccessorHolder')
  def applyOnAccessorHolder(self, accessor_holder, expression_context, portal):
    # Do not use asContext. Temporary object generated by asContext may
    # contain persistent object. If persistent object is stored on memory like
    # this(accessor_holder is on-memory object and is kept beyond transaction)
    # then ConnectionStateError occurs after a long time.
    import copy
    constraint_definition = copy.deepcopy(self.aq_base)
    # note the relative url of this constraint to display it later in
    # checkConsistency messages
    constraint_definition.relative_url = self.getRelativeUrl()
    accessor_holder.constraints.append(constraint_definition)
