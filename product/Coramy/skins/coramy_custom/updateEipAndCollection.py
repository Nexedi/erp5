## Script (Python) "updateEipAndCollection"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# callable on tissu, modele, forme, gamme

categorie_dict = {}
categorie_dict['eip/Baby']=['eip/Baby']
categorie_dict['eip/Baby/Fille']=['eip/Baby/Fille']       
categorie_dict['eip/Baby/Garcon']=['eip/Baby/Garcon']     
categorie_dict['eip/Femme']=['eip/Femme']                 
categorie_dict['eip/Femme/Chic elegante']=['eip/Femme']   
categorie_dict['eip/Femme/Classic']=['eip/Femme']         
categorie_dict['eip/Femme/Confort']=['eip/Femme']         
categorie_dict['eip/Femme/Cote azur']=['eip/Femme']       
categorie_dict['eip/Femme/Maternite']=['eip/Femme']       
categorie_dict['eip/Femme/Piscine']=['eip/Femme']         
categorie_dict['eip/Femme/Rebelle attitude']=['eip/Femme']
categorie_dict['eip/Femme/Separables']=['eip/Femme']      
categorie_dict['eip/Femme/Sportswear']=['eip/Femme']      
categorie_dict['eip/Femme/Surf']=['eip/Femme']            
categorie_dict['eip/Fille']=['eip/Fille']                 
categorie_dict['eip/Fille/Basic line']=['eip/Fille']      
categorie_dict['eip/Fille/Junior']=['eip/Fille']          
categorie_dict['eip/Fille/Nautic']=['eip/Fille']          
categorie_dict['eip/Fille/Piscine']=['eip/Fille']         
categorie_dict['eip/Fille/Pretty girl']=['eip/Fille']     
categorie_dict['eip/Fille/Rayures']=['eip/Fille']         
categorie_dict['eip/Fille/Surf']=['eip/Fille']            
categorie_dict['eip/Garcon']=['eip/Garcon']               
categorie_dict['eip/Garcon/Fantaisie']=['eip/Garcon']     
categorie_dict['eip/Garcon/Junior']=['eip/Garcon']        
categorie_dict['eip/Garcon/Piscine']=['eip/Garcon']       
categorie_dict['eip/Garcon/Surf']=['eip/Garcon']          
categorie_dict['eip/Homme']=['eip/Homme']                 
categorie_dict['eip/Homme/Basic']=['eip/Homme']           
categorie_dict['eip/Homme/Classic']=['eip/Homme']         
categorie_dict['eip/Homme/Piscine']=['eip/Homme']         
categorie_dict['eip/Homme/Surf']=['eip/Homme']            
categorie_dict['eip/Homme/Techno']=['eip/Homme']          

old_category_list = context.getCategoryList()
new_category_list = []
categorie_keys = categorie_dict.keys()
for item in old_category_list :
  if item in categorie_keys :
    for cat_item in categorie_dict[item] :
      if not cat_item in new_category_list :
        new_category_list.append(cat_item)
  else :
    if not item in new_category_list and item.find('modele_origine') == -1:
      new_category_list.append(item)

context.setCategoryList(new_category_list)
