## Script (Python) "sample_order_line_copy_price"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=
##
request = context.REQUEST

# First define some data
# which should better be defined as portal data
cout_minute_france = 0.348
cout_minute_tunisie = 0.174
cout_fixe_article = 0.404
ratio_securite_temps = 1.075
ratio_securite_appro = 1.07
france_ratio_dict = {
  'F0_T100' : 0.0,
  'F20_T80' : 0.2,
  'F50_T50' : 0.5,
  'F80_T20' : 0.8,
  'F100_T0' : 1.0
}
coef_qte_dict = {}
coef_qte_dict['00300'] = 85.0/72.5
coef_qte_dict['01000'] = 1
coef_qte_dict['05000'] = 85.0/92.5
coef_qte_dict['10000'] = 0.88

ligne = context
modele = ligne.getDefaultValue('resource',portal_type=['Modele'])

if modele <> None :
  modele_tarif_list = modele.contentValues(filter={'portal_type':'Element Tarif'})
  if modele.getTarif() <> ligne.getTarif() and modele.getTempsPiquage() == 0 :
    redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Pas+de+temps+de+piquage+pour+ce+modele.'
                              )
  else :
    for modele_tarif in modele_tarif_list :
      ligne.invokeFactory(type_name="Element Tarif",
                                   id=modele_tarif.id,
                                   RESPONSE=request.RESPONSE)
      ligne[modele_tarif.id].edit(description = modele_tarif.getDescription(), category_list = modele_tarif.getCategoryList(), commentaires = modele_tarif.getCommentaires())
      ligne[modele_tarif.id].setCellRange([None],ligne[modele_tarif.id].getQuantityRangeList(),base_id='destination_base_price')
      for q in ligne[modele_tarif.id].getQuantityRangeList():
        price_value = 0
        ecart = 0
        if modele.getTarif() == ligne.getTarif() :
          price_value = modele_tarif.getCell(None, q, base_id='destination_base_price').destination_base_price*ligne.getCoefMarge()/modele.getCoefMarge()
        else :
          price_value = modele_tarif.getCell(None, q, base_id='destination_base_price').destination_base_price/modele.getCoefMarge()
          if modele.getCoefMajoration() <> 0 :
            price_value = price_value/modele.getCoefMajoration()
          ecart = (france_ratio_dict[ligne.getTarif()]*cout_minute_france+(1-france_ratio_dict[ligne.getTarif()])*cout_minute_tunisie)*modele.getTempsPiquage()*1.075
          ecart += -1*(france_ratio_dict[modele.getTarif()]*cout_minute_france+(1-france_ratio_dict[modele.getTarif()])*cout_minute_tunisie)*modele.getTempsPiquage()*1.075
          price_value += ecart*coef_qte_dict[q]
          price_value = price_value*ligne.getCoefMarge()

        if ligne.getCoefMajoration() <> 0 :
          price_value = price_value*ligne.getCoefMajoration()
        cell = ligne[modele_tarif.id].newCell(None, q, base_id='destination_base_price')
        cell.edit(mapped_value_attribute_list = ('destination_base_price',),
                   domain_base_category_list = ('quantity_range',),
                   predicate_operator = 'SUPERSET_OF',
                   predicate_value_list = ('quantity_range/%s' % q,),
                   destination_base_price = round(price_value,2))
        if q == '01000' :
          ligne[modele_tarif.id].edit(destination_base_price = round(price_value,2))


    redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=%s+elements+de+tarif+crees.'%len(modele_tarif_list)
                              )

else :

  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Problème+de+modèle.'
                              )


request[ 'RESPONSE' ].redirect( redirect_url )
