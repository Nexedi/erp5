if site is None:
  site = context.getSiteValue()
site_uid = site.getUid()
site_url = site.getRelativeUrl()
operation_list = []
exception_portal_type_list = ['Foreign Check', 'External Banking Operation', 'Account Transfer', 'Check Deposit',
                              'Checkbook Reception', 'Accounting Cancellation', 'Stop Payment']
if site_uid is not None:
  not_closed_state_list = ('ordered','planned','confirmed','started','stopped', 'ready', 'deposited', 'received', 'finished')
  portal_type_list = [x for x in context.getPortalDeliveryTypeList()
                      if x not in exception_portal_type_list]
  document_list = context.Baobab_getRemainingOperationList(
                        site_uid=site_uid,
                        simulation_state=not_closed_state_list,
                        portal_type=portal_type_list)
  append = operation_list.append
  for document in document_list:
    # Stop Payment and Cash Movement in started state must not block counter day closing.
    # Mutilated Banknotes in planned state or in finished state with siege as source must nogt block either.
    if document not in operation_list:
      portal_type = document.getPortalType()
      simulation_state = document.getSimulationState()
      if (portal_type in ('Stop Payment', ) and simulation_state == 'started')  \
              or (portal_type == 'Mutilated Banknote' and 
                   simulation_state != 'finished' \
                 ) \
              or (portal_type == 'Check Payment' and 
                   simulation_state in ('planned', 'ordered') \
                 ) \
              or (portal_type == 'Monetary Destruction' and simulation_state in ('stopped', 'started')) \
              or (portal_type == 'Paper Money Payment' and simulation_state != 'ready') \
              or (portal_type == 'Paper Money Deposit' and simulation_state == 'stopped'):
         continue
      if portal_type in ('Cash Movement', 'Cash Movement New Not Emitted'):
         if not (
                ((simulation_state in ('confirmed') and site_url in document.getSource("")) 
                  or 
                (simulation_state in ('stopped') and site_url in document.getDestination("")))
             ):
          continue
      if portal_type in ('Money Deposit',) and simulation_state not in ('confirmed',):
        continue
      append(document)

def operation_sort(a,b):
  result = cmp(a.getPortalType(),b.getPortalType())
  if result==0:
    result = cmp(a.getSourceReference(),b.getSourceReference())
  return result

operation_list.sort(operation_sort)

return operation_list
