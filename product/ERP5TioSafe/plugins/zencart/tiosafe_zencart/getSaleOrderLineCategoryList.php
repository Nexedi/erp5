<?php
  include('tiosafe_config.php');

  if ( postOK('sale_order_line_id') and postOK('sale_order_id')) {
    
    $products_id = $_POST['sale_order_line_id'];
    $orders_id = $_POST['sale_order_id'];
    $query2 = 'SELECT orders_products_attributes_id AS id,
                products_options, 
                products_options_values 
              FROM ' . TABLE_ORDERS_PRODUCTS_ATTRIBUTES . ' 
              WHERE orders_id = ' . $orders_id . ' 
              AND orders_products_id = ' . $products_id;
    $result2 = $db->Execute($query2);

    $xml = '<xml>';

    while (!$result2->EOF) {
      $xml .= '<object>';
      $xml .= '<id>' . $result2->fields['orders_products_attributes_id'] . '</id>';
      $xml .= '<category>' . $result2->fields['products_options'] . '/' . $result2->fields['products_options_values'] . '</category>';
      $xml .= '</object>';
      $result2->MoveNext();
    }
    $xml .= '</xml>';

    header('Content-type: text/xml');
    echo $xml;
  }
  
  $db->close();

?> 
