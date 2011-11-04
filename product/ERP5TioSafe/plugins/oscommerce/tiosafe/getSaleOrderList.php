<?php
  /**
   * Retrieves all the orders in the orders table
   */
	include_once('database.php');
	include_once('functions.php');
  include_once('../includes/configure.php');
  include_once('../includes/database_tables.php');
  include_once('../includes/functions/database.php');

  tep_db_connect() or die('Unable to connect to database');
 
  if (postOK('sale_order_id')  && !verifyExistence(TABLE_ORDERS, 'orders_id', $_POST['sale_order_id'])) {
    header('Content-type: text/xml');
    echo "<xml></xml>";
    die();
  }
  $destination = 'concat(" ", concat_ws(" ", o.delivery_name, o.customers_email_address))';
  $destination_ownership = 'concat(" ", concat_ws(" ", c.customers_firstname, c.customers_lastname, c.customers_email_address))';
  $destination_administration = 'concat(" ", concat_ws(" ", o.billing_name, c.customers_email_address))';
  $destination_decision = 'concat(" ", concat_ws(" ", o.customers_name, c.customers_email_address))';

	// Getting only delivered orders ie orders_status=3
  $query = 'select o.orders_id as id, o.orders_id as reference, o.currency as currency, ' . $destination . ' as destination, ' . $destination_administration . ' as destination_administration, ' . $destination_decision . ' as destination_decision, ' . $destination_ownership . ' as destination_ownership, o.payment_method as payment_mode ' 
         . 'from ' . TABLE_ORDERS . ' as o, ' . TABLE_CUSTOMERS . ' as c  where c.customers_id = o.customers_id and orders_status = 3';


	if ( postOK('sale_order_id') ) $query .= ' and o.orders_id = ' . $_POST['sale_order_id'];
  
  header('Content-type: text/xml');
	echo executeSQL($query);

	tep_db_close();
?> 
