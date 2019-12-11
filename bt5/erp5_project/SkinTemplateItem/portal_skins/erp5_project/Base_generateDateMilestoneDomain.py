from DateTime import DateTime
criterion_property = "stop_date"
criterion_property = "delivery.stop_date"
future_domain = parent.generateTempDomain(id="future")
future_domain.edit(title='Future',
                criterion_property_list=[criterion_property])
future_domain.setCriterion(criterion_property, min=DateTime(), max=DateTime('9999/01/01 00:00'))

past_domain = parent.generateTempDomain(id="past")
past_domain.edit(title='Past',
                criterion_property_list=[criterion_property])
past_domain.setCriterion(criterion_property, min=DateTime('2000/01/01 00:00'), max=DateTime())

return [
  future_domain,
  past_domain
]
