##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class Constraint(Interface):
  """ERP5 Constraints are classes that are in charge of checking wether an
  object is in consistent state or not.

  Constraints are usually defined in PropertySheets, thus constraints are
  associated to all documents of a given portal type.
  
  A property sheet can contain _constraints slot ( just like _properties and
  _categories ).  _constraints is a list of constraint definition represented
  as dictionnaries, for example we can have:

  _constraints = (
    {   # we need to have an id
        'id': 'the_constraint',
        
        # Specify the class name of the constraint. The class name must be
        # registered to ERP5Type. If the class is not found, a
        # ConstraintNotFound error will be raised when trying to use it.
        'type': 'MyConstraintClass',
      
        # Constraint have a description.
        'description': 'Constraint description', 
       
        # XXX condition is a TALES Expression; is it part of the API ?
        # how to use condition based on a workflow state in a workflow before
        # script, where the document is not in that state yet ?
        'condition': 'python: object.getPortalType() == "Foo"'

        # Additional Constraint parameters are configured here.
        # Constraint docstring should provide a configuration example and a
        # documentation on parameter they accept.
    }
  )

  Those constraint definition parameters will be available from the Constraint
  instance as `self.constraint_definition` (a dict).

  Calling checkConsistency() method on any ERP5Type document will check all
  constraint defined on this document. If the document is a subclass of
  Products.ERP5Type.Core.Folder.Folder, checkConsistency will be called
  recursivly.
    
  XXX How to call only one constraint, even if this constraint is not defined
  on property sheet ?

  """
  
  def checkConsistency(obj, fixit=0):
    """This method checks the consistency of object `obj`, and fix errors if
    the argument `fixit` is true. Not all constraint have to support error
    repairing, in that case, simply ignore the fixit parameter.
    This method should return a list of errors, which are a list for now.
    """
    
  def _generateError(obj, error_message, mapping={}):
    """Generate an error for `obj` with the corresponding `error_message`.
    This method is usefull for Constraint authors, in case of an error, they
    can simply call:
    
    >>> if something_is_wrong:
    >>>   errors.append(self._generateError(obj, 'Something is wrong !')
    
    Then this message ('Something is wrong !') will be translated when the
    caller of document.checkConsistency() calls getTranslatedMessage() on
    ConsistencyMessage instances returned by checkConsistency.

    The implementation uses ERP5Type's Messages, so it's possible to use a
    `mapping` for substitution, like this:
    >>> if something_is_wrong:
    >>>   errors.append(self._generateError(obj,
    ...      'Something is wrong: ${wrong_thing}',
    ...      mapping=dict(wrong_thing=obj.getTheWrongThing())))
   
    """

