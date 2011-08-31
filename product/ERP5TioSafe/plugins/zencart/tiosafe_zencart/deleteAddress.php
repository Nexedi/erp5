<?php
    include('tiosafe_config.php');

    if( postNotEmpty('address_id') ) {
      $address_id = zen_db_prepare_input($_POST['address_id']);
      $query = 'DELETE FROM ' . TABLE_ADDRESS_BOOK . ' WHERE address_book_id = ' . $address_id;
      echo executeSQL($query, $db);
    }
    else 
      echo '\nInvalid query: the parameter address_id is required!';

  $db->close();
?>
