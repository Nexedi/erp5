delivery = context

# By default, we use 'CopyAndPropagate' to accept decision.
delivery.portal_simulation.solveDelivery(delivery, None,
                                         'CopyAndPropagate',
                                         divergence_list=divergence_list)
