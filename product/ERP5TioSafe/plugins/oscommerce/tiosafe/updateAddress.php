<?php
	include_once('functions.php');
	include_once('../includes/configure.php');
	include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');
	include_once('../includes/functions/general.php');

	if ( !postNotEmpty('address_id') ) die('Address Id not given');

	tep_db_connect() or die('Unable to connect to database');

	$address_id = $_POST['address_id'];

	$post_update_list = array('street', 'zip', 'city');
	$db_update_list = array('entry_street_address', 'entry_postcode', 'entry_city');

	$set_update = create_update_list($post_update_list, $db_update_list);
	
	if ( postNotEmpty('country') ) {
		// Let's get the countries_id matching the given country name
		$query = 'select countries_id from ' . TABLE_COUNTRIES . ' where countries_name = "' . $_POST['country'] . '"';
		$db_query = tep_db_query($query);
		if ( tep_db_num_rows($db_query) ) {
			$result = tep_db_fetch_array($db_query);
			$countries_id = $result['countries_id'];
			if ( empty($set_update) ) {
				$set_update = 'entry_country_id = ' . $countries_id;
			} else {
				$set_update .= ', entry_country_id = ' . $countries_id;
			}
		}
	}
	if ( !empty($set_update) ) {
		$query = "update " . TABLE_ADDRESS_BOOK . " set $set_update where address_book_id = " .  $address_id;
		tep_db_query($query);
	}

	tep_db_close();
?>
