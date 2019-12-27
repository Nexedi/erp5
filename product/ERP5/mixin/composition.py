# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Julien Muchembled <jm@nexedi.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Acquisition import aq_base
from Products.ERP5Type import Permissions
from Products.ERP5Type.Cache import transactional_cached
from Products.ERP5Type.Utils import sortValueList
from Products.ERP5Type.Core.Predicate import Predicate
from Products.ERP5.Document.BusinessProcess import BusinessProcess
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery

_MARKER = []

@transactional_cached()
def _getEffectiveModel(self, start_date, stop_date):
  """Return the most appropriate model using effective_date, expiration_date
  and version number.
  An effective model is a model which start and stop_date are equal (or
  excluded) to the range of the given start and stop_date and with the
  higher version number (if there is more than one)

  XXX Should we moved this function to a class ? Which one ?
      What about reusing IVersionable ?
  """
  reference = self.getProperty('reference')
  if not reference:
    return self

  query_list = [Query(reference=reference),
                Query(portal_type=self.getPortalType()),
                Query(validation_state=('deleted', 'invalidated'),
                      operator='NOT')]
  if start_date is not None:
    query_list.append(ComplexQuery(Query(effective_date=None),
                                   Query(effective_date=start_date,
                                         range='<='),
                                   logical_operator='OR'))
  if stop_date is not None:
    query_list.append(ComplexQuery(Query(expiration_date=None),
                                   Query(expiration_date=stop_date,
                                         range='>'),
                                   logical_operator='OR'))

  # XXX What to do the catalog returns nothing (either because 'self' was just
  #     created and not yet indexed, or because it was invalidated) ?
  #     For the moment, we return self if self is invalidated and we raise otherwise.
  #     This way, if this happens in activity it may succeed when activity is retried.
  model_list = self.getPortalObject().portal_catalog.unrestrictedSearchResults(
      query=ComplexQuery(logical_operator='AND', *query_list),
      sort_on=(('version', 'descending'),))
  if not model_list:
    if self.getValidationState() == 'invalidated':
      return self
    raise KeyError('No %s found with the reference %s between %s and %s' % \
            (self.getPortalType(), reference, start_date, stop_date))
  return model_list[0].getObject()


# We do have clever caching here, since container_list does not contain objects
# with no subobject.
# After evaluation of asComposedDocument() on a SO and all its SOL,
# _findPredicateList's cache has at most 1 entry per specialise value found
# on SO/SOL.
@transactional_cached()
def _findPredicateList(container_list, portal_type):
  predicate_list = []
  mask_set = set()
  for container in container_list:
    mask_list = []
    for ob in container.objectValues(portal_type=portal_type):
      if isinstance(ob, Predicate):
        # reference is used to hide lines on farther containers
        reference = ob.getProperty('reference')
        if reference:
          key = ob.getPortalType(), reference
          if key in mask_set:
            continue
          mask_list.append(key)
        predicate_list.append(ob)
    mask_set.update(mask_list)
  return predicate_list


