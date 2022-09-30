getInventory=context.FiscalReportCell_doGetInventory

# pobiera stan kont po stronie credit
getCredit=context.getCredit

# pobiera stan kont po stronie debit
getDebit=context.getDebit

# pobiera różnicę dla kont po obu stronach
getBalance=context.getBalance

class Bil:pass
bil=Bil()

bil.AI1=getBalance(('022',))+getBalance(('072',))
bil.AI2=getBalance(('023',))+getBalance(('073',))
bil.AI3=getBalance(('025',))+getBalance(('074',))
bil.AI4=getBalance(('206','216'))
bil.AI=bil.AI1+bil.AI2+bil.AI3+bil.AI4

bil.AII1a=getBalance(('011','016'))+getBalance(('066',))
bil.AII1b=getBalance(('012',))+getBalance(('062',))
bil.AII1c=getBalance(('013',))+getBalance(('063',))
bil.AII1d=getBalance(('014',))+getBalance(('064',))
bil.AII1e=getBalance(('015','017'))+getBalance(('065','067'))
bil.AII1=bil.AII1a+bil.AII1b+bil.AII1c+bil.AII1d+bil.AII1e
bil.AII2=getBalance(('081','082','083'))+getBalance(('086',))
bil.AII3=getBalance(('206','216'))
bil.AII=bil.AII1+bil.AII2+bil.AII3

bil.AIII=getBalance(('248',)) # XXX:280

bil.AIV1=getBalance(('031',))-getBalance(('041',))
bil.AIV2=getBalance(('032',))-getBalance(('042',))
bil.AIV3a1=getBalance(('033',))-getBalance(('043',))
bil.AIV3a2=getBalance(('034',))-getBalance(('044',))
bil.AIV3a3=getBalance(('252',))-getBalance(('280',))
bil.AIV3a4=getBalance(('035',))-getBalance(('045',))
bil.AIV3a=bil.AIV3a1+bil.AIV3a2+bil.AIV3a3
bil.AIV3b1=getBalance(('036',))-getBalance(('46',))
bil.AIV3b2=getBalance(('037',))-getBalance(('47',))
bil.AIV3b3=getBalance(('254',)) # XXX:280
bil.AIV3b4=getBalance(('038',))-getBalance(('48',))
bil.AIV3b=bil.AIV3b1+bil.AIV3b2+bil.AIV3b3
bil.AIV3=bil.AIV3a+bil.AIV3b
bil.AIV4=getBalance(('039',))-getBalance(('49',))
bil.AIV=bil.AIV1+bil.AIV2+bil.AIV3+bil.AIV4

bil.AV1=getBalance(('643',))
bil.AV2=getBalance(('641','642'))
bil.AV=bil.AV1+bil.AV2

bil.A=bil.AI+bil.AII+bil.AIII+bil.AIV+bil.AV

bil.BI1=getBalance(('31','301'))+getBalance(('341',))
bil.BI2=getBalance(('602','630','501','502','504','531'))-getBalance(('622',))
bil.BI3=getBalance(('607','670'))-getBalance(('622',))
bil.BI4=getBalance(('331','332','333','338','339','303'))-getBalance(('342','343','344','345'))
bil.BI5=getBalance(('206','216'))
bil.BI=bil.BI1+bil.BI2+bil.BI3+bil.BI4+bil.BI5

bil.BII1a=getBalance(('211','213','247'))
bil.BII1b=getBalance(('248',))
bil.BII1=bil.BII1a+bil.BII1b
bil.BII2a=getBalance(('201','203','247'))
bil.BII2b=max(getBalance(('22',)),0) # rozrachunki?
bil.BII2c=max(getBalance(('231','234','243','245','248','251','257','258')),0)
bil.BII2d=getBalance(('244',))
bil.BII2=bil.BII2a+bil.BII2b+bil.BII2c+bil.BII2d
bil.BII=bil.BII1+bil.BII2

bil.BIII1a=getBalance(('141','142','143','252'))-getBalance(('144',)) # XXX: skomasowane
bil.BIII1b=getBalance(('146','147','148','254'))-getBalance(('149',)) # XXX: skomasowane
bil.BIII1c1=getBalance(('10','13'))-getBalance(('138',))
bil.BIII1c2=getBalance(('159',))
bil.BIII1c3=getBalance(('156',))
bil.BIII1c=bil.BIII1c1+bil.BIII1c2+bil.BIII1c3
bil.BIII1=bil.BIII1a+bil.BIII1b+bil.BIII1c
bil.BIII2=getBalance(('160',))-getBalance(('165',))
bil.BIII=bil.BIII1+bil.BIII2

bil.BIV=getBalance(('641','642'))

bil.B=bil.BI+bil.BII+bil.BIII+bil.BIV

bil.aktywa=bil.A+bil.B

bil.pAI=-getBalance(('801',))
bil.pAII=-getBalance(('251',))
bil.pAIII=-getBalance(('150',))
bil.pAIV=-getBalance(('806',))
bil.pAV=-getBalance(('807',))
bil.pAVI=-getBalance(('808',))
bil.pAVII=-getBalance(('821',))
pl=context.ProfitAndLoss_calculateCells()
bil.pAVIII=pl.N
#bil.pAVIII=-942 # call ProfitAndLoss_calculateCells
bil.pAIX=-getBalance(('822',))
bil.pA=bil.pAI+bil.pAII+bil.pAIII+bil.pAIV+bil.pAV+bil.pAVI+bil.pAVII+bil.pAVIII+bil.pAIX

bil.pBI1=-getBalance(('831',))
bil.pBI2=-getBalance(('833',)) # zmienione
bil.pBI3=-getBalance(('832','834','646'))
bil.pBI=bil.pBI1+bil.pBI2+bil.pBI3
bil.pBII1=0 # zmienione - nie mamy tego rozr�nienia
bil.pBII2a=-getBalance(('138','255'))
bil.pBII2b=-getBalance(('259',))
bil.pBII2c=-getBalance(('251','256','258'))
bil.pBII2d=0
bil.pBII2=bil.pBII2a+bil.pBII2b+bil.pBII2c+bil.pBII2d
bil.pBII=bil.pBII1+bil.pBII2
bil.pBIII1=0 # jw
bil.pBIII2a=-getBalance(('139','255'))
bil.pBIII2b=-getBalance(('259',))
bil.pBIII2c=-getBalance(('251','256','257','258'))
bil.pBIII2d=-getBalance(('202','204','246','301','302','303','304'))
bil.pBIII2e=-getBalance(('205','842'))
bil.pBIII2f=-getBalance(('207',))
bil.pBIII2g=-min(getBalance(('22',)),0) # rozrachunki?
bil.pBIII2h=-min(getBalance(('231',)),0)
bil.pBIII2i=-min(getBalance(('234','245','248','257')),0)
bil.pBIII2=bil.pBIII2a +bil.pBIII2b +bil.pBIII2c +bil.pBIII2d +bil.pBIII2e +bil.pBIII2f +bil.pBIII2g +bil.pBIII2h +bil.pBIII2i
bil.pBIII3=-getBalance(('851','859'))
bil.pBIII=bil.pBIII1+bil.pBIII2+bil.pBIII3
bil.pBIV1=-getBalance(('841',))
bil.pBIV2=-getBalance(('843','844','845')) # czy rozr�nienie termin�w jest wa�ne? to tzreba by albo zmieni� plan kont, albo liczy� wg terminu
bil.pBIV=bil.pBIV1+bil.pBIV2

bil.pB=bil.pBI+bil.pBII+bil.pBIII

bil.pasywa=bil.pA+bil.pB













return bil

# vim:syntax=python
