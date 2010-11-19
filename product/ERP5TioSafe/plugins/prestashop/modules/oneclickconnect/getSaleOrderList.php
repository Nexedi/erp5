<?php
$path = explode('/modules',dirname(__FILE__));
$config = $path[0].'/config/settings.inc.php';
include($config);
include('database.php');


header('Content-Type: text/plain; charset=utf-8');


$sql = "SELECT ";
$sql .= "DISTINCT(".constant('_DB_PREFIX_')."orders.id_order) AS reference, ";
$sql .= constant('_DB_PREFIX_')."orders.id_order AS id, ";
$sql .= constant('_DB_PREFIX_')."currency.iso_code AS currency, ";
$sql .= "DATE_FORMAT(".constant('_DB_PREFIX_')."orders.invoice_date, '%Y/%m/%d') AS start_date, ";
$sql .= "DATE_FORMAT(".constant('_DB_PREFIX_')."orders.delivery_date, '%Y/%m/%d') AS stop_date, ";
# Source and Destination
$sql .= "CONCAT('', IFNULL(";
$sql .= "CONCAT(".constant('_DB_PREFIX_')."customer.id_customer), ' Unknown unknown@person.com'";
$sql .= ")) AS destination, ";
# Source and Destination for the Ownership
$sql .= "CONCAT('', IFNULL(";
$sql .= "CONCAT(".constant('_DB_PREFIX_')."customer.id_customer), ' Unknown unknown@person.com'";
$sql .= ")) AS destination_ownership, ";
# Payment mode
$sql .= constant('_DB_PREFIX_')."orders.payment AS payment_mode ";

# Join's list
$sql .= "FROM ".constant('_DB_PREFIX_')."orders " ;

$sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."customer " ;
$sql .= "ON ".constant('_DB_PREFIX_')."customer.id_customer=".constant('_DB_PREFIX_')."orders.id_customer ";

$sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."currency " ;
$sql .= "ON ".constant('_DB_PREFIX_')."currency.id_currency=".constant('_DB_PREFIX_')."orders.id_currency ";

$sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."order_history " ;
$sql .= "ON ".constant('_DB_PREFIX_')."order_history.id_order=".constant('_DB_PREFIX_')."orders.id_order ";

$sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."order_detail " ;
$sql .= "ON ".constant('_DB_PREFIX_')."order_detail.id_order=".constant('_DB_PREFIX_')."orders.id_order ";

$sql .= "WHERE ";

if (isset($_POST['sale_order_id'])){
  $sql .= constant('_DB_PREFIX_')."orders.id_order=".$_POST['sale_order_id']." AND ";
}

$sql .= constant('_DB_PREFIX_')."order_history.id_order_history=";
$sql .= "(SELECT MAX(id_order_history) FROM ".constant('_DB_PREFIX_')."order_history WHERE id_order=".constant('_DB_PREFIX_')."orders.id_order) AND ";
$sql .= constant('_DB_PREFIX_')."order_history.id_order_state IN (4, 5, 6, 7) ";

$sql .= "ORDER BY ".constant('_DB_PREFIX_')."orders.id_order ASC ";


echo executeSQL($sql);
?>
