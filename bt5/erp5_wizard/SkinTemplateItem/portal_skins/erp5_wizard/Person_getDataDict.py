return {'reference': person.getReference(),
      'validation_state': person.getValidationState(),
      'email': person.getDefaultEmailText(),
      'erp5_uid': context.ERP5Site_getExpressInstanceUid()}
