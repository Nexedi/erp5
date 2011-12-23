<?php
include('database.php');

$email = "";
$payment_method = "";
$order_status = "pending";

if (isset($_POST['id'])) {
    $id = $_POST['id'];
}
if (isset($_POST['email'])) {
    $email = $_POST['email'];
}
if (isset($_POST['payment_method'])) {
    $payment_method = $_POST['payment_method'];
}
if (isset($_POST['order_status'])) {
    $order_status = $_POST['order_status'];
}

if (isset($id)){
  $req_exist = mysql_query("SELECT * from uc_orders where order_id=$id") or die(mysql_error());
  $rows = mysql_num_rows($req_exist);
  if ($rows == 0){
    $sale_order_sql = sprintf("INSERT INTO uc_orders (order_id, order_status, primary_email, payment_method, created, modified) VALUES (%d, %s, %s, %s,%d,%d)", 
	    GetSQLValueString($id,"int"), 
	    GetSQLValueString($order_status,"text"), 
	    GetSQLValueString($primary_email,"text"), 
	    GetSQLValueString($payment_method,"text"),
	    GetSQLValueString(time(),"int"),
	    GetSQLValueString(time(),"int")); 
    mysql_query($sale_order_sql) or die(mysql_error());
  }
}

?>