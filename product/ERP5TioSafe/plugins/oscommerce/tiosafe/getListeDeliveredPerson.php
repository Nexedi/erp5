<?php
  /**
   * Retrieves all the persons who are on the addresses and different from the owner of the address
   */
	include_once('database.php');
	include_once('functions.php');
	include_once('../includes/configure.php');
	include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');

  if ( postOK('person_id') ) {
    if (!(int) $_POST['person_id']) {
      header('Content-type: text/xml');
      echo '<xml></xml>';
      die();
    } 
  }

  if ( !verifyExistence(TABLE_ADDRESS_BOOK, 'address_book_id', $_POST['person_id'])) {
    header('Content-type: text/xml');
    echo '<xml></xml>';
    die();
  }

	tep_db_connect() or die('Unable to connect to database');


	$query = 'select ab.address_book_id as id, ab.entry_firstname as firstname, ab.entry_lastname as lastname, c.customers_email_address as email, c.customers_dob as birthday, concat_ws(" ", ab.entry_company, c.customers_email_address) as relation '
					. 'from ' . TABLE_ADDRESS_BOOK . ' as ab, ' . TABLE_CUSTOMERS . ' as c '
					. 'where c.customers_id = ab.customers_id and ((ab.entry_firstname != c.customers_firstname) or (ab.entry_lastname != c.customers_lastname)) '
					. 'and ab.entry_firstname != "" and ab.entry_lastname != ""';

	if ( postOK('person_id') ) $query .= ' and ab.address_book_id = ' . $_POST['person_id'];

  include_once('object_query.php');

  $query = new Object_query($query);

  if ($query->isRequestOk()) {
    $xml = '<xml>';

    foreach ($query->getCollection() as $person) {
      $xml .= '<object>';
      foreach ($person as $key => $value) {
        if ($key == 'relation') {
          if ($value != '') {
            $xml .= "<$key>$value</$key>";
          }
          continue;
        }
        $xml .= "<$key>$value</$key>";
      }
      $xml .= '</object>';
    }  

    $xml .= '</xml>';
    header('Content-type: text/xml');
    echo $xml;
  }
?>
