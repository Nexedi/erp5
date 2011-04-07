import warnings
from Products.ERP5.mixin import composition
from Products.ERP5.ERP5Site import ERP5Site

def patch():
  from AccessControl.PermissionRole import PermissionRole
  from Products.ERP5Type import Permissions
  def declareProtected(cls, permission, *name_list):
    roles = PermissionRole(permission)
    for name in name_list:
      setattr(cls, name + '__roles__', roles)

  ## ERP5Site

  declareProtected(ERP5Site, Permissions.AccessContentsInformation,
                   'getPortalBusinessStateTypeList',
                   'getPortalBusinessPathTypeList')

  def getPortalBusinessStateTypeList(self):
    """
      Return business state types.
    """
    return ('Business State',)

  ERP5Site.getPortalBusinessStateTypeList = getPortalBusinessStateTypeList

  def getPortalBusinessPathTypeList(self):
    """
      Return business path types.
    """
    return ('Business Path',)

  ERP5Site.getPortalBusinessPathTypeList = getPortalBusinessPathTypeList

  ## AmountGeneratorMixin

  class true:
    def __nonzero__(self):
      warnings.warn("Default value for 'generate_empty_amounts' parameter"
                    " is False for new simulation", DeprecationWarning)
      return True
  true = true()

  from Products.ERP5.mixin.amount_generator import AmountGeneratorMixin
  for method_id in ('getAggregatedAmountList',): # getGeneratedAmountList
    m = getattr(AmountGeneratorMixin, method_id)
    f = m.im_func
    f = type(f)(f.func_code, f.func_globals, f.func_name,
                f.func_defaults[:3] + (true,), f.func_closure)
    m = type(m)(f, None, AmountGeneratorMixin)
    setattr(AmountGeneratorMixin, method_id, m)

  ## CompositionMixin

  composition._LEGACY_SIMULATION = True

  ## Movement

  from Products.ERP5.Document.Movement import Movement

  def isFrozen(self):
    """
    Returns the frozen status of this movement.
    a movement in stopped, delivered or cancelled states is automatically frozen.
    If frozen is locally set to '0', we must check for a parent set to '1', in
    which case, we want the children to be frozen as well.

    BPM evaluation allows to set frozen state list per Business Path.
    """
    business_path = self.getCausalityValue(portal_type='Business Path')
    if business_path is None:
      # XXX Hardcoded
      # Maybe, we should use getPortalCurrentInventoryStateList
      # and another portal method for cancelled (and deleted)
      #     LOG("Movement, isFrozen", DEBUG, "Hardcoded state list")
      if self.getSimulationState() in ('stopped', 'delivered', 'cancelled'):
        return 1
    else:
      # conditional BPM enabled frozen state check
      # BPM dynamic configuration
      if self.getSimulationState() in business_path.getFrozenStateList():
        return True

    # manually frozen
    frozen = self._baseIsFrozen()
    if frozen == 0:
      self._baseSetFrozen(None)
    return frozen or False

  Movement.isFrozen = isFrozen

  ## SimulationMovement

  from Products.ERP5.Document.SimulationMovement import SimulationMovement
  try:
    del SimulationMovement.isFrozen
  except AttributeError:
    pass

  def isCompleted(self):
    """Zope publisher docstring. Documentation in ISimulationMovement"""
    # only available in BPM, so fail totally in case of working without BPM
    return self.getSimulationState() in self.getCausalityValue(
        portal_type='Business Path').getCompletedStateList()

  SimulationMovement.isCompleted = isCompleted

  def asComposedDocument(self, *args, **kw):
    # XXX: What delivery should be used to find amount generator lines ?
    #      With the currently enabled code, entire branches in the simulation
    #      tree get (temporary) deleted when new delivery lines are being built
    #      (and don't have yet a specialise value).
    #      With the commented code, changing the STC on a SIT generated from a
    #      SPL/SO would have no impact (and would never make the SIT divergent).
    #return self.getRootSimulationMovement() \
    #           .getDeliveryValue() \
    #           .asComposedDocument(*args, **kw)
    while 1:
      delivery_value = self.getDeliveryValue()
      if delivery_value is not None:
        return delivery_value.asComposedDocument(*args, **kw)
      # below code is for compatibility with old rules
      grand_parent = self.getParentValue().getParentValue()
      if grand_parent.getPortalType() == 'Simulation Tool':
        return self.getOrderValue().asComposedDocument(*args, **kw)
      self = grand_parent

  SimulationMovement.asComposedDocument = asComposedDocument

  def isBuildable(self):
    """Simulation Movement buildable logic"""
    if self.getDeliveryValue() is not None:
      # already delivered
      return False

    # might be buildable - business path dependent
    business_path = self.getCausalityValue(portal_type='Business Path')
    explanation_value = self.getExplanationValue()
    if business_path is None or explanation_value is None:
      return True

    return len(business_path.filterBuildableMovementList([self])) == 1

  SimulationMovement.isBuildable = isBuildable

  def _getApplicableRuleList(self):
    """ Search rules that match this movement, but don't try to look up
        successor trade_phases
    """
    portal_rules = self.getPortalObject().portal_rules
    return portal_rules.searchRuleList(self,
                                       sort_on='version',
                                       sort_order='descending')

  SimulationMovement._getApplicableRuleList = _getApplicableRuleList

patch()
