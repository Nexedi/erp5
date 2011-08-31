<?php
  /**
   * Deletes the product matching the given ID
   */
	include_once('functions.php');
  include_once('../includes/configure.php');
  include_once('../includes/functions/database.php');
  include_once('../includes/database_tables.php');

	if ( !postNotEmpty('id') ) die('Product not given');

  tep_db_connect() or die("Unable to connect to database server");

  $query = 'delete from '  . TABLE_PRODUCTS . ' where products_id = ' . $_POST['product_id'];
  tep_db_query($query);
  
  $query = 'delete from ' . TABLE_PRODUCTS_DESCRIPTION . ' where products_id = ' . $_POST['product_id'];
	tep_db_query($query);

	tep_db_close();
?>
