<?php
    include('tiosafe_config.php');

    if( postNotEmpty('address_id') ) {
      $address_id = $_POST['address_id'];
    
      $post_update_list = array('street', 'zip', 'city');
      $db_update_list = array('entry_street_address', 'entry_postcode', 'entry_city');

      $set_update = create_update_list($post_update_list, $db_update_list);

      //If the country is posted, get the id
      if ( postNotEmpty('country') ) {
        $countries_id = getCountryId ($_POST['country'], $db);
        if ( empty($set_update) ) 
          $set_update = 'entry_country_id = ' . $countries_id;
        else 
          $set_update .= ', entry_country_id = ' . $countries_id; 
        }
      
      if ( !empty($set_update) && !empty($address_id)) {
        $query = "UPDATE " . TABLE_ADDRESS_BOOK . " SET $set_update WHERE address_book_id = " .  $address_id;
        echo executeSQL($query, $db);
      }
      
    }
    else 
      echo '\nInvalid query: the parameter address_id is required!';

  $db->close();
?>
