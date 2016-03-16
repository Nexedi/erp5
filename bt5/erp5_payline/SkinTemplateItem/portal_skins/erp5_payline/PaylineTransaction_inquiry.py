"""
Call whatever can make context progress.
What is called depends on context's resource and simulation state.
Trigger for this call may be an HTTP Exchange (a notification received from Payline) or an alarm (missed notification and timeout reached).
"""
simulation_state = context.getSimulationState()
if simulation_state not in ('confirmed', 'started'):
  raise ValueError('No action expected in %r state' % (simulation_state, ))
getattr(context, script.id + context.getSimulationState().title().replace('_', '') + context.getResourceValue().getCodification())()
