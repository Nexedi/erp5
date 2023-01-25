"""
This method send only for Bug Messages was overwritten by
BugMessage_send script. This script only build and setData to
the Bug Messages. THIS NOT SEND MAIL IT SELF!
"""
bug_event = state_change['object']
bug_event.send()
