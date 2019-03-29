from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

object_to_check_list = [context]
object_to_check_list.extend(context.getMovementList())

for object in object_to_check_list:
  baobab_source = object.getBaobabSource()
  baobab_destination = object.getBaobabDestination()

  for node_url in (baobab_source,baobab_destination):
    if node_url is not None:
      #context.log('node_url', node_url)
      try:
        node = context.portal_categories.restrictedTraverse(node_url)
      except KeyError:
        context.log('Error on ', (context.getRelativeUrl(),node_url))
        msg = Message(domain='ui',message='Sorry, wrong source or destination')
        raise ValidationFailed(msg,)
