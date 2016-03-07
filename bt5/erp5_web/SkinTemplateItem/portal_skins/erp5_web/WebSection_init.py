# List no document until at least one Criterion is created.
# BBB: property does not exist on old property sheets
getattr(context, 'setEmptyCriterionValid', lambda _: None)(False)
