# different part of the configuration process in estimatd percentages
# values for machine with pystones =(1.3600000000000012, 36764.705882352908)
building_bt5_part_percentage = 15.0
installation_bt5_part_percentage = 26.0
activity_part_percentage = 59.0
calc_percentage = 0.0
is_activities_running = len(installation_status['activity_list'])!=0
is_bt5_building_running = installation_status['bt5']['all']==0 and \
                          not is_activities_running

if not is_bt5_building_running:
  all_bt5s = float(installation_status['bt5']['all'])
  current_bt5s = float(installation_status['bt5']['current'])
  if all_bt5s:
    bt5_percent_of_total = current_bt5s / all_bt5s
  else:
    bt5_percent_of_total = 1
  calc_percentage = calc_percentage + building_bt5_part_percentage + \
                    bt5_percent_of_total*installation_bt5_part_percentage

if is_activities_running:
  activity_list = installation_status['activity_list']
  all_activities = float(max(activity_list))
  current_activities = float(activity_list[-1])
  activity_percent_of_total = (all_activities - current_activities)/all_activities
  calc_percentage += activity_percent_of_total*activity_part_percentage
  #context.log('%s\nLast:%s\nAll:%s\-->%s' %(activity_list, current_activities, all_activities, activity_percent_of_total))

return context.ConfiguratorTool_viewRunningInstallationMessageRenderer(percentage=int(calc_percentage))
