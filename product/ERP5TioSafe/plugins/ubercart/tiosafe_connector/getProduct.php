<?php
include('database.php');
header('Content-Type: text/plain; charset=utf-8');
$sql = "SELECT ucp.nid AS id,ucp.model as reference, ucp.sell_price AS sale_price, ucp.cost AS purchase_price, ";
$sql .= "n.title as title, n.status as state ";
$sql .= "FROM uc_products ucp " ;
$sql .= "LEFT OUTER JOIN node n ON n.nid = ucp.nid ";
if (isset($_POST['id'])) {
    $sql .= " WHERE ucp.nid='".$_POST['id']."' ";
}
if (isset($_POST['product_id'])) {
    $sql .= " WHERE ucp.nid='".$_POST['product_id']."' ";
}
$sql .= "ORDER BY title ASC";
echo executeSQL($sql);
?>