## Script (Python) "SalesOrder_orderList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=batch_mode=0,**kw
##title=
##
# order the selection of Sales Order
request = context.REQUEST

object_list = context.object_action_list(selection_name='sales_order_selection')

ordered_order_number = 0
ordered_order_list = ' '

not_ordered_order_number = 0
not_ordered_order_list = ' '

uid_list = []

for order in object_list:

  simulation_state = order.getSimulationState()
  if (simulation_state == 'planned' or simulation_state == 'draft'): 
    
    error_message = order.Order_lightControl()
    if error_message == '':

      # we give local_roles to the users
      user_name = ''
      user_name = order.getSourceAdministrationTitle().replace(' ','_')
      order.assign_gestionaire_designe_roles(user_name = user_name)

	  
      # set the transition_state to 'ordered'
      order.order()

      #order.flushActivity(invoke=1)
    
      ordered_order_number += 1
      ordered_order_list += order.getId()+' '

    else:
      not_ordered_order_number += 1
      not_ordered_order_list += order.getId()+' '

      uid_list.append(order.getUid())

  else:
    """
    not_ordered_order_number += 1
    not_ordered_order_list += order.getId()+' '
    
    uid_list.append(order.getUid())
    """
    None

# and this is the end ....
if batch_mode:
  return None
else:
  if not_ordered_order_number == 0: 
    redirect_url = '%s?%s%i%s' % ( context.absolute_url()+'/'+'view', 'portal_status_message=',ordered_order_number,'+Commandes+ventes+validées.')
  else:
    context.portal_selections.setSelectionToIds('sales_order_selection', uid_list, REQUEST=request)
    redirect_url = '%s?%s%i%s' % ( context.absolute_url()+'/'+'view', 'portal_status_message=',not_ordered_order_number,'+Commandes+ventes+non+validées.')

  request[ 'RESPONSE' ].redirect( redirect_url )
