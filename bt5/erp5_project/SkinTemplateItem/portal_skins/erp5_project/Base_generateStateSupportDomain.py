domain_list = []

validated_domain = parent.generateTempDomain(id='validated')

validated_domain.edit(title="Validated",
                    criterion_property_list=['simulation_state'])
validated_domain.setCriterion('simulation_state', identity='validated')
domain_list.append(validated_domain)

not_validated_domain = parent.generateTempDomain(id='not_validated')

not_validated_domain.edit(title="Not Validated",
                       criterion_property_list=['simulation_state'])
not_validated_domain.setCriterion('simulation_state', identity=['submitted', 'suspended', 'draft', 'invalidated'])

domain_list.append(not_validated_domain)

cancelled_domain = parent.generateTempDomain(id='cancelled')

cancelled_domain.edit(title="Cancelled",
                       criterion_property_list=['simulation_state'])
cancelled_domain.setCriterion('simulation_state', identity=['cancelled', 'deleted'])

domain_list.append(cancelled_domain)

return domain_list
