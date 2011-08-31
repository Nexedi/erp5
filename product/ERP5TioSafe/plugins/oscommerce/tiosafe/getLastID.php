<?php
  /**
   * Returns the ID of the last inserted element in a table
   * We don't use this WSR because the way the ID is retrieved is not efficient
   * and we manage to retrieve directly the after the insertion of the element
   * @see createPerson.php
   * @see createProduct.php
   */
	include_once('database.php');
	include_once('functions.php');
	include_once('../includes/configure.php');
	include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');

	if ( !postNotEmpty('type') ) die('Type not given');

	tep_db_connect() or die('Unable to connect to database');

	$type = $_POST['type'];
	$query = "";

	switch ($type) {
		case 'Person' :
						$query = 'select max(customers_id) as id from ' . TABLE_CUSTOMERS;
						break;
		case 'Product' :
						$query = 'select max(products_id) as id from ' . TABLE_PRODUCTS;
						break;
		default :
						die('Unknown type');
	}

	$xml = executeSQL($query);

	header('Content-type: text/xml');
	echo $xml;
?>
