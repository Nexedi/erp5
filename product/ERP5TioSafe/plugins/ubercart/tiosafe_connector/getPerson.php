<?php
include('database.php');
header('Content-Type: text/plain; charset=utf-8');
$sql .= "SELECT DISTINCT order_id as id, billing_first_name AS firstname, "; 
$sql .= "billing_last_name AS lastname, primary_email AS email, ";
$sql .= "billing_street1 as street, billing_postal_code as zip,  billing_city as city, country_name as country, ";
$sql .= "order_id AS company, billing_company as company_id, ";
$sql .= "'type/Person' AS category ";
$sql .= "FROM uc_orders uco ";
$sql .= "LEFT OUTER JOIN uc_countries ucc ON ucc.country_id = uco.billing_country ";
$sql .= "WHERE 1=1 AND concat(billing_first_name,billing_last_name)<>'' ";

if (isset($_POST['firstname'])) {
    $sql .= " AND billing_first_name=".$_POST['firstname']." ";
}
if (isset($_POST['lastname'])) {
    $sql .= " AND billing_last_name=".$_POST['lastname']." ";
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
