return context.AccountModule_getBankAccountItemList(
        organisation=context.getSourceSection(),
        skip_invalidated_bank_accounts=
                    (context.getValidationState() != 'delivered'))
