<?php
  /**
   * Retrieves all the persons in the customers table
   */
	include_once('functions.php');
	include_once('database.php');
  include_once('../includes/configure.php');
  include_once('../includes/database_tables.php');
  include_once('../includes/functions/database.php');

 /* if ( postOK('person_id') ) {
    if ( !(int) $_POST['person_id'] ) {
      header('Content-type: text/xml');
      echo '<xml></xml>';
      die();
    }
  }

  if ( postOK('person_id') && !verifyExistence(TABLE_CUSTOMERS, 'customers_id', $_POST['person_id'])) {
    header('Content-type: text/xml');
    echo '<xml></xml>';
    die();
  }
*/
  tep_db_connect() or die('Unable to connect to database');

  $query = 'select c.customers_id as id, c.customers_firstname as firstname, c.customers_lastname as lastname, c.customers_email_address as email, c.customers_dob as birthday, c.customers_telephone as telephone, c.customers_fax as fax, concat_ws(" ", "", ab.entry_company, ctr.countries_name) as relation ' . 
           'from ' . TABLE_CUSTOMERS . ' as c , ' . TABLE_ADDRESS_BOOK . ' as ab,  ' . TABLE_COUNTRIES . ' as ctr ' .
           'where c.customers_default_address_id = ab.address_book_id and ab.entry_country_id = ctr.countries_id' ;

	if (postOK('person_id')) $query .= ' and c.customers_id = ' . $_POST['person_id'];

  include_once('object_query.php');

  $query = new Object_query($query);

  if ($query->isRequestOk()) {
    $xml = '<xml>';
    
    foreach ($query->getCollection() as $person) {
      $xml .= '<object>';
      foreach ($person as $key => $value) {
        if ($key == 'relation') {
          if ($value != '' and isValidRelation($person['id'])) {
						$xml .= "<nb_rel>" . count(explode(" ", $value)) . "</nb_rel>";
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

	tep_db_close();
?> 
