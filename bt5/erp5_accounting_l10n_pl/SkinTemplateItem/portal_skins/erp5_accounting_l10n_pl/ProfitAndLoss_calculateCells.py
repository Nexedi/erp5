getInventory=context.FiscalReportCell_doGetInventory

# pobiera stan kont po stronie credit
getCredit=context.getCredit

# pobiera stan kont po stronie debit
getDebit=context.getDebit

# pobiera różnicę dla kont po obu stronach
getBalance=context.getBalance

class PL:pass
pl=PL()

pl.AI=-getBalance(('70',))
pl.AII=getBalance(('490',))
pl.AIII=getBalance(('790',))
pl.AIV=-getBalance(('731','732','733','740'))
pl.A=pl.AI+pl.AII+pl.AIII+pl.AIV

pl.BI=getBalance(('408',))
pl.BII=getBalance(('401',))
pl.BIII=getBalance(('402',))
pl.BIV=getBalance(('403',))
pl.BV=getBalance(('404',))
pl.BVI=getBalance(('405',))
pl.BVII=getBalance(('409',))
pl.BVIII=getBalance(('736','737','738','741'))
pl.B=pl.BI+pl.BII+pl.BIII+pl.BIV+pl.BV+pl.BVI+pl.BVII+pl.BVIII

pl.C=pl.A-pl.B

pl.DI=max(getBalance(('761',))-getBalance(('766',)),0)
pl.DII=-getBalance(('762',))
pl.DIII=-getBalance(('763','764'))
pl.D=pl.DI+pl.DII+pl.DIII

pl.EI=max(getBalance(('766',))-getBalance(('761',)),0)
pl.EII=getBalance(('767',))
pl.EIII=getBalance(('768','769'))
pl.E=pl.EI+pl.EII+pl.EIII

pl.F=pl.C+pl.D-pl.E

pl.GI=-getBalance(('750',))
pl.GII=-getBalance(('751',))
pl.GIII=max(getBalance(('752',)) -getBalance(('761',)),0)
pl.GIV=-getBalance(('753',))
pl.GV=-getBalance(('754',))

pl.G=pl.GI+pl.GII+pl.GIII+pl.GIV+pl.GV

pl.HI=getBalance(('757',))
pl.HII=max(getBalance(('756',)) -getBalance(('752',)),0)
pl.HIII=getBalance(('758',))
pl.HIV=getBalance(('759',))
pl.H=pl.HI+pl.HII+pl.HIII+pl.HIV

pl.I=pl.F+pl.G-pl.H

pl.JI=getBalance(('770',))
pl.JII=getBalance(('771',))
pl.J=pl.JI-pl.JII

pl.K=pl.I+pl.J

pl.L=getBalance(('871',))

pl.M=getBalance(('872',))

pl.N=pl.K-pl.L-pl.M

return pl

# vim:syntax=python
