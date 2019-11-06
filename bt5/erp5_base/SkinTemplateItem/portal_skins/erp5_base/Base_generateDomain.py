domain = parent.generateTempDomain(id=id)
domain.edit(title=title,
            criterion_property_list=[criterion_property])
domain.setCriterion(criterion_property, identity=criterion_identity)
return domain
