context = state_change['object']
activate_kw = state_change['kwargs'].get('activate_kw') or {}
context.activate(**activate_kw).updateCausalityState()