class asComposedDocument(object):
  """Return a temporary object which is the composition of all effective models

  The returned value is a temporary copy of the given object. The list of all
  effective models (specialise values) is stored in a private attribute.
  Collecting predicates (from effective models) is done lazily. Predicates can
  be accessed through contentValues/objectValues.

  This class should be seen as a function, and it is named accordingly.
  It is out of CompositionMixin class to avoid excessive indentation.
  """
  # Cache created classes to make other caches (like Base.aq_portal_type)
  # useful and avoid memory leaks.
  __class_cache = {}

  def __new__(cls, orig_self, portal_type_list=None):
    self = orig_self.asContext(_portal_type_list=portal_type_list) # XXX-JPS orig_self -> original_self - please follow conventions
    base_class = self.__class__
    try:
      self.__class__ = cls.__class_cache[base_class]
    except KeyError:
      cls.__class_cache[base_class] = self.__class__ = \
        type(base_class.__name__, (cls, base_class, BusinessProcess), {})
              # here we could inherit many "useful" classes dynamically - héhé
              # that would be a "real" abstract composition system
    self._effective_model_list, specialise_value_list = \
      orig_self._findEffectiveAndInitialModelList(portal_type_list)
    self._setValueList('specialise', specialise_value_list)
    return self

  def __init__(self, orig_self, portal_type_list=None):
    # __init__ is not called automatically after __new__ because returned object
    # is wrapped in an acquisition context.
    assert False

  def asComposedDocument(self, portal_type_list=None):
    assert False, "not useful yet"
    # If required, this must be implemented by calling 'asComposedDocument' on
    # the original object (because the parameters may differ).

  @property
  def _folder_handler(self):
    assert False, "Attempt to use .asComposedDocument() result as folder. This should never happen!"

  def _getOb(self, key, *args, **kw):
    raise KeyError(key)

  def __getattr__(self, name):
    raise AttributeError(name)

  def objectValues(self, spec=None, meta_type=None, portal_type=None,
                   sort_on=None, sort_order=None, checked_permission=None,
                   **kw):
    assert spec is meta_type is checked_permission is None, "not useful yet"
    object_list = getattr(aq_base(self), '_predicate_list', None)
    if object_list is None:
      container_list = tuple(filter(len, self._effective_model_list))
      object_list = _findPredicateList(container_list, self._portal_type_list)
      self._predicate_list = object_list
    if portal_type is not None:
      if isinstance(portal_type, str):
        portal_type = (portal_type,)
      object_list = filter(lambda x: x.getPortalType() in portal_type,
                           object_list)
    return sortValueList(object_list, sort_on, sort_order, **kw)

  def getProperty(self, key, d=_MARKER, **kw):
    for obj in [self._original] + self._effective_model_list:
      r = obj.getProperty(key, _MARKER, **kw)
      if r is not _MARKER:
        return r
    if d is not _MARKER:
      return d

class CompositionMixin:
  """
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asComposedDocument')
  asComposedDocument = transactional_cached(
    lambda self, portal_type_list=None: (self, portal_type_list)
    )(asComposedDocument)

  # XXX add accessors to get properties from '_effective_model_list' ?
  #     (cf PaySheetModel)

  def _findEffectiveSpecialiseValueList(self, specialise_type_list=None):
    """Return a list of effective specialised objects that is the
    inheritance tree.
    An effective object is an object which have start_date and stop_date
    included to the range of the given parameters start_date and stop_date.

    This algorithm uses Breadth First Search.
    """
    return self._findEffectiveAndInitialModelList(specialise_type_list)[0]

  def _findEffectiveAndInitialModelList(self, specialise_type_list):
    start_date = self.getStartDate()
    stop_date = self.getStopDate()
    effective_list = []
    effective_set = set()
    effective_index = -1
    model_list = self.getInheritedSpecialiseValueList(specialise_type_list)
    specialise_value_list = model_list
    while effective_index < len(effective_list):
      if effective_index >= 0:
        # we don't use getSpecialiseValueList to avoid acquisition on the parent
        model_list = effective_list[effective_index]._getValueList('specialise',
                                        portal_type=specialise_type_list or ())
      effective_index += 1
      for model in model_list:
        model = _getEffectiveModel(model, start_date, stop_date)
        if model not in effective_set:
          effective_set.add(model)
          if 1: #model.test(self): # XXX
            effective_list.append(model)
    return effective_list, specialise_value_list

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getInheritedSpecialiseValueList')
  def getInheritedSpecialiseValueList(self, specialise_type_list=None,
                                      exclude_specialise_type_list=()):
    """Get inherited specialise values

    Values are inherited from parent only if portal types differ,
    so that a child can override.
    """
    portal_type_set = set()
    specialise_list = []
    for value in self._getValueList('specialise'):
      portal_type = value.getPortalType()
      if not (portal_type in exclude_specialise_type_list or
          specialise_type_list and portal_type not in specialise_type_list):
        portal_type_set.add(portal_type)
        specialise_list.append(value)
    parent = self.getParentValue()
    if isinstance(parent, CompositionMixin):
      portal_type_set.update(exclude_specialise_type_list)
      specialise_list += parent.getInheritedSpecialiseValueList(
        specialise_type_list, portal_type_set)
    return specialise_list

del asComposedDocument # to be unhidden (and renamed ?) if needed

InitializeClass(CompositionMixin)
