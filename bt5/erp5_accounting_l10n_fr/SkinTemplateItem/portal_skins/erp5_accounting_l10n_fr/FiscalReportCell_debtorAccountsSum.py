context.log("Naming Convention Violation", "FiscalReportCell_debtorAccountsSum should be renamed FiscalReportCell_getDebtorBalance")
return context.FiscalReportCell_getBalance(accounts, debtor_only=True, **kw)
