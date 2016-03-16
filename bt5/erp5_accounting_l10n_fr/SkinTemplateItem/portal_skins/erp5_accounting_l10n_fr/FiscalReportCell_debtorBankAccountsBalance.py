context.log("Naming Convention Violation", "FiscalReportCell_debtorBankAccountsBalance should be renamed FiscalReportCell_getDebtorBankAccountBalance")
return context.FiscalReportCell_getBankAccountBalance(accounts, debtor_only=True, **kw)
