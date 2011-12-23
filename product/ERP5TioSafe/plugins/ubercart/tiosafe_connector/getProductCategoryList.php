<?php
include('database.php');
header('Content-Type: text/plain; charset=utf-8');
if (isset($_POST['id'])){
  $product_id = $_POST['id'];
}
if (isset($_POST['product_id'])){
  $product_id = $_POST['product_id'];
}
if (isset($_POST['group_id'])){
  $product_id = $_POST['group_id'];
}
$category_list = getProductCategory($product_id);
$sql = "";
for($i=0; $i<count($category_list); $i++){
  $categories = split("/",$category_list[$i]);
  $name = $categories[count($categories)-1];
  $sql .= "SELECT '".$category_list[$i]."' as category , tn.tid as distinction "; // 
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
?>