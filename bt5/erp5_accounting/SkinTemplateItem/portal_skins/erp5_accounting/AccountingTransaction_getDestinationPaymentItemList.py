return context.AccountModule_getBankAccountItemList(
        organisation=context.getDestinationSection(),
        skip_invalidated_bank_accounts=
                    (context.getSimulationState() != 'delivered'))
