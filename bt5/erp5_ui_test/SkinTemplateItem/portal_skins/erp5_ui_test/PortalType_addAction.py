# this script has a parameter named `id`
# pylint: disable=redefined-builtin
"""Add or replace an action on a type informations from types tool.
"""
assert context.meta_type in ('ERP5 Type Information', 'ERP5 Base Type'), context.meta_type

context.PortalType_deleteAction(id=id)

context.addAction( id         = id
                 , action     = action
                 , name       = name
                 , condition  = condition
                 , permission = permission
                 , category   = category
                 , icon       = icon
                 , priority   = 10.0
                 )

return 'Set Successfully.'
