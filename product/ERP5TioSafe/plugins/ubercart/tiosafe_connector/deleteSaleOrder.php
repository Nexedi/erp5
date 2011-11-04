<?php
include('database.php');


header('Content-Type: text/plain; charset=utf-8');

$sql .= "DELETE FROM uc_orders ";
if (isset($_POST['id'])) {
    $sql .= "WHERE order_id=".$_POST['id']."; ";
}

$req = mysql_query($sql);
if (!$req) {
    die('\nInvalid query: ' . mysql_error());
}

$sql = "DELETE FROM uc_order_products ";
if (isset($_POST['id'])) {
    $sql .= "WHERE order_id=".$_POST['id']." ";
}

$req = mysql_query($sql);
if (!$req) {
    die('\nInvalid query: ' . mysql_error());
}
mysql_close();
?>
