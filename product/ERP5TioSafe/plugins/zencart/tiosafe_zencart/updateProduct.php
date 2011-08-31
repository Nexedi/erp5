<?php
  include('tiosafe_config.php');

  //Product id is required
  if (postNotEmpty ('product_id')) {
    $products_id = $_POST['product_id'];
    $language_id = getDefaultLanguageID($db);
    $products_last_modified = date('Y/m/d h:i:s');

    $update_array_1 = array('sale_price');
    $db_array_1 = array('products_price');
    $set_update_1 = create_update_list($update_array_1, $db_array_1);
    if ( !empty($set_update_1) ) {
      $query_1 = "UPDATE " . TABLE_PRODUCTS . " SET $set_update_1, products_last_modified='".$products_last_modified."' WHERE products_id = " . $products_id;
      executeSQL($query_1, $db);
    }

   
    $update_array_2 = array('title');
    $db_array_2 = array('products_name');
    $set_update_2 = create_update_list($update_array_2, $db_array_2);
    if ( !empty($set_update_2) ) {
      $query_2 = "UPDATE " . TABLE_PRODUCTS_DESCRIPTION . " SET $set_update_2 WHERE products_id = " . $products_id . " and language_id = " . $language_id;
      echo executeSQL($query_2, $db);
    }
  }
  else 
    echo '\nInvalid query: The parameter product_id is required!';

?>
