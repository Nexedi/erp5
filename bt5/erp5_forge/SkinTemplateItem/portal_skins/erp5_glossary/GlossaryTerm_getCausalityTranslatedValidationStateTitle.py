causality_term = context.getCausalityValue(portal_type='Glossary Term')
if causality_term is not None:
  return causality_term.getTranslatedValidationStateTitle()
