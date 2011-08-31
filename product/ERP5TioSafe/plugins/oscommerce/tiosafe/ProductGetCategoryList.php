<?php
	include_once('functions.php');
  include_once('../includes/configure.php');
  include_once('../includes/database_tables.php');
  include_once('../includes/functions/database.php');

  tep_db_connect() or die('Unable to connect to database');

  if (postOK('product_id') && !verifyExistence(TABLE_PRODUCTS, 'products_id', $_POST['product_id'])) {
    header('Content-type: text/xml');
    echo '<xml></xml>';
    die();
  } 
  if (postOK('order_id') && !verifyExistence(TABLE_ORDERS, 'orders_id', $_POST['order_id'])) {
    header('Content-type: text/xml');
    echo '<xml></xml>';
    die();
  }
	if ( postOK('product_id') and !postOK('order_id') ) {
  	$product_id = $_POST['product_id'];
		$language_id = getDefaultLanguageID();

		$query = 'select pa.products_attributes_id, po.products_options_name, pov.products_options_values_name from ' . TABLE_PRODUCTS_ATTRIBUTES . ' as pa, ' . TABLE_PRODUCTS_OPTIONS . ' as po, ' . TABLE_PRODUCTS_OPTIONS_VALUES . ' as pov where pa.products_id = ' . $product_id . ' and pa.options_id = po.products_options_id and pa.options_values_id = pov.products_options_values_id and po.language_id = ' . $language_id . ' and pov.language_id = ' . $language_id;	
  	$db_query = tep_db_query($query);

  	$xml = '<xml>';

  	while ( $result = tep_db_fetch_array($db_query) ) {
			$xml .= '<object>';
    	$xml .= '<category>' . $result['products_options_name'] . '/' . strtolower($result['products_options_values_name']) . '</category>';
   	 $xml .= '</object>';
  	}
  
  	$xml .= '</xml>';
	} else if ( postOK('product_id') and postOK('order_id') ) {
		$query = 'select products_options, products_options_values from ' . TABLE_ORDERS_PRODUCTS_ATTRIBUTES . ' where orders_id = ' . $_POST['order_id'] . ' and orders_products_id = ' . $_POST['product_id'];
		$db_query = tep_db_query($query);

		$xml = '<xml>';

		while ( $result = tep_db_fetch_array($db_query) ) {
			$xml .= '<object>';
			$xml .= '<category>' . $result['products_options'] . '/' . strtolower($result['products_options_values']) . '</category>';
			$xml .= '</object>';
		}
		$xml .= '</xml>';
	}

	tep_db_close();

  header('Content-type: text/xml');
  echo $xml;

?> 
