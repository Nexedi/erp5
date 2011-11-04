<?php
	include_once('functions.php');
	include_once('../includes/configure.php');
	include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');
	include_once('../includes/functions/general.php');
	include_once('../includes/languages/english.php');

	if ( !postNotEmpty('person_id') ) die('Person Id not given');

	tep_db_connect() or die('Unable to connect to database');

	$person_id = $_POST['person_id'];

	$update_list = array ('firstname', 'lastname', 'email');
	$db_list = array ('customers_firstname', 'customers_lastname', 'customers_email_address');

	$set_update = create_update_list($update_list, $db_list);

	$birthday = str_replace('/', '', $_POST['birthday']);

	if ( !empty($birthday) ) {
		$set_update .= (empty($set_update) ? '':',');
	 	$set_update .= 'customers_dob = "' . $birthday . '"';	
	}

	if ( !empty($set_update) ) {
		$query = "update " . TABLE_CUSTOMERS . " set $set_update where customers_id = " . $person_id;
		
		error_log('query : ' . $query, 3, 'log');
		tep_db_query($query);
	}

	tep_db_close();
?>
