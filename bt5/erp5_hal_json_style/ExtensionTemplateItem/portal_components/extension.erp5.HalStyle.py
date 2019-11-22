from Acquisition import aq_self, aq_base, aq_inner
from Products.ERP5Type.Utils import UpperCase
from ZODB.POSException import ConflictError
from AccessControl import Unauthorized


def Base_aqSelf(self):
  return aq_self(self)

def Base_aqBase(self):
  return aq_base(self)

def Base_aqInner(self):
  return aq_inner(self)

def Field_getSubFieldKeyDict(self, field, field_id, key=None):
  """XXX"""
  return field.generate_subfield_key(field_id, key=key)

def Listbox_getBrainValue(self, brain, obj, select, can_check_local_property, editable_field=None):
  """
  ListBox.py / getValueList
  """
  tales = False

  # Use a widget, if any.
  if editable_field is not None:
    # XXX we need to take care of whether the editable field is
    # a proxy field or not, because a proxy field may inherit a
    # tales expression from a template field, and the API is not
    # unified.
    get_tales = getattr(editable_field, 'get_recursive_tales',
                        editable_field.get_tales)
    tales = get_tales('default')
    if tales:
      default_field_value = editable_field.__of__(obj).get_value('default',
                                                                 cell=brain)

  # If a tales expression is not defined, get a skin, an accessor or a property.
  if not tales:
    if (can_check_local_property) and (getattr(aq_self(brain), select, None) is not None):
      default_field_value = getattr(brain, select)
    else:
      try:
        # Get the trailing part.
        try:
          property_id = select[select.rindex('.') + 1:]
        except ValueError:
          property_id = select
        try:
          accessor_name = 'get%s' % UpperCase(property_id)
          # Make sure the object have the attribute, and this is not
          # acquired, but still get the attribute on the acquisition wrapper
          getattr(aq_base(obj), accessor_name)
          default_field_value = getattr(obj, accessor_name)
        except AttributeError:
          default_field_value = getattr(obj, property_id, None)
      except (AttributeError, KeyError, Unauthorized):
        default_field_value = None

  # If the value is callable, evaluate it.
  if callable(default_field_value):
    try:
      try:
        default_field_value = default_field_value(brain=brain)
      except TypeError:
        default_field_value = default_field_value()
    except (ConflictError, RuntimeError):
      raise
    except Exception:
      default_field_value = None

  # Listbox.py forces result to be an empty string
  # This is not needed in hal
  # if default_field_value is None:
  #   default_field_value = ''

  return default_field_value


def WorkflowTool_listActionParameterList(self):
  action_list = self.listActions()
  info = self._getOAI(None)

  workflow_dict = {}
  result_list = []

  for action in action_list:
    if (action['workflow_id'] not in workflow_dict):
      workflow = self.getWorkflowById(action['workflow_id'])
      if workflow is not None:
        workflow_dict[action['workflow_id']] = workflow.getWorklistVariableMatchDict(info, check_guard=False)

    query = workflow_dict[action['workflow_id']].get(action['worklist_id'])
    if query is not None:
      query.pop('metadata')
      result_list.append({
        'count': action['count'],
        'name': action['name'],
        'local_roles': query.pop('local_roles'),
        'query': query
      })


  return result_list
