<?php
include('database.php');

if (isset($_POST['product_id'])) {
    $id = $_POST['product_id'];
    $product_sql = "UPDATE uc_products SET ";
    $node_sql = "UPDATE node SET ";
    $noderev_sql .= "UPDATE node_revisions SET ";
}
if (isset($_POST['reference'])) {
    $reference = $_POST['reference'];
    $product_sql .= sprintf(" model = '%s', ", $reference);
}
if (isset($_POST['purchase_price'])) {
    $purchase_price = $_POST['purchase_price'];
    $product_sql .= sprintf(" cost = '%f', ", $purchase_price);
}
if (isset($_POST['sale_price'])) {
    $sale_price = $_POST['sale_price'];
    $product_sql .= sprintf(" sell_price = '%f', ", $sale_price);
}
if (isset($_POST['title'])) {
    $title = $_POST['title'];
    $node_sql .= sprintf(" title = '%s', ",$title);
    $noderev_sql .= sprintf(" title = '%s', ",$title);
}

if ((isset($_POST['reference'])) OR (isset($_POST['purchase_price'])) OR (isset($_POST['sale_price'])) OR (isset($_POST['title']))){
  $product_sql .= " nid=nid WHERE nid='$id' ";
  $node_sql .= " nid=nid WHERE nid='$id' ";
  $noderev_sql .= " nid=nid WHERE nid='$id' ";
  echo "$product_sql \n $node_sql \n $noderev_sql \n";
  mysql_query($product_sql) or die(mysql_error());
  mysql_query($node_sql) or die(mysql_error());
  mysql_query($noderev_sql) or die(mysql_error());
}
?>
