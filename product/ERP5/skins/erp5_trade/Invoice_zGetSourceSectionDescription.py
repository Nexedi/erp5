## Script (Python) "Invoice_zGetSourceSectionDescription"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
source_section_title = context.getSourceSectionTitle()


case = {
  'Coramy': ('Coramy', 
             '5 bis, rue Denis Cordonnier - 59820 Gravelines - Tél. : 33(0)3 28 51 91 51 -  Fax : 33(0)3 28 23 34 96',
             'MAILLOTS DE BAIN - GYM - SWIMSUITS - FITNESS',
             'S.A.S. au capital de 435.200  - T.V.A. FR 67 611 750 274 - R.C. Dunkerque 611 750 274 - SIRET 611 750 274 00023  - CNUF 15971',
             '40'),
  'BLS': ('BLS' ,
          '5 bis, rue Denis Cordonnier - 59820 Gravelines - Tél. : 33(0)3 28 51 86 26 -  Fax : 33(0)3 28 23 34 96', 
          'LICENSE MAILLOTS DE BAIN DIM FEMME & HOMME',
          'S.A.R.L. au capital de 10.000  - T.V.A. FR 51 442 959 243 - R.C. Dunkerque 442 959 243 - SIRET 442 959 243 00019'
          '60'),
  'Houvenaegel':('Houvenaegel' , 
                 '5 bis, rue Denis Cordonnier - 59820 Gravelines - Tél. : 33(0)3 28 51 91 55 -  Fax : 33(0)3 28 23 34 96', 
                 'MAILLOTS DE BAIN - GYM - SWIMSUITS - FITNESS',
                 'S.A.R.L. au capital de 7.622,45  - T.V.A. FR 07 422 769 810 - R.C. Dunkerque 422 769 810 - SIRET 422 769 810 00025',
                 '20')
}

return case[ source_section_title ]
