from Products.PythonScripts.standard import Object
from six.moves import range
request = container.REQUEST
portal = context.getPortalObject()
state_item_list=[x[1] for x in portal.ERP5Site_getWorkflowStateItemList(
     portal_type=portal.getPortalEventTypeList(), state_var='simulation_state')]
#remove deteted state
if 'deleted' in state_item_list:
  state_item_list.remove('deleted')

request_start_date = request.get('from_date', None)
request_stop_date = request.get('at_date', None)
section_uid = context.Base_getSectionUidListForSectionCategory(request.get('section_category',None))

#create a default line dictionary
default_dic={}
default_dic['uid']=""
for event_state in state_item_list:
  default_dic[event_state]=0
default_dic['total']=0
default_dic['ticket_type']=""
default_dic['ticket_title']=""
default_dic['resource']=""

#create the work list
column_list=[]

#create unassigned Line dictionaty and append to the list
unassigned_dic=default_dic.copy()
unassigned_dic['ticket_title']=""
unassigned_dic['ticket_type']=portal.Base_translateString("Unassigned")
#column_list.append(new_dic)

#Return index of uid into the list and append if not exists
def createReturnLine(uid, list_):
  for i in range(len(list_)):
    if list[i]['uid']==uid:
      return i
  new_dic=default_dic.copy()
  new_dic['uid']=uid
  list_.append(new_dic)
  return len(list_)-1

# Prepare the parameters to filter
query_dict = {}
if request_start_date:
  query_dict['delivery.start_date'] = dict(range='min', query=request_start_date)
if request_stop_date:
  query_dict['delivery.stop_date'] = dict(range='ngt',
                                     query=request_stop_date.latestTime())
#Get objects with request parameters
event_list=portal.portal_catalog(portal_type=portal.getPortalEventTypeList(),
                                            **query_dict)
for r_event in event_list:
  event=r_event.getObject()
  if event.getSimulationState() in state_item_list:
    #Follow-up has priority
    if not event.getFollowUpUid() == None:
      ticket=portal.restrictedTraverse(event.getFollowUp())
      #Filter by Source section if it's necessary
      if not section_uid or ticket.getSourceSectionUid() in section_uid :
        i=createReturnLine(event.getFollowUpUid(),column_list)
        column_list[i][event.getSimulationState()]=column_list[i][event.getSimulationState()]+1
        column_list[i]['total']=column_list[i]['total']+1
        if column_list[i]['ticket_type']=="":
          column_list[i]['ticket_title']=ticket.getTitle()
          column_list[i]['ticket_type']=ticket.getTranslatedPortalType()
          column_list[i]['resource']=ticket.getResourceTranslatedTitle()
    else:
      if not event.getCausalityUid() == None:
        event_rel=portal.restrictedTraverse(event.getCausality())
        #check relationship of the event with ticket by causality
        if not event_rel.getFollowUpUid() == None:
          ticket=portal.restrictedTraverse(event_rel.getFollowUp())
          #Filter by Source section if it's necessary
          if not section_uid or ticket.getSourceSectionUid() in section_uid:
            i=createReturnLine(event_rel.getFollowUpUid(),column_list)
            column_list[i][event.getSimulationState()]=column_list[i][event.getSimulationState()]+1
            column_list[i]['total']=column_list[i]['total']+1
            if column_list[i]['ticket_type']=="":
              column_list[i]['ticket_title']=ticket.getTitle()
              column_list[i]['ticket_type']=ticket.getTranslatedPortalType()
              column_list[i]['resource']=ticket.getResourceTranslatedTitle()
        else:
          #Unassigned
          if not section_uid:
            unassigned_dic[event.getSimulationState()]=unassigned_dic[event.getSimulationState()]+1
            unassigned_dic['total']=unassigned_dic['total']+1
      else:
        #Unassigned
        if not section_uid:
          unassigned_dic[event.getSimulationState()]=unassigned_dic[event.getSimulationState()]+1
          unassigned_dic['total']=unassigned_dic['total']+1
#Sort the result and add unassigned
def comparator(x, y):
  if x['ticket_type'] == y['ticket_type']:
    return cmp(x['ticket_title'], y['ticket_title'])
  return cmp(x['ticket_type'], y['ticket_type'])
column_list.sort(comparator)
if unassigned_dic['total']>0: column_list.append(unassigned_dic)
#fill line_list that is returned to report
line_list = []
for row in column_list:
  obj = Object(uid="new_")
  obj['ticket_title']=row['ticket_title']
  obj['ticket_type']=row['ticket_type']
  obj['resource']=row['resource']
  obj['total']=row['total']
  default_dic['total']=default_dic['total']+row['total']
  for event_state in state_item_list:
    obj[event_state]=row[event_state]
    default_dic[event_state]=default_dic[event_state]+row[event_state]
  line_list.append(obj)

#Totals count line
obj = Object(uid="new_")
obj['ticket_title']=portal.Base_translateString('Total')
obj['total']=default_dic['total']
for event_state in state_item_list:
  obj[event_state]=default_dic[event_state]
line_stats_list=[]
line_stats_list.append(obj)
request.set('stat_line',line_stats_list)

return line_list
