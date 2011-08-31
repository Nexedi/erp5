<?php
  include('tiosafe_config.php');

  if(postNotEmpty ('title')) {

    $products_name = $_POST['title'];
    $products_sale_price = 0;
    $language_id = getDefaultLanguageID($db);
    $products_date_added = date('Y/m/d h:i:s');

    // Setting the products_status as '1' ie available
    $sql_array = array('products_price' => $products_sale_price,
                        'products_status' => '1',
                        'products_date_added' => $products_date_added
                );
    zen_db_perform(TABLE_PRODUCTS, $sql_array);
    $products_id = zen_db_insert_id();

    

    $sql_array = array( 'products_id' => $products_id,
                        'language_id' => $language_id,
                        'products_name' => zen_sanitize_string($products_name)
                );
    zen_db_perform(TABLE_PRODUCTS_DESCRIPTION, $sql_array);
  }
  else 
    echo '\nInvalid query: The parameter title is required!';

  $db->close();

?>
