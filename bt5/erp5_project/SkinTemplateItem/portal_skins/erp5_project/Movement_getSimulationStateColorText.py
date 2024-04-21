# Define the color using the simulation state
if task.getPortalType() in task.getPortalCalendarPeriodTypeList():
  return '#d3d3d3'

simulation_method = getattr(task, 'getSimulationState', None)
if simulation_method is None:
  return '#D1E8FF'

simulation_state = simulation_method()  # pylint:disable=not-callable

color_dict = {
  'draft': '#a7d7ae',
  'planned': '#ffff00',
  'ordered': '#ff8e56',
  'confirmed': '#ff0000',
  'started': '#ff00ff',
  'stopped': '#00b8ff',
  'delivered': '#3deb3d',
}
return color_dict.get(simulation_state, '#D1E8FF')
