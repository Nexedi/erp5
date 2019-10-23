from Products.ERP5Type.Log import log

domain_list = []

started_domain = parent.generateTempDomain(id='started')

started_domain.edit(title="Confirmed",
                    criterion_property_list=['simulation_state'])
started_domain.setCriterion('simulation_state', identity='confirmed')
domain_list.append(started_domain)

not_started_domain = parent.generateTempDomain(id='not_started')

not_started_domain.edit(title="Not Confirmed",
                       criterion_property_list=['simulation_state'])
not_started_domain.setCriterion('simulation_state', identity=['draft'])

domain_list.append(not_started_domain)


closed_domain = parent.generateTempDomain(id='closed')

closed_domain.edit(title="Closed",
                       criterion_property_list=['simulation_state'])
closed_domain.setCriterion('simulation_state', identity=['delivered', 'stopped'])

domain_list.append(closed_domain)

return domain_list
