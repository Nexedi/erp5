<?php
  include('tiosafe_config.php');

  $customer_id = "";
  if(postNotEmpty ('person_id')) {
    $customer_id = $_POST['person_id'];

    //Prepare update list
    $update_list = array ('firstname', 'lastname', 'email');
    $db_list = array ('customers_firstname', 'customers_lastname', 'customers_email_address');
    $set_update = create_update_list($update_list, $db_list);

    if ( postNotEmpty('birthday') ) {
      //$dob = tep_date_raw($_POST['birthday']);
      $dob = $_POST['birthday'];

      if ( empty($set_update) ) $set_update .= 'customers_dob = "' . $dob . '"';
      else $set_update .= ', customers_dob = "' . $dob . '"';	
    }

    if ( !empty($set_update) ) {
      $query = "UPDATE " . TABLE_CUSTOMERS . " SET $set_update WHERE customers_id = " . (int)$customer_id;
      echo executeSQL($query, $db);
    }
  }
  else 
    echo '\nInvalid query: The parameter person_id is required!';

  $db->close();
?>
