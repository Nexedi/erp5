kwargs = state_change['kwargs']
person = state_change['object']

person.edit(password=kwargs['password'], reference=kwargs['reference'])
