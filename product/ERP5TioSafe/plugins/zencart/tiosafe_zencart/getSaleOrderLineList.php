<?php
 include('tiosafe_config.php');


  if(postNotEmpty('sale_order_id')) {

    
    
    $orders_id = $_POST['sale_order_id'];
    //$orders_id = 5;
    $req_select  = "SELECT orders_products_id AS id, ";
    $req_select .= "products_id AS id_product, "; 
    $req_select .= "orders_id AS id_group, "; 
    $req_select .= "products_name AS title, ";
    $req_select .= "products_id AS reference, ";
    //$req_select .= "order_item_sku AS resource, ";
    $req_select .= "IF (products_tax>0 , (products_tax*100/final_price), '0.00') AS vat, ";
    $req_select .= "IF (products_tax>0, products_tax, '0.00') AS vat_price, ";
  
    $req_select .= "products_quantity AS quantity, ";
    $req_select .= "products_price AS net_price, ";
    $req_select .= "final_price AS gross_price ";
    $req_select .= "FROM  ". TABLE_ORDERS_PRODUCTS ."  op ";
    //$req_select .= "LEFT OUTER JOIN ". TABLE_ORDERS ." ord ON op.orders_id=ord.orders_id ";
    //$req_select .= "LEFT OUTER JOIN ". TABLE_ORDERS ." ord ON op.orders_id=ord.orders_id ";
    //$req_select .= "LEFT OUTER JOIN ". TABLE_PRODUCTS ." prod ON op.products_id=prod.products_id ";
    //$req_select .= "LEFT OUTER JOIN ". TABLE_TAX_RATES ." tax ON prod.products_tax_class_id=tax.product_id ";
    $req_select .= "WHERE orders_id='".$orders_id."' ";
    $req_select .= "ORDER BY orders_products_id ASC";

    /*$req_select  = "SELECT item.order_item_id AS id, ";*/
    header('Content-type: text/xml');
    echo executeSQL($req_select, $db);
 }
  else 
    echo '\nInvalid query: Parameter sale_order_id is regired!';
  
  $db->close();

?>
