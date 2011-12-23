<?php
  /**
   * Creates a product and returns the ID of the created product in the database
   */
	include_once('functions.php');
	include_once('../includes/configure.php');
	include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');

	tep_db_connect() or die('Unable to connect to database');

	$sql_array = array('products_status' => '1' );
	tep_db_perform(TABLE_PRODUCTS, $sql_array);

	$sql_array = array('products_id' => tep_db_insert_id(),
									   'language_id' => getDefaultLanguageID(),
										 'products_name' => $_POST['title']
										 );
	tep_db_perform(TABLE_PRODUCTS_DESCRIPTION, $sql_array);

	header('Content-type: text/xml');
	echo '<xml><object><id>' . tep_db_insert_id() . '</id></object></xml>';

	tep_db_close();
?>
