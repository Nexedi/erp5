<?php
  /**
   * Retrieves all the addresses for a person
   */
	include_once('database.php');
	include_once('functions.php');
	include_once('../includes/configure.php');
	include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');

	tep_db_connect() or die('Unable to connect to database');

	$query = 'select ab.address_book_id as id, ab.entry_street_address as street, ab.entry_postcode as zip, ab.entry_city as city, c.countries_name as country from ' . TABLE_ADDRESS_BOOK . ' as ab, ' . TABLE_COUNTRIES . ' as c where c.countries_id = ab.entry_country_id and ab.address_book_id = ' . $_POST['person_id'];

	header('Content-type: text/xml');
	echo executeSQL($query);

	tep_db_close();
?>
