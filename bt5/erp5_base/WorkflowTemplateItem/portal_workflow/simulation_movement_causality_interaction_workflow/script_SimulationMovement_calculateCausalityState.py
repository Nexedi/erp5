delivery = state_change['object'].getExplanationValue()
try:
  delivery.aq_explicit.getCausalityState
except AttributeError:
  return
delivery.activate(activity='SQLDict', tag='build:'+delivery.getPath()).Delivery_calculate()
