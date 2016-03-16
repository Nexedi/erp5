"""Call send on the message"""
message = state_change['object']
message.send(**state_change.kwargs)
