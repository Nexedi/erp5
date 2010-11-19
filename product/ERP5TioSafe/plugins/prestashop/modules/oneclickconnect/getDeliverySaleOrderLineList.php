<?php
$path = explode('/modules',dirname(__FILE__));
$config = $path[0].'/config/settings.inc.php';
include($config);
include('database.php');


header('Content-Type: text/plain; charset=utf-8');

$sql = "SELECT ";
$sql .= constant('_DB_PREFIX_')."orders.id_order AS id, ";
$sql .= "'Service Delivery' AS id_product, ";
$sql .= "0 AS id_group, ";
$sql .= "' Service Delivery' AS resource, ";
$sql .= "'Delivery' AS title, ";
$sql .= "'Delivery' AS reference, ";
$sql .= "FORMAT(1, 2) AS quantity, ";
# build value without taxes
$sql .= "ROUND(";
$sql .= "(".constant('_DB_PREFIX_')."orders.total_shipping / (1 + ";
$sql .= "(IFNULL(".constant('_DB_PREFIX_')."tax.rate, 19.60) / 100)";
$sql .= "))";
$sql .= ", 6) AS price, ";
$sql .= "ROUND((IFNULL(".constant('_DB_PREFIX_')."tax.rate, 19.60)), 2) AS VAT ";

$sql .= "FROM ".constant('_DB_PREFIX_')."orders ";

$sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."carrier ";
$sql .= "ON ".constant('_DB_PREFIX_')."carrier.id_carrier=".constant('_DB_PREFIX_')."orders.id_carrier ";

$sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."tax ";
$sql .= "ON ".constant('_DB_PREFIX_')."tax.id_tax=".constant('_DB_PREFIX_')."carrier.id_tax ";

$sql .= "WHERE ";
$sql .= constant('_DB_PREFIX_')."orders.total_shipping != 0.0 ";

if (isset($_POST['sale_order_id'])){
    $sql .= "AND ".constant('_DB_PREFIX_')."orders.id_order=".$_POST['sale_order_id'];
}


echo executeSQL($sql);
?>
