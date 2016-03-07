"""This script returns the list of available accounting plan information.

To make a new accounting plan available to TioLive , add an entry in this list.
"""

Base_translateString = context.Base_translateString

return [
  dict(id='ifrs',
       name=Base_translateString('IAS-IFRS Compliant'),
       root='gap/ias/ifrs',
       bt5='erp5_accounting_l10n_ifrs',),
  dict(id='fr',
       name=Base_translateString('PCG (France)'),
       root='gap/fr/pcg',
       bt5='erp5_accounting_l10n_fr',),
  dict(id='de',
       name=Base_translateString('SKR04 (Germany)'),
       root='gap/de/skr04',
       bt5='erp5_accounting_l10n_de_skr04',),
  dict(id='sn',
       name=Base_translateString('SYSCOA (West Africa)'),
       root='gap/ohada/syscohada',
       bt5='erp5_accounting_l10n_sn',),
  dict(id='br',
       name=Base_translateString('Plano Geral de Contas (Brazil)'),
       root='gap/br/pcg',
       bt5='erp5_accounting_l10n_br_extend',),
  dict(id='lu',
       name=Base_translateString('Standard Luxembourgers Plan(Luxembourg)'),
       root='gap/lu/standard',
       bt5='erp5_accounting_l10n_lu',),
  dict(id='ru',
       name=Base_translateString('Standard Russian Plan (2000 edition)'),
       root='gap/ru/ru2000',
       bt5='erp5_accounting_l10n_ru',),
  dict(id='cn',
       name=Base_translateString('Basic Chinese Plan'),
       root='gap/cn/basic',
       bt5='erp5_accounting_l10n_cn_basic',),
]
