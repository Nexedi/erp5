if depth == 0:
  module = context.task_module

  domain = parent.generateTempDomain(id='sub%s' % module.getId())
  domain.edit(title=module.getTitle(),
              membership_criterion_base_category=('parent', ),
              membership_criterion_category=(module.getRelativeUrl(),),
              domain_generator_method_id=script.id,
              uid=module.getUid())
  return [domain]
else:
  return []
