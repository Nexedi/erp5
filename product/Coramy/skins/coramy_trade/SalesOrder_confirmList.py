## Script (Python) "SalesOrder_confirmList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=start_date=None, stop_date=None,batch_mode=0,**kw
##title=
##
# confirm the selection of Sales Order
request = context.REQUEST

object_list = context.object_action_list(selection_name='sales_order_selection')

confirmed_order_number = 0
confirmed_order_list = ' '

not_confirmed_order_number = 0
not_confirmed_order_list = ' '

uid_list = []

for order in object_list:

  simulation_state = order.getSimulationState()
  if (simulation_state == 'planned' or simulation_state == 'ordered'): 
    
    error_message = order.Order_heavyControl()
    if error_message == '':

      # we give local_roles to the users
      user_name = ''
      user_name = order.getSourceAdministrationTitle().replace(' ','_')
      order.assign_gestionaire_designe_roles(user_name = user_name)

      if start_date != None:
        order.setStartDate(start_date)
      if stop_date != None:
        order.setStopDate(stop_date)
	

	  
      # set the transition_state to 'confirmed'
      order.confirm()
    
      #order.flushActivity(invoke=1)
      
      confirmed_order_number += 1
      confirmed_order_list += order.getId()+' '
    else:
      not_confirmed_order_number += 1
      not_confirmed_order_list += order.getId()+' '

      uid_list.append(order.getUid())
      
  elif (simulation_state == 'draft'):
    not_confirmed_order_number += 1
    not_confirmed_order_list += order.getId()+' '

    uid_list.append(order.getUid())


# and this is the end ....
if batch_mode:
  return None
else:
  """
  redirect_url = '%s?%s%i%s' % ( context.absolute_url()+'/'+'view', 'portal_status_message=',not_confirmed_order_number,'+Commandes+ventes+non+confirmées:'+not_confirmed_order_list+'\n')
  request[ 'RESPONSE' ].redirect( redirect_url )
  """
  if not_confirmed_order_number == 0: 
    redirect_url = '%s?%s%i%s' % ( context.absolute_url()+'/'+'view', 'portal_status_message=',confirmed_order_number,'+Commandes+ventes+confirmées.')
  else:
    context.portal_selections.setSelectionToIds('sales_order_selection', uid_list, REQUEST=request)
    redirect_url = '%s?%s%i%s' % ( context.absolute_url()+'/'+'view', 'portal_status_message=',not_confirmed_order_number,'+Commandes+ventes+non+confirmées.')

  request[ 'RESPONSE' ].redirect( redirect_url )
