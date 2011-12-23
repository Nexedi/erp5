<?php
  /**
   * Deletes the person matching the given ID
   * We don't delete persons and addresses in the plugin side
   */
	include_once('functions.php');
	include_once('../includes/configure.php');
	include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');

	if ( !postNotEmpty('person_id') ) die('Person Id not given');

	tep_db_connect() or die('Unable to connect to database');

	$query = 'delete from ' . TABLE_CUSTOMERS . ' where customers_id = ' . $_POST['person_id'];
	tep_db_query($query);

	$query = 'delete from ' . TABLE_ADDRESS_BOOK . ' where customers_id = ' . $_POST['person_id'];
	tep_db_query($query);

	tep_db_close();
?>
