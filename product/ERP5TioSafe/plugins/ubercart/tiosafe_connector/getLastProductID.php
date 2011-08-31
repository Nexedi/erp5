<?php
include('database.php');
header('Content-Type: text/plain; charset=utf-8');

$sql = "SELECT max(ucp.nid) AS id ";
$sql .= "FROM uc_products ucp " ;
$req = mysql_query($sql);
if ($req){
  $res = mysql_fetch_array($req);
  echo "<xml><object><id>".$res["id"]."</id></object></xml>";
  return;
}
echo "<xml><object><id>-1</id></object></xml>";
return;

?>