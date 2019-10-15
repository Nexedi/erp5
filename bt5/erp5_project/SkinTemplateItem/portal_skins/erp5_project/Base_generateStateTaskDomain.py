domain_list = []

started_domain = parent.generateTempDomain(id='confirmed')

started_domain.edit(title="Confirmed",
                    criterion_property_list=['simulation_state'])
started_domain.setCriterion('simulation_state', identity='confirmed')
domain_list.append(started_domain)

open_domain = parent.generateTempDomain(id='not_confirmed')

open_domain.edit(title="Not Confirmed",
                       criterion_property_list=['simulation_state'])
open_domain.setCriterion('simulation_state', identity=['planned', 'ordered', 'draft'])

domain_list.append(open_domain)

cancelled_domain = parent.generateTempDomain(id='cancelled')

cancelled_domain.edit(title="Cancelled",
                       criterion_property_list=['simulation_state'])
cancelled_domain.setCriterion('simulation_state', identity=['cancelled', 'deleted'])

domain_list.append(cancelled_domain)

return domain_list
