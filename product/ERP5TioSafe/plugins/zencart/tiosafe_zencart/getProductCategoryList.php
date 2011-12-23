<?php
  include('tiosafe_config.php');

  //
  if (postOK('product_id')) {
   
  

    $products_id = $_POST['product_id'];
    //$products_id = 179;
    $language_id = getDefaultLanguageID($db);

    $xml = '<xml>';
    /*
    // Add a category line for Product type
    $product_type_query = $db->Execute("SELECT master_categories_id
                              FROM " . TABLE_PRODUCTS . " prd
                              LEFT JOIN " . TABLE_CATEGORIES_DESCRIPTION . " cat
                              ON prd.master_categories_id = cat.categories_id
                              WHERE prd.products_id = '" . $products_id . "'
                                    AND cat.language_id = '" . $language_id . "' ");
    if ($product_type_query->RecordCount() > 0) {
      $categ_id = $product_type_query->fields['master_categories_id'];
      $category_path = getCategoryERP5LikePath($categ_id,$parent_id=0)."/".zen_get_category_name($categ_id,$language_id);
      $xml .= '<object>';
        $xml .= '<id>' . $product_type_query->fields['master_categories_id'] . '</id>';
        $xml .= '<category>'. COLLECTION_CIM_ID .''. $category_path . '</category>';
      $xml .= '</object>';
    }
    */

    $query1 = 'SELECT pa.products_attributes_id AS id, 
              po.products_options_name,  
              pov.products_options_values_name 
              FROM ' . TABLE_PRODUCTS_ATTRIBUTES . ' AS pa
              LEFT JOIN ' . TABLE_PRODUCTS_OPTIONS . ' AS po 
                ON  pa.options_id = po.products_options_id 
              LEFT JOIN ' . TABLE_PRODUCTS_OPTIONS_VALUES . ' AS pov 
                ON pa.options_values_id = pov.products_options_values_id
              WHERE pa.products_id = "' . $products_id . '" 
                AND po.language_id = "' . $language_id . '" 
                AND pov.language_id = "' . $language_id . '"';	
    //echo $query1;
    $result1 = $db->Execute($query1);

    while (!$result1->EOF) {
      $xml .= '<object>';
        $xml .= '<id>' . $result1->fields['id'] . '</id>';
        $xml .= '<category>' . $result1->fields['products_options_name'] . '/' . $result1->fields['products_options_values_name'] . '</category>';
      $xml .= '</object>';
      $result1->MoveNext();
    }

    $xml .= '</xml>';

    header('Content-type: text/xml');
    echo $xml;
  } 
  else 
    echo '\nInvalid query: Parameter product_id is required!';
  

  $db->close();

?> 
