<?php
include('database.php');
header('Content-Type: text/plain; charset=utf-8');

if (isset($_POST['sale_order_id'])) {
    $order_id = $_POST['sale_order_id'];
}
if (isset($_POST['id'])) {
    $order_id = $_POST['id'];
}

$currency = getDefaultSiteCurency(); 
$sql = " SELECT op.nid AS id_product, op.order_product_id AS id, op.title AS title, op.qty AS quantity, ";
$sql .= " $currency as currency, op.price AS price, ucp.model as reference, price as net_price ";
if (isset($_POST['sale_order_id']) or isset($_POST['id'])){
  $vat = getVatTaxRate($order_id);
  $sql .= ",$vat*100 as vat,$vat*op.price*op.qty as vit_price ";
}
$sql .= "FROM uc_order_products op " ;
$sql .= "LEFT OUTER JOIN node n ON n.nid = op.nid ";
$sql .= "LEFT OUTER JOIN uc_products ucp ON op.nid = ucp.nid ";
$sql .= "WHERE 1=1 ";
if (isset($_POST['sale_order_id'])) {
    $sql .= " AND order_id=".$_POST['sale_order_id']." ";
}
if (isset($_POST['id'])) {
    $sql .= " AND order_id=".$_POST['id']." ";
}
$sql .= "ORDER BY reference ASC ";
echo executeSQL($sql);
?>
