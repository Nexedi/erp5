"""This script returns the list of available translation business templates.

"""

Base_translateString = context.Base_translateString

return [
  dict(id='fr',
       name=Base_translateString('French'),
       bt5='erp5_l10n_fr',),
  dict(id='de',
       name=Base_translateString('German'),
       bt5='erp5_l10n_de',),
  dict(id='pl',
       name=Base_translateString('Polish'),
       bt5='erp5_l10n_pl_PL',),
  dict(id='pt-BR',
       name=Base_translateString('Portuguese / Brazil'),
       bt5='erp5_l10n_pt-BR',),
  dict(id='ko',
       name=Base_translateString('Korean'),
       bt5='erp5_l10n_ko',),
  dict(id='ru',
       name=Base_translateString('Russian'),
       bt5='erp5_l10n_ru',),
  dict(id='zh',
       name=Base_translateString('Chinese'),
       bt5='erp5_l10n_zh',),
]
