## Script (Python) "set_criteria"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Update all topics to create a classification hierarchy
##
global changed
changed = 0

def updateCriterion(topic,root_topic):
  global changed
  # Search for criterium
  my_cryterium = None
  for criterium in topic.listCriteria():
    if criterium.Type() == 'String Criterion':
      my_cryterium = criterium
  if my_cryterium is not None:
    my_cryterium.edit(root_topic + topic.id)
    changed = changed + 1
  else:
    my_cryterium = topic.addCriterion('Subject','String Criterion')
    updateCriterion(topic,root_topic)

def updateSubtopics(topic, root_topic=''):
  updateCriterion(topic,root_topic)
  for subtopic in topic.objectValues('Portal Topic'):
     updateSubtopics(subtopic,root_topic=root_topic + topic.id + '/')

for topic in container.objectValues('Portal Topic'):
  updateSubtopics(topic)

print changed

return printed