## Script (Python) "purchase_order_apply_condition_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=
##
redirect_url = context.purchase_order_apply_condition(form_id=form_id)

context.REQUEST[ 'RESPONSE' ].redirect( redirect_url )
