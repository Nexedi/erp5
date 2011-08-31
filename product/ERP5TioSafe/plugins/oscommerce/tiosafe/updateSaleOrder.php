<?php

/**
 * No WSR for updating sales order
 *
 *
	include_once('functions.php');
  include_once('../includes/configure.php');
  include_once('../includes/functions/database.php');
  include_once('../includes/database_tables.php');
  include_once('../includes/functions/general.php');

	if ( !postNotEmpty('id') ) die('Orders Id not given');

  tep_db_connect() or die('Unable to connect to database');

	$post_update_list = array('customers_id', 'start_date', 'stop_date', 'currency');
	$db_update_list = array('customers_id', 'date_purchased', 'orders_date_finished', 'currency');

	$set_update_list = create_update_list($post_update_list, $db_update_list);

	if ( !empty($set_update_list) ) {
		$orders_id = $_POST['id'];
		$query = "update " . TABLE_ORDERS . " set $set_update_list where orders_id = " . $orders_id;
		tep_db_query($query);

		// Updating the currency value
		if ( postNotEmpty('currency') ) {
			$currency_value = getCurrencyValue($_POST['currency']);
			$query = 'update ' . TABLE_ORDERS . ' set currency_value = "' . $currency_value . '"';
			tep_db_query($query);
		}
	}

	tep_db_close();

*/
?>
