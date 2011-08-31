<?php
  include("includes/config.inc.php");
  include("includes/function.php");

  ///Get the query string and complete the SQL query
  $order_id = "";
  if(isset($_POST['sale_order_id']))
    $order_id = $_POST['sale_order_id'];
 
  
  if($order_id != "") {
  
    // Generate the query
    $req_select  = "SELECT item.order_item_id AS id, ";
    $req_select .= "item.product_id AS id_product, "; 
    $req_select .= "item.product_id AS id_group, "; 
    $req_select .= "product_name AS title, ";
    $req_select .= "order_item_sku AS reference, ";
    $req_select .= "(tax_rate*100) AS vat, ";
    $req_select .= "(product_item_price*tax_rate) AS vat_price, ";
    
    //$req_select .= "order_item_sku AS resource, ";
    $req_select .= "product_quantity AS quantity, ";
    $req_select .= "product_item_price AS net_price, ";
    $req_select .= "product_final_price AS gross_price, ";

    $req_select .= "order_item_currency AS currency ";
    $req_select .= "FROM  ".constant('_VM_TABLE_PREFIX_')."_order_item item ";
    $req_select .= "LEFT OUTER JOIN ".constant('_VM_TABLE_PREFIX_')."_product prod ON item.product_id=prod.product_id ";
    $req_select .= "LEFT OUTER JOIN ".constant('_VM_TABLE_PREFIX_')."_tax_rate tax ON prod.product_tax_id=tax.tax_rate_id  ";
    $req_select .= "WHERE item.order_id=".$order_id." ";
    $req_select .= " ORDER BY order_item_name ASC, order_item_sku ASC";

    header('Content-type: text/xml');
    echo executeSQL($req_select);
 }
  else 
    echo '\nInvalid query: No parameter given!';

  mysql_close();
 ?>