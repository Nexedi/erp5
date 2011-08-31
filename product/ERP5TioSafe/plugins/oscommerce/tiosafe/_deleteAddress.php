<?php
  /**
   * Deletes the address matching the given ID
   * We don't delete persons and addresses in the plugin side
   */
	include_once('functions.php');
	include_once('../includes/configure.php');
	include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');
	include_once('../includes/functions/general.php');

	if ( !postNotEmpty('address_id') ) die('Address Id not given');
	
	tep_db_connect() or die('Unable to connect to database');

	$address_id = tep_db_prepare_input($POST['address_id']);

	$query = 'select ab.customers_id as id from ' . TABLE_ADDRESS_BOOK . ' as ab, ' . TABLE_CUSTOMERS . ' as c where ab.customers_id = c.customers_id'
					.' and ab.address_book_id = c.customers_default_address_id and ab.address_book_id = ' . $address_id;

	$db_query = tep_db_query($query);
	if ( tep_db_num_rows($db_query) == 1 ) {
		$customer = tep_db_fetch_array($db_query);
		$customers_id = $customer['id'];

		$query = 'update ' . TABLE_CUSTOMERS . ' set customers_default_address_id = NULL where customers_id = ' . $customers_id;
		tep_db_query($query);
	}

	$query = 'delete from ' . TABLE_ADDRESS_BOOK . ' where address_book_id = ' . $address_id;

	tep_db_query($query);

	tep_db_close();
?>
