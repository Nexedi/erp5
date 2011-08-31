<?php
include('database.php');
header('Content-Type: text/plain; charset=utf-8');
$sql .= "SELECT DISTINCT order_id as id,country_name as country, billing_company,billing_postal_code as billing_zip, ";
$sql .= "billing_phone, primary_email, billing_street1, billing_city ";
$sql .= "FROM uc_orders uco ";
$sql .= "LEFT OUTER JOIN uc_countries ucc ON ucc.country_id = uco.billing_country ";
$sql .= "WHERE 1=1 ";
if (isset($_POST['email'])) {
    $sql .= " AND primary_email='".$_POST['email']."' ";
}
if (isset($_POST['title'])) {
    $sql .= " AND billing_company='".$_POST['title']."' ";
}
if (isset($_POST['id'])) {
    $sql .= " AND order_id='".$_POST['id']."' ";
}
if (isset($_POST['organisation_id'])) {
    $sql .= " AND order_id='".$_POST['organisation_id']."' ";
}
$sql .= " ORDER BY billing_company, primary_email ";

echo executeSQL($sql);
?>
