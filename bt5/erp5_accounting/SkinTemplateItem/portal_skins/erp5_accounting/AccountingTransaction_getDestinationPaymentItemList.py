return context.AccountModule_getBankAccountItemList(
        organisation=context.getDestinationSection(),
        base_category='destination_payment',
        skip_invalidated_bank_accounts=
                    (context.getSimulationState() != 'delivered'))
