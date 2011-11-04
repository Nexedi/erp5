<?php
    include('tiosafe_config.php');

    //tep_db_connect() or die('Unable to connect to database');
    $birthday=$first_name=$last_name=$user_email="";
    if(isset($_POST['birthday']))  $birthday = $_POST['birthday'];
    if(isset($_POST['firstname'])) $first_name = $_POST['firstname'];
    if(isset($_POST['lastname']))  $last_name = $_POST['lastname'];
    if(isset($_POST['email']))     $user_email = $_POST['email'];
  
    if ($first_name!="" && $last_name!="" && $user_email!="") {
      $sql_array = array( 'customers_firstname' => zen_db_prepare_input($first_name),
                          'customers_lastname' => zen_db_prepare_input($last_name),
                          'customers_email_address' => zen_db_prepare_input($user_email),
                          'customers_dob' => zen_db_prepare_input($birthday)
                        );
      zen_db_perform(TABLE_CUSTOMERS, $sql_array);
    }
    else
     echo '\nInvalid query: firstname, lastname, email are required!';
 
  $db->close();
?>
