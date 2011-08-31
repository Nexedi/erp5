<?php
include('database.php');
$reference = "";
$purchase_price = 0.0;
$sale_price = 0.0;
$title = "";

if (isset($_POST['reference'])) {
    $reference = $_POST['reference'];
}
if (isset($_POST['purchase_price'])) {
    $purchase_price = $_POST['purchase_price'];
}
if (isset($_POST['sale_price'])) {
    $sale_price = $_POST['sale_price'];
}
if (isset($_POST['title'])) {
    $title = $_POST['title'];
}
$req = mysql_query("SELECT max(vid)+1 AS last_id from uc_products") or die(mysql_error());
$res = mysql_fetch_array($req);
$last_id = $res["last_id"];
if ($last_id == 0) {
  $last_id = 1;
}

$product_sql = sprintf("INSERT INTO uc_products (vid, nid, model, cost, sell_price) VALUES (%d, %d, '%s', %f, %f)", 
	GetSQLValueString($last_id,"int"), 
	GetSQLValueString($last_id,"int"), 
	GetSQLValueString($reference,"text"), 
	GetSQLValueString($purchase_price,"float"), 
	GetSQLValueString($sale_price,"float")); 
$node_sql = sprintf("INSERT INTO node (vid, nid, type, language, title, uid, created, changed) VALUES (%d, %d, '%s', '%s', '%s', %d, %d, %d)", 
	GetSQLValueString($last_id,"int"), 
	GetSQLValueString($last_id,"int"), 
	GetSQLValueString('product',"text"), 
	GetSQLValueString('en',"text"), 
	GetSQLValueString($title,"text"), 
	GetSQLValueString(1,"int"),
	GetSQLValueString(time(),"int"), 
	GetSQLValueString(time(),"int"));
$node_comment_statistics = sprintf("INSERT INTO node_comment_statistics (nid, last_comment_timestamp, last_comment_uid) VALUES (%d, %d, %d)", 
	GetSQLValueString($last_id,"int"), 
	GetSQLValueString(time(),"int"), 
	GetSQLValueString(1,"int"));
$node_revisions = sprintf("INSERT INTO node_revisions (nid, vid, uid, title, timestamp) VALUES (%d, %d, %d, '%s', %d)", 
	GetSQLValueString($last_id,"int"), 
	GetSQLValueString($last_id,"int"), 
	GetSQLValueString(1,"int"),
	GetSQLValueString($title,"text"), 
	GetSQLValueString(time(),"int"));
$content_type_product = sprintf("INSERT INTO content_type_product (nid, vid) VALUES (%d, %d)", 
	GetSQLValueString($last_id,"int"), 
	GetSQLValueString($last_id,"int"));

mysql_query($product_sql) or die(mysql_error());
mysql_query($node_sql) or die(mysql_error());
mysql_query($node_comment_statistics) or die(mysql_error());
mysql_query($node_revisions) or die(mysql_error());
mysql_query($content_type_product) or die(mysql_error());
echo  $last_id;
return $last_id;

?>