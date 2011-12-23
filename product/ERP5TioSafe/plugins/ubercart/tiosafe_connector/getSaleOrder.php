<?php
include('database.php');
header('Content-Type: text/plain; charset=utf-8');
$currency = getDefaultSiteCurency(); 
$sql = "SELECT o.order_id AS id, o.created as start_date, $currency as currency, ";
$sql .= "billing_first_name, billing_last_name, billing_company, delivery_first_name, ";
$sql .= "delivery_last_name, delivery_company, payment_method, primary_email, ";
$sql .= "oli.title as delivery_title, oli.amount as delivery_price,0.00 as delivery_tax_rate, ";
$sql .= "cpo.code as discount_code, cp.name as discount_title, cpo.value as discount_price,0.00 as discount_tax_rate, ";
$sql .= "ucc.country_name as billing_country,  uccd.country_name as delivery_country ";
$sql .= "FROM uc_orders o " ;
$sql .= "LEFT OUTER JOIN uc_order_line_items oli ON o.order_id=oli.order_id AND oli.type='shipping' " ;
$sql .= "LEFT OUTER JOIN uc_coupons_orders cpo ON o.order_id=cpo.oid " ;
$sql .= "LEFT OUTER JOIN uc_coupons cp ON cp.cid=cpo.cid " ;
$sql .= "LEFT OUTER JOIN uc_countries ucc ON ucc.country_id = o.billing_country ";
$sql .= "LEFT OUTER JOIN uc_countries uccd ON uccd.country_id = o.delivery_country ";
$sql .= "WHERE 1=1 ";
if (isset($_POST['sale_order_id'])) {
    $sql .= "AND o.order_id='".$_POST['sale_order_id']."' ";
}
if (isset($_POST['id'])) {
    $sql .= "AND o.order_id='".$_POST['id']."' ";
}
$sql .= "ORDER BY o.order_id ASC";
#$sql .= "ORDER BY start_date ASC";
echo executeSQL($sql);
?>

  