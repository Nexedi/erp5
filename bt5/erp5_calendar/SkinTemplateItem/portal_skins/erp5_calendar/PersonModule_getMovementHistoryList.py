portal = context.getPortalObject()
selection_name = 'person_module_selection'
person_list = portal.portal_selections.getSelectionCheckedValueList(selection_name)
if not person_list:
  person_list = portal.portal_selections.callSelectionFor(selection_name)

# Select only the visible part
main_axis_begin = context.REQUEST.get('list_start', 0)
form = getattr(context, 'PersonModule_viewPlanning')
planning_box = form.get_field('planning_box')
main_axis_end = main_axis_begin + planning_box.get_value('main_axis_groups')

node_uid_list = [x.uid for x in person_list[main_axis_begin:main_axis_end]]

acceptable_state_list = context.getPortalFutureInventoryStateList() + \
                        context.getPortalReservedInventoryStateList() + \
                        context.getPortalTransitInventoryStateList() + \
                        context.getPortalCurrentInventoryStateList()

movement_list = context.portal_simulation.getMovementHistoryList(
                   node_uid=node_uid_list,
                   portal_type=portal_type,
                   simulation_state=acceptable_state_list,
                   to_date=to_date,
                   from_date=from_date,
                   omit_mirror_date=0,
)


# XXX It is a bad idea to return order_value or delivery_value,
# because same object can be displayed multiple time in some cases

return_list = []

# Normally, simulation movement should only have 1 order value
for mvt_obj in movement_list:
  # XXX Can't we use a brain instead ?
  if mvt_obj.portal_type == "Simulation Movement":
    obj = mvt_obj.getOrderValue()
    if obj is not None:
      mvt_obj = obj
  return_list.append(mvt_obj)

return return_list
