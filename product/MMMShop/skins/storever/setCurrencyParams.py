## Script (Python) "setCurrencyParams"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Set the currency parameters for a specific member
##
currency_manager = context.getCurrencyManager()
member_currency = context.getMemberObj().pref_currency

for currency in currency_manager.listCurrencies():
   if currency.getCode() == member_currency:
      context.REQUEST.set('exchange_rate', currency.getRate())
      context.REQUEST.set('money_unit', currency.getMonetaryUnit())
      context.REQUEST.set('prod_unit', currency.getMonetaryUnit())
      context.REQUEST.set('cur_code', currency.getCode())
