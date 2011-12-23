<?php
include('database.php');
header('Content-Type: text/plain; charset=utf-8');
if (isset($_POST['sale_order_id'])){
  $sale_order_id = $_POST['sale_order_id'];
}
if (isset($_POST['sale_order_line_id'])){
  $sale_order_line_id = $_POST['sale_order_line_id'];
  $req = mysql_query("SELECT * FROM uc_order_products WHERE order_product_id=$sale_order_line_id ") or die(mysql_error());
  if (mysql_num_rows($req)>0){
    $res = mysql_fetch_array($req);
    $product_id = $res["nid"];
    $category_list = getProductCategory($product_id);
    $sql = "";
    for($i=0; $i<count($category_list); $i++){
      $categories = split("/",$category_list[$i]);
      $name = $categories[count($categories)-1];
      $sql .= "SELECT '".$category_list[$i]."' as category , tn.tid as distinction "; 
      $sql .= "FROM term_node tn " ;
      $sql .= "LEFT OUTER JOIN term_data td ON tn.tid = td.tid ";
      $sql .= " where td.name='$name' ";
      if (isset($product_id)) {
	  $sql .= " AND nid=".$product_id." ";
      }
      if ($i < (count($category_list)-1)){
	$sql .= " UNION ";
      }
    }
    if (!empty($sql)){
      echo executeSQL($sql);
    }
  }
}
?>