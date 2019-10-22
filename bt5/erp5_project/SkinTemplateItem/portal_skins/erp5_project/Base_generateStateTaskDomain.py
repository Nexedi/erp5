domain_list = []

started_domain = parent.generateTempDomain(id='started')

started_domain.edit(title="Confirmed",
                    criterion_property_list=['simulation_state'])
started_domain.setCriterion('simulation_state', identity='confirmed')
domain_list.append(started_domain)

not_started_domain = parent.generateTempDomain(id='not_started')

not_started_domain.edit(title="Not Confirmed",
                       criterion_property_list=['simulation_state'])
not_started_domain.setCriterion('simulation_state', identity=['planned', 'ordered', 'draft', 'cancelled'])

domain_list.append(not_started_domain)

return domain_list
