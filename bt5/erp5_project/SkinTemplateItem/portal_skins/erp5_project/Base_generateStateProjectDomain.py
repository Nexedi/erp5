domain_list = []

started_domain = parent.generateTempDomain(id='started')

started_domain.edit(title="Started",
                    criterion_property_list=['validation_state'])
started_domain.setCriterion('validation_state', identity='validated')
domain_list.append(started_domain)

not_started_domain = parent.generateTempDomain(id='not_started')

not_started_domain.edit(title="Not Started",
                       criterion_property_list=['validation_state'],
                       identity_criterion=dict(validation_state=('invalidated')))
not_started_domain.setCriterion('validation_state', identity=['draft', 'invalidated', 'suspended'])

domain_list.append(not_started_domain)

return domain_list
