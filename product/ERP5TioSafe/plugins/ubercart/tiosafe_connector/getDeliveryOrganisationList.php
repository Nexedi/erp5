<?php
include('database.php');
header('Content-Type: text/plain; charset=utf-8');
$sql .= "SELECT DISTINCT order_id as id, country_name as country, delivery_company, delivery_postal_code as delivery_zip, ";
$sql .= "delivery_phone, primary_email, delivery_street1, delivery_city ";
$sql .= "FROM uc_orders uco ";
$sql .= "LEFT OUTER JOIN uc_countries ucc ON ucc.country_id = uco.delivery_country ";
$sql .= "WHERE delivery_company <> billing_company ";
if (isset($_POST['email'])) {
    $sql .= " AND primary_email='".$_POST['email']."' ";
}
if (isset($_POST['title'])) {
    $sql .= " AND delivery_company='".$_POST['title']."' ";
}
if (isset($_POST['id'])) {
    $sql .= " AND order_id='".$_POST['id']."' ";
}
if (isset($_POST['organisation_id'])) {
    $sql .= " AND order_id='".$_POST['organisation_id']."' ";
}
$sql .= " ORDER BY delivery_company, primary_email ";
echo executeSQL($sql);
?>
