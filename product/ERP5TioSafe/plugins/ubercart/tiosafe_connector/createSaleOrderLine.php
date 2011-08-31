<?php
include('database.php');

$quantity = 0;

if (isset($_POST['order_id'])) {
    $order_id = $_POST['order_id'];
}
if (isset($_POST['product_id'])) {
    $product_id = $_POST['product_id'];
}
if (isset($_POST['quantity'])) {
    $quantity = $_POST['quantity'];
}

if (isset($order_id) && isset($product_id)){

  $req_node = mysql_query("SELECT * from node where nid='$product_id'") or die(mysql_error());
  $res_node = mysql_fetch_array($req_node);

  $req_product = mysql_query("SELECT * from uc_products where nid='$product_id'") or die(mysql_error());
  $res_product = mysql_fetch_array($req_product);

  
  $sale_order_line_sql = sprintf("INSERT INTO uc_order_product (order_id, nid, title, manufacturer, model, qty, cost, price) VALUES (%d, %d, %s, %s, %s,%d,%f,%f)", 
	  GetSQLValueString(,"int"), 
	  GetSQLValueString(,"int"), 
	  GetSQLValueString(,"int"), 
	  GetSQLValueString(,"int"), 
	  GetSQLValueString(,"int")); 
  mysql_query($sale_order_line_sql) or die(mysql_error());

}

?>