"""Exception Classes for ERP5"""

# These classes are placed here so that they can be imported into TTW Python
# scripts. To do so, add the following line to your Py script:
# from Products.ERP5.Errors import DeferredCatalogError

from Products.PythonScripts.Utility import allow_class
from Products.CMFCore.WorkflowCore import WorkflowException
from MySQLdb import ProgrammingError

allow_class(ProgrammingError)

class DeferredCatalogError(Exception):

    def __init__(self, error_key, context):
        Exception.__init__(self, error_key)
        self.error_key = error_key
        self.field_id = context.getRelativeUrl()


class UnsupportedWorkflowMethod(WorkflowException):

  def __init__(self, instance, workflow_id, transition_id):
    self.instance = instance
    self.workflow_id = workflow_id
    self.transition_id = transition_id

  def __str__(self):
    return "Transition %s/%s unsupported for %r. Current state is %r." \
      % (self.workflow_id, self.transition_id, self.instance,
         self.instance.getPortalObject().portal_workflow[self.workflow_id]
             ._getWorkflowStateOf(self.instance, id_only=1))


class ImmobilisationValidityError(Exception):pass
class ImmobilisationCalculationError(Exception):pass
class TransformationRuleError(Exception):pass
class SimulationError(Exception):pass


allow_class(DeferredCatalogError)
allow_class(ImmobilisationValidityError)
allow_class(ImmobilisationCalculationError)
allow_class(WorkflowException)
allow_class(UnsupportedWorkflowMethod)
allow_class(TransformationRuleError)
allow_class(SimulationError)

