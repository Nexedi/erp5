##############################################################################
#
# Copyright (c) 2002-2014 Nexedi SA and Contributors. All Rights Reserved.
#
##############################################################################
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from erp5.component.document.DeliveryLine import DeliveryLine

class ImplicitItemMovement(DeliveryLine):

  meta_type = 'ERP5 Implicit Item Movement'
  portal_type = 'Implicit Item Movement'
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isAccountable')
  def isAccountable(self):
    """
      Returns 1 if this needs to be accounted
      Only account movements which are not associated to a delivery
      Whenever delivery is there, delivery has priority
    """
    return not self.hasCellContent()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getRootDeliveryValue')
  def getRootDeliveryValue(self):
    """
    Returns the root delivery responsible of this line
    """
    return self

# Workaround buggy implementation of getImmobilisationState
ImplicitItemMovement.getImmobilisationState = None