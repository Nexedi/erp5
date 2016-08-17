paysheet = context

getMovementTotalPriceFromCategory = paysheet.PaySheetTransaction_getMovementTotalPriceFromCategory

deduction_mutuelle = getMovementTotalPriceFromCategory(\
    base_contribution='base_contribution/base_amount/payroll/l10n/fr/base/deduction_mutuelle',
    contribution_share='contribution_share/employee')
prix_fixe_mutuelle = context.getRatioQuantityFromReference('prix_fixe_mutuelle') or 0
total_mutuelle = prix_fixe_mutuelle + deduction_mutuelle

salaire_net_imposable = getMovementTotalPriceFromCategory(\
    base_contribution='base_contribution/base_amount/payroll/base/income_tax',
    contribution_share='contribution_share/employee') + total_mutuelle

return salaire_net_imposable
