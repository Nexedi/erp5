return context.getPortalObject().portal_catalog(
    portal_type='Glossary Term',
    reference=context.getReference(),
    uid='!=%d' % context.getUid(),
    language=context.getLanguage(),
    business_field_uid=context.getBusinessFieldUid(),
    validation_state=('draft', 'validated'),
    **kw)
