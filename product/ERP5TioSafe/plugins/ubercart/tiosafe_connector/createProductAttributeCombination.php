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
    if (($rows == 0) and ($vname != "")){
	$vocabulary_sql = sprintf("INSERT INTO vocabulary (name, module, multiple) VALUES ('%s','%s',%d)", 
		GetSQLValueString($vname,"text"),      
		GetSQLValueString('uc_catalog',"text"),      
		GetSQLValueString(1,"int"));      
        mysql_query($vocabulary_sql) or die(mysql_error());
        $vid = mysql_insert_id(); 
	$vocabulary_nt_sql = sprintf("INSERT INTO vocabulary_node_types (vid, type) VALUES (%d,'%s')", 
		GetSQLValueString($vid,"int"),      
		GetSQLValueString('product',"text"));      
        mysql_query($vocabulary_nt_sql) or die(mysql_error());
        echo $vocabulary_nt_sql."\n";
	$vocabulary_nt2_sql = sprintf("INSERT INTO vocabulary_node_types (vid, type) VALUES (%d,'%s')", 
		GetSQLValueString($vid,"int"),      
		GetSQLValueString('product_kit',"text"));      
        mysql_query($vocabulary_nt2_sql) or die(mysql_error());
        echo $vocabulary_nt2_sql."\n";
    }else if ($rows != 0){
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
      if (($td_rows == 0) and ($tdname != "")){
	  $term_data_sql = sprintf("INSERT INTO term_data (vid, name) VALUES (%d, '%s')", 
		  GetSQLValueString($vid,"int"), 
		  GetSQLValueString($tdname,"text"));      
	  mysql_query($term_data_sql) or die(mysql_error());
	  echo $term_data_sql."\n";    
	  $tid = mysql_insert_id(); 
	  $term_hierarchy_sql = sprintf("INSERT INTO term_hierarchy (tid, parent) VALUES (%d, %d)", 
		  GetSQLValueString($tid,"int"),      
		  GetSQLValueString($parent_id,"int"));      
	  mysql_query($term_hierarchy_sql) or die(mysql_error());
          echo "\n".$term_hierarchy_sql."\n";
      }else if ($td_rows != 0){
	  $result2 = mysql_fetch_array($req_exist_td);
	  $tid = $result2["tid"];
      }  
      if ((isset($vid)) and (isset($tid)) and ($product_id!="") and ($i==(count($category_list)-1))){
          echo "mayoro diagne ".$product_id;
	  $term_node_sql = sprintf("INSERT INTO term_node (vid, nid, tid) VALUES (%s, %s, %d)", 
		  GetSQLValueString($product_id,"text"), 
		  GetSQLValueString($product_id,"text"), 
		  GetSQLValueString($tid,"int"));    
          echo "\n".$term_node_sql."\n";  
	  mysql_query($term_node_sql) or die(mysql_error()); 
      }
    $i++;
    }
  }
}
?>