## Script (Python) "order_status_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=workflow_action, comment=''
##title=Modify the status of an order object
##
context.portal_workflow.doActionFor(
    context,
    workflow_action,
    comment=comment)

if workflow_action == 'reject':
    redirect_url = context.portal_url() + '/search?review_state=pending'
elif workflow_action == 'confirm':
    # Empty the cart first
    try:
        user = context.portal_membership.getAuthenticatedMember().getUserName()
        mem_folder = context.portal_membership.getHomeFolder(user)
        mem_folder.ShoppingCart.clearCart()
    except:
        pass
    redirect_url = '%s/view?%s' % ( context.local_absolute_url()
                                  , 'portal_status_message=Order+confirmed.'
                                  )
elif workflow_action == 'cancel':
    redirect_url = '%s/view?%s' % ( context.local_absolute_url()
                                  , 'portal_status_message=Order+cancelled.'
                                  )
else:
    redirect_url = '%s/view?%s' % ( context.local_absolute_url()
                                  , 'portal_status_message=Status+changed.'
                                  )

context.REQUEST[ 'RESPONSE' ].redirect( redirect_url )
