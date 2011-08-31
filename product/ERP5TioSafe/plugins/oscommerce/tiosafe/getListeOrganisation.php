<?php
  /**
   * Retrieves all the organisations
   */
	include_once('database.php');
	include_once('functions.php');
	include_once('../includes/configure.php');
	include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');

  if (postOK('organisation_id') && !verifyExistence(TABLE_ADDRESS_BOOK, 'address_book_id', $_POST['organisation_id'])) {
    header('Content-type: text/xml');
    echo '<xml></xml>';
    die();
  }

  $query = 'select ab.address_book_id as id, ab.entry_country_id as country_id, ab.entry_company as title, c.customers_email_address as email, c.customers_telephone as phone, c.customers_fax as fax, ctr.countries_name as country ' .
           'from ' . TABLE_ADDRESS_BOOK . ' as ab, ' . TABLE_CUSTOMERS . ' as c, ' . TABLE_COUNTRIES . ' as ctr ' .
           'where ab.customers_id = c.customers_id and ab.entry_company != "" and ctr.countries_id = ab.entry_country_id';

  if ( postOK('organisation_id') ) $query .= ' and ab.address_book_id = ' . $_POST['organisation_id'];

  include_once('object_query.php');

  $query = new Object_query($query);

  if ($query->isRequestOk()) {
    $xml = '<xml>';

    $organisations = array();

    foreach ($query->getCollection() as $organisation) {
      if (!isKnownOrganisation($organisations, $organisation['title'])){
        $organisations[$organisation['title']] = array();
      } else {
        if (isKnownCountryForOrg($organisations, $organisation['title'], $organisation['country_id'])) {
          continue;
        }
      }
      $organisations[$organisation['title']][] = $organisation['country_id'];
      $xml .= '<object>';
      foreach ($organisation as $key => $value) {
        $xml .= "<$key>$value</$key>";
      }
      $xml .= '</object>';
    }

    $xml .= '</xml>';
    header('Content-type: text/xml');
    echo $xml;
  }
?>
