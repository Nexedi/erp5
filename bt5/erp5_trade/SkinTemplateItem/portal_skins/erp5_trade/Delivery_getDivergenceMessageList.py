divergence_messages_list =  context.getDivergenceList()

from Products.ERP5Type.Document import newTempBase

portal_object = context.getPortalObject()
l = []

# function to create a new fast input line
def createInputLine(d_message, new_id):
  int_len = 3

  o = newTempBase( portal_object
                 , str(new_id)
                 , uid ='new_%s' % str(new_id).zfill(int_len)
                 ,  message = str(d_message.getTranslatedMessage())
                 ,  tested_property_id = d_message.getProperty('tested_property')
                 ,  object_title =  d_message.getObject().getTranslatedTitle()
                 ,  prevision_value = d_message.getProperty('prevision_value')
                 ,  decision_value = d_message.getProperty('decision_value')
                 , solver_script_list = d_message.getProperty('solver_script_list'))

  l.append(o)

# generate all lines for the fast input form
for i, d_message in enumerate(divergence_messages_list):
  createInputLine(d_message, i)

# return the list of fast input lines

return l
