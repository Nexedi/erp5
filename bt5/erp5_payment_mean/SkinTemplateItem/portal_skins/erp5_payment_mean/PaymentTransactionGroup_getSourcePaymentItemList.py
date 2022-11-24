return context.AccountModule_getBankAccountItemList(
        organisation=context.getSourceSection(),
        base_category='source_payment',
        skip_invalidated_bank_accounts=
                    (context.getValidationState() != 'delivered'))
