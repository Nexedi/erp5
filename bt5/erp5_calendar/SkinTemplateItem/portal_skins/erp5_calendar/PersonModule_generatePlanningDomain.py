return context.BaseDomain_generateDomainFromSelection(
     script_id=script.id,
     selection_name='person_module_selection',
     membership_criterion_base_category=('source', 'destination'),
     depth=depth, parent=parent, **kw)
