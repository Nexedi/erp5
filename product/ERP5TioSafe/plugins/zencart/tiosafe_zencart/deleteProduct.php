<?php
  include('tiosafe_config.php');

  if(postNotEmpty('product_id')) {

      $products_id = $_POST['product_id'];
      //$products_id = 181;
      /*
      $query = 'DELETE FROM '  . TABLE_PRODUCTS . ' WHERE products_id = ' . $products_id;
      zen_db_query($query);
      
      $query = 'DELETE FROM ' . TABLE_PRODUCTS_DESCRIPTION . ' WHERE products_id = ' . $products_id;
      zen_db_query($query); */
      zen_remove_product($products_id);
  }
  else 
    echo '\nInvalid query: The parameter product_id is required!';

  $db->close();

?>
