<?php
  /**
   * Retrieves all the products of the products table
   */
	include_once('database.php');
  include_once('functions.php');
	include_once('../includes/configure.php');
	include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');

	tep_db_connect() or die('Unable to connect to database');

  if (postOK('products_id') && !verifyExistence(TABLE_PRODUCTS, 'products_id', $_POST['product_id'])) {
    header('Content-type: text/xml');
    echo '<xml></xml>';
    die();
  }
	$language_id = getDefaultLanguageID();
	$query = 'select p.products_id as id, p.products_id as reference, pd.products_name as title from ' . TABLE_PRODUCTS . ' as p, ' . TABLE_PRODUCTS_DESCRIPTION . ' as pd where p.products_id = pd.products_id and pd.language_id = ' . $language_id;

	if ( postOK('product_id') ) $query .= ' and p.products_id = ' . $_POST['product_id'];

	header('Content-type: text/xml');
	echo executeSQL($query);

	tep_db_close();
?>
