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

  ## CompositionMixin

  composition._LEGACY_SIMULATION = True

  ## SimulationMovement

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

  from Products.ERP5.Document.SimulationMovement import SimulationMovement
  SimulationMovement.asComposedDocument = asComposedDocument

patch()
