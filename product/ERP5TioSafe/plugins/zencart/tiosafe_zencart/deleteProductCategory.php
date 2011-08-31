<?php
  include('tiosafe_config.php');

  $language_id = getDefaultLanguageID($db);


  if(postNotEmpty('product_id') && postNotEmpty('base_category') && postNotEmpty('variation')) {

      $products_id = $_POST['product_id'];
      $product_base_category = $_POST['base_category'];
      $product_variation = $_POST['variation'];
      $products_options_id=$products_options_values_id="";

      //Get the option ID
      $query1 = 'SELECT po.products_options_id, 
              po.products_options_name 
              FROM ' . TABLE_PRODUCTS_OPTIONS . ' AS po 
              WHERE  po.language_id = "' . $language_id . '" 
                AND po.products_options_name = "' . $product_base_category . '"'; 
    
      $result1 = $db->Execute($query1);
      if (!$result1->EOF) {
        $products_options_id=$result1->fields['products_options_id'];
      }
      //Get the option value id
      $query2 = 'SELECT pov.products_options_values_id, 
                        pov.products_options_values_name 
                FROM ' . TABLE_PRODUCTS_OPTIONS_VALUES . ' AS pov 
                WHERE pov.language_id = ' . $language_id . ' 
                  AND pov.products_options_values_name = "' . zen_sanitize_string($product_variation) . '"'; 
      //echo $query2;
      $result2 = $db->Execute($query2);
      if (!$result2->EOF) {
      $products_options_values_id=$result2->fields['products_options_values_id'];
      }

      //delete the attribute 
      if($products_options_id != "" and $products_options_values_id !="") {
        $query = 'DELETE FROM '  . TABLE_PRODUCTS_ATTRIBUTES . ' 
                  WHERE products_id = ' . $products_id .'
                  AND options_id = ' . $products_options_id .'
                  AND options_values_id = ' . $products_options_values_id;
        //echo $query;
       $result = $db->Execute($query);
      }
      
  }
  else 
    echo '\nInvalid query: The parameter product_id is required!';

  $db->close();

?>
