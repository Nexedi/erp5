context.log("Naming Convention Violation", "FiscalReportCell_creditorBankAccountsBalance should be renamed FiscalReportCell_getCreditorBankAccountBalance")
return context.FiscalReportCell_getBankAccountBalance(accounts, creditor_only=True, **kw)
