<?php
  /**
   * Creates a person and returns the id of the created person in the database
   */
	include_once('../includes/configure.php');
  include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');
	include_once('../includes/functions/general.php');

	tep_db_connect() or die('Unable to connect to database');
	
	$birthday = str_replace('/', '', $_POST['birthday']);

	$sql_array = array('customers_firstname' => tep_db_prepare_input($_POST['firstname']),
										 'customers_lastname' => tep_db_prepare_input($_POST['lastname']),
										 'customers_email_address' => tep_db_prepare_input($_POST['email']),
										 'customers_dob' => $birthday,
										 'customers_telephone' => tep_db_prepare_input($_POST['phone']),
										 'customers_fax' => tep_db_prepare_input($_POST['fax'])
										);

	tep_db_perform(TABLE_CUSTOMERS, $sql_array);

	header('Content-type: text/xml');
	echo '<xml><object><id>' . tep_db_insert_id() . '</id></object></xml>';

	tep_db_close();
?>
