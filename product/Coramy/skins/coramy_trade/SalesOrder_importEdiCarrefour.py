## Script (Python) "SalesOrder_importEdiCarrefour"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=line_header, argument, item_sales_order, products_list, useful_functions, **kw
##title=
##
# import d'un fichier EDI Carrefour
# format de fichier attendu
# Traduction .rec du fichier Edifact par NY Net


def read_START(argument, item_sales_order, products_list ):
	item_sales_order.setGroup('Carrefour International/Carrefour France')
	# recuperation du client et du destinataire
	functions =  (	
		(argument[2], item_sales_order.setSourceSection),
		(argument[3], item_sales_order.setDestinationDecision)
	)

	for tuple in functions:
		useful_functions['link_with_organisation'](tuple[0], tuple[1], 'Organisation')



def read_UNH(argument, item_sales_order, products_list ):
	None

def read_BGM(argument, item_sales_order, products_list ):
	item_sales_order.setDestinationReference(argument[1])




def read_DTM(argument, item_sales_order, products_list ):
	date = argument[1][:4] + '/' + argument[1][4:6] + '/' + argument[1][6:8] 

	case = {
		'2':item_sales_order.setTargetStopDate,
		# date livraison demandee
		'137':None,
		# date du document
		'200':None
		# date enlevement cargaison
	}
	if case[argument[0]] != None:
		case[argument[0]](date)

def read_NAD(argument, item_sales_order, products_list ):
	case = {
		#'BY':item_sales_order.setDestinationPayment ,
		'BY':item_sales_order.setDestinationDecision,
		# acheteur
		'SU':item_sales_order.setSourceSection ,
		# fournisseur
		# source_section
		'DP':item_sales_order.setDestination
		# intervenant a livrer
		# destination
	}

	useful_functions['link_with_organisation'](argument[1], case[argument[0]], 'Organisation')


def read_CUX(argument, item_sales_order, products_list ):
	if argument[2] == '9':
		item_sales_order.setPriceCurrency('devise/'+argument[1])

def read_TDT(argument, item_sales_order, products_list ):
	#item_sales_order.setDeliveryMode(.....)
	# nothing interesting to get
	None
		
def read_LIN(argument, item_sales_order, products_list ):
	# get ean13 code
	products_list.append( (argument[0], []) )
	None
	
def read_IMD(argument, item_sales_order, products_list ):
	# nothing interesting to get
	None

def read_QTY(argument, item_sales_order, products_list ):
	products_list[ len(products_list) - 1 ][1].append( [argument[1], None] )

def read_PRI(argument, item_sales_order, products_list ):
	list_tuple = products_list[ len(products_list) - 1 ][1]   
	list_tuple[ len(list_tuple) - 1 ][1] = argument[0]

def read_UNS(argument, item_sales_order, products_list ):
	None

# dictionary of the functions
functions_list = {
	'START':read_START,
	'UNH':read_UNH,
	'BGM':read_BGM,
	'DTM':read_DTM,
	'NAD':read_NAD,
	'CUX':read_CUX,
	'TDT':read_TDT,
	'LIN':read_LIN,
	'IMD':read_IMD,
	'QTY':read_QTY,
	'PRI':read_PRI,
	'UNS':read_UNS
}

# execute a function
functions_list[line_header](argument, item_sales_order, products_list )
