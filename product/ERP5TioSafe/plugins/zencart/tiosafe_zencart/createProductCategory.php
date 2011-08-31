<?php
  include('tiosafe_config.php');

  if(isset($_POST['product_id'])) $products_id = $_POST['product_id'];
  if(isset($_POST['base_category']))   $product_base_category = $_POST['base_category'];
  if(isset($_POST['variation']))   $product_variation = $_POST['variation'];
  if(isset($_POST['price']))   $product_price = $_POST['price'];

   
  $language_id = getDefaultLanguageID($db);



  if(postNotEmpty ('product_id') && postNotEmpty ('base_category') && postNotEmpty ('variation')) {

    $products_id = $_POST['product_id'];
    $product_base_category = $_POST['base_category'];
    $product_variation = $_POST['variation'];
    $product_price = $_POST['price'];
    $products_date_added = date('Y/m/d h:i:s');

    $new_option = $new_option_value = false;
 
    /* Check if option exists */
    $query1 = 'SELECT po.products_options_id, 
              po.products_options_name 
              FROM ' . TABLE_PRODUCTS_OPTIONS . ' AS po 
              WHERE  po.language_id = "' . $language_id . '" 
                AND po.products_options_name = "' . $product_base_category . '"'; 
    
    $result1 = $db->Execute($query1);
    if (!$result1->EOF) {
     $products_options_id=$result1->fields['products_options_id'];
    } else // Create the options
    { $new_option = true;
      //Get the next id as done in zencart
      $max_options_id_values = $db->Execute("select max(products_options_id) + 1 as next_id
                                             from " . TABLE_PRODUCTS_OPTIONS);
      $products_options_id = $max_options_id_values->fields['next_id'];

      $sql_array = array('products_options_id' => $products_options_id,
                         'language_id' => $language_id,
                         'products_options_name' => zen_sanitize_string($product_base_category)
                );
      zen_db_perform(TABLE_PRODUCTS_OPTIONS, $sql_array);
    }


    //Check if value exists
    $query2 = 'SELECT pov.products_options_values_id, 
                      pov.products_options_values_name 
              FROM ' . TABLE_PRODUCTS_OPTIONS_VALUES . ' AS pov 
              WHERE pov.language_id = ' . $language_id . ' 
                AND pov.products_options_values_name = "' . zen_sanitize_string($product_variation) . '"'; 
    //echo $query2;
    $result2 = $db->Execute($query2);
    if (!$result2->EOF) {
     $products_options_values_id=$result2->fields['products_options_values_id'];
    } else // Create the value
    { $new_option_value = true;
      //Get the next id as done in zencart
      $max_values_id_values = $db->Execute("select max(products_options_values_id) + 1
                                           as next_id from " . TABLE_PRODUCTS_OPTIONS_VALUES);
      $products_options_values_id = $max_values_id_values->fields['next_id'];

      $sql_array = array('products_options_values_id' => $products_options_values_id,
                         'language_id' => $language_id,
                         'products_options_values_name' => zen_sanitize_string($product_variation)
                );
      zen_db_perform(TABLE_PRODUCTS_OPTIONS_VALUES, $sql_array);
    }


    //Check if the option is used buy the product
    $query3 = 'SELECT pa.products_attributes_id AS id, 
              po.products_options_name,  
              pov.products_options_values_name 
              FROM ' . TABLE_PRODUCTS_ATTRIBUTES . ' AS pa
              LEFT JOIN ' . TABLE_PRODUCTS_OPTIONS . ' AS po 
                ON  pa.options_id = po.products_options_id 
              LEFT JOIN ' . TABLE_PRODUCTS_OPTIONS_VALUES . ' AS pov 
                ON pa.options_values_id = pov.products_options_values_id
              WHERE pa.products_id = "' . $products_id . '"
                AND pa.options_id = "' . $products_options_id . '" 
                AND pa.options_values_id = "' . $products_options_values_id . '" 
                AND po.language_id = "' . $language_id . '" 
                AND pov.language_id = ' . $language_id; 
    $result3 = $db->Execute($query3);
    if (!$result3->EOF) {
     $products_attributes_id=$result3->fields['id'];
    } else // Create the attribute
    {
      $sql_array = array('products_id' => $products_id,
                         'options_id' => $products_options_id,
                         'options_values_id' => $products_options_values_id
                         );
      zen_db_perform(TABLE_PRODUCTS_ATTRIBUTES, $sql_array);

      if($new_option or $new_option_value) {
        $sql_array2 = array('products_options_id' => $products_options_id,
                          'products_options_values_id' => $products_options_values_id
                         );
        zen_db_perform(TABLE_PRODUCTS_OPTIONS_VALUES_TO_PRODUCTS_OPTIONS, $sql_array2);
      }
    }

  }
  else 
    echo '\nInvalid query: The parameters, product_id, base_category and variation are required!';

  $db->close();

?>
