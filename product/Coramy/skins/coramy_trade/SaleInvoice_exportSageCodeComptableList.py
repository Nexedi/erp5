## Script (Python) "SaleInvoice_exportSageCodeComptableList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=analytique=None, source_section_title=None, amount_type=None, location=None, compte_client=None
##title=
##
# { analytique: { source_section_title:{ amount_type: { location: } } } }

code_comptable_dict = {

'VENTES': {
  'Coramy': {
    'TTC': {
      'CEE':    compte_client,
      'HCEE':   compte_client,
      'France': compte_client
    },
    'HT': {
      'France': '7011100',
      'CEE':    '7011200',
      'HCEE':   '7011300'
    },
    'discount': {
      'France': '7091100',
      'CEE':    '7091200',
      'HCEE':   '7091300'
    },
    'escompte': {
      'France': '6651000',
      'HCEE':   '6652000',
      'CEE':    '6653000'
    },
    'tva': {
      'CEE':    '4457102',
      'HCEE':   '4457102',
      'France': '4457102'
    },
  },
  'BLS': {
    'TTC': {
      'CEE':compte_client,
      'HCEE':compte_client,
      'France':compte_client
    },
    'HT': {
      'France': '7071000',
      'CEE':    '7071200',
      'HCEE':   '7071300'
    },
    'discount': {
      'France': '7097000',
      'CEE':    '7097200',
      'HCEE':   '7097300'
    },
    'escompte': {
      'France': '6651000',
      'HCEE':   '6652000',
      'CEE':    '6653000'
    },
    'tva': {
      'CEE':    '4457102',
      'HCEE':   '4457102',
      'France': '4457102'
    },
  },
  'Houvenaegel': {
    'TTC': {
      'CEE':    compte_client,
      'HCEE':   compte_client,
      'France': compte_client
    },
    'HT': {
      'France': '7071000',
      'CEE':    '7071200',
      'HCEE':   '7071300'
    },
    'discount': {
      'France': '7097000',
      'CEE':    '7097200',
      'HCEE':   '7097300'
    },
    'escompte': {
      'France': '6651000',
      'HCEE':   '6652000',
      'CEE':    '6653000'
    },
    'tva': {
      'CEE':    '4457102',
      'HCEE':   '4457102',
      'France': '4457102'
    },
  },
}}

return code_comptable_dict[analytique][source_section_title][amount_type][location]
