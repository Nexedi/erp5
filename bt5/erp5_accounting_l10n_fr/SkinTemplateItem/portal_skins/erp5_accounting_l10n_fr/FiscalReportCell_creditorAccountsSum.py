context.log("Naming Convention Violation", "FiscalReportCell_creditorAccountsSum should be renamed FiscalReportCell_getCreditorBalance")
return context.FiscalReportCell_getBalance(accounts, creditor_only=True, **kw)
