<?php
include('database.php');
header('Content-Type: text/plain; charset=utf-8');
$sql .= "SELECT DISTINCT order_id as id, delivery_first_name AS firstname, "; 
$sql .= "delivery_last_name AS lastname, primary_email AS email, ";
$sql .= "delivery_street1 as street, delivery_postal_code as zip,  delivery_city as city, country_name as country, ";
$sql .= "order_id AS company, delivery_company as company_id, ";
$sql .= "'type/Person' AS category ";
$sql .= "FROM uc_orders uco ";
$sql .= "LEFT OUTER JOIN uc_countries ucc ON ucc.country_id = uco.billing_country ";
$sql .= "WHERE delivery_first_name<>billing_first_name and delivery_last_name<>billing_last_name  AND concat(delivery_first_name,delivery_last_name)<>''";
if (isset($_POST['firstname'])) {
    $sql .= " AND delivery_first_name=".$_POST['firstname']." ";
}
if (isset($_POST['lastname'])) {
    $sql .= " AND delivery_last_name=".$_POST['lastname']." ";
}
if (isset($_POST['email'])) {
    $sql .= " AND primary_email='".$_POST['email']."' ";
}
if (isset($_POST['id'])) {
    $sql .= " AND order_id='".$_POST['id']."' ";
}
if (isset($_POST['person_id'])) {
    $sql .= " AND order_id='".$_POST['person_id']."' ";
}

echo executeSQL($sql);
?>
