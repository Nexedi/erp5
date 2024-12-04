supplier = context.getSourceSectionValue()
supplier_bank_account = [x for x in supplier.objectValues(portal_type='Bank Account') if x.getValidationState() == 'validated'][0]
return dict(title = supplier_bank_account.getTitle(),
            iban = supplier_bank_account.getIban(),
            bic_code = supplier_bank_account.getBicCode(),
            account_type = supplier_bank_account.getBankAccountType(),
            bank_name = supplier_bank_account.getSourceFreeText()
           )
