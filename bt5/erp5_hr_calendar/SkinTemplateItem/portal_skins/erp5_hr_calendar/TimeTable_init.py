# Create a first line to retrieve list of days
int_index = 0
line = context.newContent(int_index=int_index)
day_list = line.getWeekDayList()
line.edit(day_of_week=day_list[0])
tag = "%s_reindex" % context.getRelativeUrl()

# Create other lines
for day in day_list[1:]:
  int_index+=1
  context.newContent(int_index=int_index, day_of_week=day,
                     activate_kw={"tag": tag})
# after indexing, make sure to update periodicity stop date
context.getPortalObject().portal_alarms.update_time_table_end_periodicity.activate(
  activity='SQLDict',
  after_tag=tag, priority=5).activeSense()
