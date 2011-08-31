<?php
include('database.php');
header('Content-Type: text/plain; charset=utf-8');
if (isset($_POST['firstname']) or isset($_POST['lastname']) or isset($_POST['email']))
{
  $sql .= "SELECT DISTINCT order_id as id, billing_first_name AS firstname, "; 
  $sql .= "billing_last_name AS lastname, primary_email AS email, ";
  $sql .= "CONCAT(billing_first_name, ' ', billing_last_name) AS title, ";
  $sql .= "'type/person' AS category ";
  $sql .= "FROM uc_orders ";
  $sql .= "WHERE 1=1";
  if (isset($_POST['firstname'])) {
      $sql .= " AND billing_first_name='".$_POST['firstname']."' ";
  }
  if (isset($_POST['lastname'])) {
      $sql .= " AND billing_last_name='".$_POST['lastname']."' ";
  }
  if (isset($_POST['email'])) {
      $sql .= " AND primary_email='".$_POST['email']."' ";
  }

  $req = mysql_query($sql);
  if ($req){
    $res = mysql_fetch_array($req);
    echo "<xml><object><id>".$res["id"]."</id></object></xml>";
    return;
  }
}else if (isset($_POST['reference']) and isset($_POST['title']) ) {
  $sql = "SELECT ucp.nid AS id,ucp.model as reference, ucp.sell_price AS sale_price, ucp.cost AS purchase_price, ";
  $sql .= "n.title as title, n.status as state ";
  $sql .= "FROM uc_products ucp " ;
  $sql .= "LEFT OUTER JOIN node n ON n.nid = ucp.nid ";
  $sql .= " WHERE 1=1 ";
  if (isset($_POST['reference'])) {
      $sql .= " AND ucp.model='".$_POST['reference']."' ";
  }
  if (isset($_POST['title'])) {
      $sql .= " AND n.title='".$_POST['title']."' ";
  }
  $req = mysql_query($sql);
  if ($req){
    $res = mysql_fetch_array($req);
    echo "<xml><object><id>".$res["id"]."</id></object></xml>";
    return;
  }
} else {
  echo "<xml><object><id>-1</id></object></xml>";
  return;
}

?>