<?php
  /**
   * Retrieves all the lines (products linked with an order) of an order
   */
	include_once('database.php');
  include_once('functions.php');
  include_once('../includes/configure.php');
  include_once('../includes/functions/database.php');
  include_once('../includes/database_tables.php');
  include_once('../includes/functions/general.php');

  tep_db_connect() or die('Unable to connect to database');

  if (!postOK('sale_order_id') or !verifyExistence(TABLE_ORDERS_PRODUCTS, 'orders_id', $_POST['sale_order_id'])) {
    header('Content-type: text/xml');
    echo '<xml></xml>';
    die();
  }

  $query = 'select orders_products_id as id, products_name as title, concat_ws(" ", "", products_name) as reference, products_price as price, products_quantity as quantity, products_tax as vat from ' . TABLE_ORDERS_PRODUCTS . ' where orders_id = ' . $_POST['sale_order_id'];
  
	header('Content-type: text/xml');
	echo executeSQL($query);

	tep_db_close();
?>
