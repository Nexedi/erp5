## Script (Python) "SalesOrder_importEdiAuchan"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=line_header, argument, item_sales_order, products_list, useful_functions, **kw
##title=
##
# import d'un fichier EDI Auchan
# format de fichier attendu
# Traduction .rec du fichier Edifact par NY Net

def read_START(argument, item_sales_order, products_list ):
	item_sales_order.setGroup('Auchan International/Auchan France')
	"""
	# recuperation du client et du destinataire
	functions =  (	
		(argument[2], item_sales_order.setSourceSection),
		(argument[3], item_sales_order.setDestinationDecision)
	)
	for tuple in functions:
		useful_functions['link_with_organisation'](tuple[0], tuple[1], 'Organisation')
	"""

def read_ALC_DEDUCTION_FRAIS(argument, item_sales_order, products_list ):
	None

def read_BGM_TYPE_DOCUMENT(argument, item_sales_order, products_list ):
	# nothing interesting to get
	None

def read_BGM_NUMERO_DOCUMENT(argument, item_sales_order, products_list ):
	item_sales_order.setDestinationReference(argument[0])
	
def read_CNT_TOTAL_CONTROLE(argument, item_sales_order, products_list ):
	None
def read_CUX_MONNAIE(argument, item_sales_order, products_list ):
	# nothing interesting to get
	item_sales_order.setPriceCurrency('devise/'+'EUR')
	None

def read_DTM_DATE_COMMANDE(argument, item_sales_order, products_list ):
	# nothing interesting to get
	None
def read_DTM_DATE_DEPART(argument, item_sales_order, products_list ):
	date = argument[1][:4] + '/' + argument[1][4:6] + '/' + argument[1][6:8] 
	item_sales_order.setTargetStopDate(date)

def read_DTM_DATE_LIVRAISON(argument, item_sales_order, products_list ):
	date = argument[1][:4] + '/' + argument[1][4:6] + '/' + argument[1][6:8] 
	item_sales_order.setTargetStopDate(date)

def read_DTM_DATE_REFERENCE(argument, item_sales_order, products_list ):
	None

def read_LIN_ARTICLE(argument, item_sales_order, products_list ):
	# get ean13 code
	products_list.append( (argument[0], []) )


def read_LOC_EMPLACEMENT(argument, item_sales_order, products_list ):
	None
def read_MEA_MESURES(argument, item_sales_order, products_list ):
	None
def read_MOA_MONTANT_REMISE(argument, item_sales_order, products_list ):
	None
def read_NAD_ACHETEUR(argument, item_sales_order, products_list ):
	#useful_functions['link_with_organisation'](argument[0], item_sales_order.setDestinationPayment   , 'Organisation')
	useful_functions['link_with_organisation'](argument[0], item_sales_order.setDestinationDecision, 'Organisation')
	
def read_NAD_FOURNISSEUR(argument, item_sales_order, products_list ):
	useful_functions['link_with_organisation'](argument[0], item_sales_order.setSourceSection,  'Organisation')

def read_NAD_LIEU_LIVRAISON(argument, item_sales_order, products_list ):
	# code EAN inconnu de Coramy, solution temporaire ...
	item_sales_order.setDestination(item_sales_order.getDestinationDecision())
	
	#useful_functions['link_with_organisation'](argument[0], item_sales_order.setDestination,  'Organisation')
	
def read_PAC_EMBALLAGE(argument, item_sales_order, products_list ):
	None
def read_PCD_POURCENTAGE(argument, item_sales_order, products_list ):
	None
def read_PIA_COMPLEMENT_PRODUI(argument, item_sales_order, products_list ):
	None
def read_PRI_PRIX_UNIT_NET(argument, item_sales_order, products_list ):
	list_tuple = products_list[ len(products_list) - 1 ][1]   
	list_tuple[ len(list_tuple) - 1 ][1] = argument[0]

def read_QTY_PAR_COMBIEN(argument, item_sales_order, products_list ):
	None
def read_QTY_QUANTITE_CDE(argument, item_sales_order, products_list ):
	#products_list[ len(products_list) - 1 ][1].append( (argument[0],) )
	products_list[ len(products_list) - 1 ][1].append( [argument[0],None] )

def read_QTY_QUANTITE_GRATUITE(argument, item_sales_order, products_list ):
	None
def read_RFF_REFERENCE_OPERATI(argument, item_sales_order, products_list ):
	None
def read_TDT_TRANSPORT(argument, item_sales_order, products_list ):
	None
def read_TOD_CONDITION_LIVRAIS(argument, item_sales_order, products_list ):
	None
def read_UNH_ENTETE_COMMANDE(argument, item_sales_order, products_list ):
	# nothing interesting to get
	None
def read_UNS_SECTION_MESSAGE(argument, item_sales_order, products_list ):
	None

# dictionary of the functions
functions_list = {
	'START':read_START,
	'ALC_DEDUCTION_FRAIS__':read_ALC_DEDUCTION_FRAIS,
	'BGM_TYPE_DOCUMENT____':read_BGM_TYPE_DOCUMENT,
	'BGM_NUMERO_DOCUMENT__':read_BGM_NUMERO_DOCUMENT,
	'CNT_TOTAL_CONTROLE___':read_CNT_TOTAL_CONTROLE,
	'CUX_MONNAIE__________':read_CUX_MONNAIE,
	'DTM_DATE_COMMANDE____':read_DTM_DATE_COMMANDE,
	'DTM_DATE_DEPART______':read_DTM_DATE_DEPART,
	'DTM_DATE_LIVRAISON___':read_DTM_DATE_LIVRAISON,
	'DTM_DATE_REFERENCE___':read_DTM_DATE_REFERENCE,
	'LIN_ARTICLE__________':read_LIN_ARTICLE,
	'LOC_EMPLACEMENT______':read_LOC_EMPLACEMENT,
	'MEA_MESURES__________':read_MEA_MESURES,
	'MOA_MONTANT_REMISE___':read_MOA_MONTANT_REMISE,
	'NAD_ACHETEUR_________':read_NAD_ACHETEUR,
	'NAD_FOURNISSEUR______':read_NAD_FOURNISSEUR,
	'NAD_LIEU_LIVRAISON___':read_NAD_LIEU_LIVRAISON,
	'PAC_EMBALLAGE________':read_PAC_EMBALLAGE,
	'PCD_POURCENTAGE______':read_PCD_POURCENTAGE,
	'PIA_COMPLEMENT_PRODUI':read_PIA_COMPLEMENT_PRODUI,
	'PRI_PRIX_UNIT_NET____':read_PRI_PRIX_UNIT_NET,
	'QTY_PAR_COMBIEN______':read_QTY_PAR_COMBIEN,
	'QTY_QUANTITE_CDE_____':read_QTY_QUANTITE_CDE,
	'QTY_QUANTITE_GRATUITE':read_QTY_QUANTITE_GRATUITE,
	'RFF_REFERENCE_OPERATI':read_RFF_REFERENCE_OPERATI,
	'TDT_TRANSPORT________':read_TDT_TRANSPORT,
	'TOD_CONDITION_LIVRAIS':read_TOD_CONDITION_LIVRAIS,
	'UNH_ENTETE_COMMANDE__':read_UNH_ENTETE_COMMANDE,
	'UNS_SECTION_MESSAGE__':read_UNS_SECTION_MESSAGE
}
# execute a function
functions_list[line_header](argument, item_sales_order, products_list )
