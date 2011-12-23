<?php
include('database.php');

if (isset($_POST['product_id'])) {
    $product_id = $_POST['product_id'];
}
if (isset($_POST['id_product'])) {
    $product_id = $_POST['id_product'];
}
if (isset($_POST['base_category'])) {
    $base_category = $_POST['base_category'];
}
if (isset($_POST['variation'])) {
    $variation = $_POST['variation'];
}

if (isset($product_id) && isset($base_category) && isset($variation)){
  if ($base_category != ""){
    $cat_list = split('"',$variation);
    print_r($cat_list);
    echo "pr id = ".$product_id."\n";
    $category_list = split('/',$cat_list[0]);
    $vname = $base_category;
    echo "variation".$variation."\n";
    print_r($category_list);
    $req_exist = mysql_query("SELECT * from vocabulary where name='$vname'") or die(mysql_error());
    $rows = mysql_num_rows($req_exist);
    if ($rows != 0){
        $result = mysql_fetch_array($req_exist);
        $vid = $result["vid"];  
    }   
    $i=0;
    while($i<count($category_list)){
      $tdname = $category_list[$i];
      if ($i==0){
        $parent_id = 0;
      }else{
        $parent_id = $tid;
      }
      echo $product_id."\n";
      $req_exist_td = mysql_query("SELECT * from term_data where name='$tdname'") or die(mysql_error());
      $td_rows = mysql_num_rows($req_exist_td);
      if ($td_rows != 0){
	  $result2 = mysql_fetch_array($req_exist_td);
	  $tid = $result2["tid"];
      }  
      if ((isset($vid)) and (isset($tid)) and ($product_id!="") and ($i==(count($category_list)-1))){
          echo "mayoro diagne ".$product_id;
	  $term_node_sql = "delete from term_node where nid='$product_id' and tid='$tid'";    
          echo "\n".$term_node_sql."\n";  
	  mysql_query($term_node_sql) or die(mysql_error()); 
      }
    $i++;
    }
  }
}
?>