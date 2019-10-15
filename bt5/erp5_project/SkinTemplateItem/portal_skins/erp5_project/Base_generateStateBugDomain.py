#list of new open bugs
#list of recently closed bugs


domain_list = []

started_domain = parent.generateTempDomain(id='started')
started_domain.edit(title="Open",
                    criterion_property_list=['simulation_state'])
started_domain.setCriterion('simulation_state', identity=['confirmed', 'ready'])
domain_list.append(started_domain)

closed_domain = parent.generateTempDomain(id='closed')
closed_domain.edit(title="Solved/Closed",
                       criterion_property_list=['simulation_state'])
closed_domain.setCriterion('simulation_state', identity=['delivered', 'stopped'])
domain_list.append(closed_domain)

not_started_domain = parent.generateTempDomain(id='not_started')
not_started_domain.edit(title="Not Confirmed",
                       criterion_property_list=['simulation_state'])
not_started_domain.setCriterion('simulation_state', identity=['draft', 'cancelled'])
domain_list.append(not_started_domain)

return domain_list
