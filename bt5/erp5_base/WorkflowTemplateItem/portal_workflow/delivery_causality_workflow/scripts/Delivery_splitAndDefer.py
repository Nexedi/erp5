delivery = state_change['object']

split_movement_list = state_change['kwargs']['split_movement_list']
start_date = state_change['kwargs']['start_date']
stop_date = state_change['kwargs']['stop_date']

if not len(split_movement_list):
  delivery.updateCausalityState()
  return

tag = delivery.getPath() + '_split'

for movement in split_movement_list:
  delivery.getPortalObject().portal_simulation.solveMovement(
    movement, None, 'SplitAndDefer', start_date=start_date,
    stop_date=stop_date, activate_kw={'tag':tag})

delivery.activate(after_tag=tag).updateCausalityState()

# Create delivery
explanation_uid_list = []
object_ = delivery
while object_ is not None:
  explanation_uid_list.append(object_.getUid())
  object_ = object_.getCausalityValue()
    
previous_tag = None
for delivery_builder in delivery.getBuilderList():
  this_builder_tag = '%s_split_%s' % (delivery.getPath(),
                                      delivery_builder.getId())
  after_tag = [tag]
  if previous_tag:
    after_tag.append(previous_tag)
  delivery_builder.activate(activity='SQLQueue',
                            tag=this_builder_tag,
                            after_tag=after_tag).build(
                                  explanation_uid=explanation_uid_list)
  previous_tag = this_builder_tag
