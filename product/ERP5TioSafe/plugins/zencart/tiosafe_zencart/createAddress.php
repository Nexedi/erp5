<?php
    include('tiosafe_config.php');

    if(postNotEmpty ('person_id')) {
      $customers_id = $_POST['person_id'];
      $countries_name = $_POST['country'];
      $street = $_POST['street'];
      $zip = $_POST['zip'];
      $city = $_POST['city'];
      $countries_id = getCountryId ($_POST['country'], $db);
        
      //Insert the new address
      $sql_array = array('customers_id' => zen_db_prepare_input($customers_id),
                        'entry_street_address' => zen_db_prepare_input($street),
                        'entry_postcode' => zen_db_prepare_input($zip),
                        'entry_city' => zen_db_prepare_input($city),
                        'entry_country_id' => $countries_id,
                      );
      zen_db_perform(TABLE_ADDRESS_BOOK, $sql_array);
      
      //XXX Create a function using an sql query, 
      // we are not sure mysql_insert_id return the right customer id
      $address_book_id = zen_db_insert_id();

      // Check if the customer has a default_address
      // If not, set this one as default
      $query = $db->Execute("SELECT customers_default_address_id
                              FROM " . TABLE_CUSTOMERS . "
                              WHERE customers_id = '" . $customers_id . "'");
      if ($query->RecordCount() > 0) {
        if ( empty($query->fields['customers_default_address_id'])) {
          $query = 'UPDATE ' . TABLE_CUSTOMERS . ' SET customers_default_address_id = ' . $address_book_id . ' where customers_id = ' . $customers_id;
          executeSQL($query, $db);
        }
      }
    } 
    else 
      echo '\nInvalid query: person_id parameter is required!';
      
  $db->close();
?>
