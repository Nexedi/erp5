# get all operations related to ths site
# as source
if simulation_state is None:
  simulation_state = ['confirmed']
kwd_source = {'default_source_uid' : site_uid,'simulation_state' : simulation_state}
kwd_destination = {'default_destination_uid' : site_uid,'simulation_state' : simulation_state}
kwd_site = {'default_site_uid' : site_uid,'simulation_state' : simulation_state}
if date is not None:
  kwd_source['delivery.start_date']=date
  kwd_destination['delivery.start_date']=date
  kwd_site['delivery.start_date']=date
if portal_type is not None:
  kwd_source['portal_type'] = portal_type
  kwd_destination['portal_type'] = portal_type
  kwd_site['portal_type'] = portal_type
# as destination
operation_list = list(context.portal_catalog(**kwd_source)) + \
                 list(context.portal_catalog(**kwd_destination)) + \
                      list(context.portal_catalog(**kwd_site))
operation_list_object = [x.getObject() for x in operation_list]

return operation_list_object
