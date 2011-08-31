<?php
include('database.php');

if (isset($_POST['id'])) {
    $id = $_POST['id'];
    $sale_order_sql = "UPDATE uc_orders SET ";
}
if (isset($_POST['sale_order_id'])) {
    $id = $_POST['sale_order_id'];
    $sale_order_sql = "UPDATE uc_orders SET ";
}
if (isset($_POST['payment_method'])) {
    $payment_method = $_POST['payment_method'];
    $sale_order_sql .= sprintf("  payment_method = %s, ", $payment_method);
}
if (isset($id)){
  $sale_order_sql .= " order_id = order_id WHERE order_id=$id";
  mysql_query($sale_order_sql) or die(mysql_error());
}
?>