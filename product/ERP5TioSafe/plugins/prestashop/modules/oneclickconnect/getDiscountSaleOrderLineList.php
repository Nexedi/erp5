<?php
$path = explode('/modules',dirname(__FILE__));
$config = $path[0].'/config/settings.inc.php';
include($config);
include('database.php');

header('Content-Type: text/plain; charset=utf-8');

$sql = "SELECT ";
$sql .= constant('_DB_PREFIX_')."order_discount.id_order_discount AS id, ";
$sql .= "'Service Discount' AS id_product, ";
$sql .= "0 AS id_group, ";
$sql .= "' Service Discount' AS resource, ";
$sql .= "'Discount' AS title, ";
$sql .= "'Discount' AS reference, ";
$sql .= "FORMAT(1, 2) AS quantity, ";
$sql .= "-(ROUND(value, 6)) AS price, ";
$sql .= "'0.00' AS VAT ";

$sql .= "FROM ".constant('_DB_PREFIX_')."order_discount ";

if (isset($_POST['sale_order_id'])){
    $sql .= "WHERE ";
    $sql .= "id_order=".$_POST['sale_order_id'];
}

echo executeSQL($sql);
?>
