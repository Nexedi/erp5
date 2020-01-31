# this script has a parameter named `id`
# pylint: disable=redefined-builtin
"""Redirect to Foo_viewFormBox"""
msg = "%s %s %s %s" % (id, title, quantity, description)

context.Base_redirect("Foo_viewFormBox", 
                      keep_items={'portal_status_message': msg})
