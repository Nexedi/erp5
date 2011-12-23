<?php
	include_once('functions.php');
	include_once('../includes/configure.php');
	include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');
	include_once('../includes/functions/general.php');

	if ( !postNotEmpty('person_id') ) die('Person Id not given');

	tep_db_connect() or die('Unable to connect to database');
	
	$sql_array = array(
										 'customers_id' => $_POST['person_id'],
										 'entry_street_address' => tep_db_prepare_input($_POST['street']),
										 'entry_postcode' => tep_db_prepare_input($_POST['zip']),
										 'entry_city' => tep_db_prepare_input($_POST['city']),
										 'entry_country_id' => getCountryIdByName($_POST['country']),
										);

	tep_db_perform(TABLE_ADDRESS_BOOK, $sql_array);
	$address_book_id = tep_db_insert_id();

	// Setting this address as the customer's default one, in case he doesn't have an address yet
	if ( !getCustomersDefaultAddressId($_POST['person_id']) ) {
		$query = 'update ' . TABLE_CUSTOMERS . ' set customers_default_address_id = ' . $address_book_id
								 . ' where customers_id = ' . $_POST['person_id'];
		tep_db_query($query);
	}

	tep_db_close();
?>
