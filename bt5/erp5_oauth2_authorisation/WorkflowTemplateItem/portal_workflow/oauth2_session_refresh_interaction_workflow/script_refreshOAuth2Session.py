# Proxy role: Manager, because the originator for the event which triggered
# this interaction may have been using a proxy role itself, and we should
# not limit what can be done on Assignments, but just follow what is being
# done.
state_change['object'].refreshAccessToken()
